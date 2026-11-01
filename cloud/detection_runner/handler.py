import hashlib
import json
import os
import time
from pathlib import Path

import boto3
from publication import publish_finding

athena = boto3.client("athena")
ledger = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])

def handler(event, context):
    sql = Path(__file__).with_name("detection.sql").read_text()
    identity = boto3.client("sts").get_caller_identity()
    publishing = os.environ.get("PUBLISH_ENABLED", "false") == "true"

    if publishing:
        migration_id = hashlib.sha256(
            ("AWSLAB-DET-001:" + os.environ["MIGRATION_EVENT_ID"]).encode()
        ).hexdigest()
        migrated = ledger.get_item(
            Key={"finding_id": migration_id},
            ConsistentRead=True,
        ).get("Item", {})
        if (
            migrated.get("status") != "PUBLISHED"
            or not migrated.get("sns_message_id")
        ):
            raise RuntimeError(
                "Publication blocked: prior finding migration is incomplete."
            )

    started = athena.start_query_execution(
        QueryString=sql,
        ClientRequestToken=context.aws_request_id,
        QueryExecutionContext={
            "Database": os.environ["DATABASE"],
            "Catalog": "AwsDataCatalog",
        },
        WorkGroup=os.environ["WORKGROUP"],
        ResultReuseConfiguration={
            "ResultReuseByAgeConfiguration": {"Enabled": False}
        },
    )
    query_id = started["QueryExecutionId"]
    print(json.dumps({
        "stage": "query_started",
        "query_id": query_id,
        "request_id": context.aws_request_id,
    }))

    deadline = time.monotonic() + 180
    while True:
        execution = athena.get_query_execution(
            QueryExecutionId=query_id
        )["QueryExecution"]
        state = execution["Status"]["State"]

        if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
            break

        if (
            time.monotonic() >= deadline
            or context.get_remaining_time_in_millis() < 30000
        ):
            athena.stop_query_execution(QueryExecutionId=query_id)
            raise RuntimeError(
                f"Query deadline exceeded; cancellation requested: {query_id}"
            )
        time.sleep(3)

    if state != "SUCCEEDED":
        reason = execution["Status"].get("StateChangeReason", "")
        raise RuntimeError(f"Query {query_id}: {state}: {reason}")

    columns = None
    first_row = True
    findings = []
    paginator = athena.get_paginator("get_query_results")

    for page in paginator.paginate(QueryExecutionId=query_id):
        result = page["ResultSet"]
        if columns is None:
            columns = [
                column["Name"]
                for column in result["ResultSetMetadata"]["ColumnInfo"]
            ]

        for row in result.get("Rows", []):
            values = [
                cell.get("VarCharValue", "") for cell in row["Data"]
            ]
            if first_row:
                first_row = False
                if values != columns:
                    raise RuntimeError("Unexpected SELECT result header.")
                continue

            record = dict(zip(columns, values))
            finding_id = hashlib.sha256(
                f"AWSLAB-DET-001:{record['eventid']}".encode()
            ).hexdigest()

            item = ledger.get_item(
                Key={"finding_id": finding_id},
                ConsistentRead=True,
            ).get("Item")

            publication_result = "EVALUATION_ONLY"
            if publishing:
                if context.get_remaining_time_in_millis() < 45000:
                    raise RuntimeError(
                        "Insufficient time to safely attempt publication."
                    )
                publication_result = publish_finding(
                    ledger,
                    os.environ["TOPIC_ARN"],
                    record,
                    query_id,
                    context.aws_request_id,
                )
                item = {"status": "PUBLISHED"}

            findings.append({
                "publication_result": publication_result,
                "finding_id": finding_id,
                "event_id": record["eventid"],
                "event_time": record["eventtime"],
                "event_name": record["eventname"],
                "error_code": record["errorcode"],
                "publication_state": (
                    item.get("status", "UNKNOWN") if item else "UNRECORDED"
                ),
            })

    summary = {
        "trigger_context": {
            "trigger": event.get("trigger", "MANUAL"),
            "schedule_arn": event.get("schedule_arn"),
            "scheduled_time": event.get("scheduled_time"),
            "scheduler_execution_id": event.get("scheduler_execution_id"),
        },
        "mode": "CLOUD_PUBLISHING" if publishing else "EVALUATION_ONLY",
        "query_state": state,
        "query_id": query_id,
        "request_id": context.aws_request_id,
        "execution_identity": identity["Arn"],
        "sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
        "bytes_scanned": execution.get("Statistics", {}).get(
            "DataScannedInBytes"
        ),
        "finding_count": len(findings),
        "notifications_published": sum(
            f["publication_result"] == "PUBLISHED_NOW" for f in findings
        ),
        "notifications_skipped": sum(
            f["publication_result"] == "SKIPPED_PUBLISHED" for f in findings
        ),
        "findings": findings,
    }
    print(json.dumps(summary))
    return summary
