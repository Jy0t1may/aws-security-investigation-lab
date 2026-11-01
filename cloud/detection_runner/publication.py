import hashlib
import json
from datetime import datetime, timezone

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

sns = boto3.client(
    "sns",
    config=Config(
        retries={"mode": "standard", "total_max_attempts": 1},
        connect_timeout=5,
        read_timeout=20,
    ),
)

def now():
    return datetime.now(timezone.utc).isoformat()

def publish_finding(table, topic, record, query_id, request_id):
    finding_id = hashlib.sha256(
        f"AWSLAB-DET-001:{record['eventid']}".encode()
    ).hexdigest()

    try:
        table.put_item(
            Item={
                "finding_id": finding_id,
                "status": "PENDING",
                "rule_id": "AWSLAB-DET-001",
                "event_id": record["eventid"],
                "owner_request_id": request_id,
                "created_at": now(),
            },
            ConditionExpression="attribute_not_exists(finding_id)",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] != "ConditionalCheckFailedException":
            raise

        existing = table.get_item(
            Key={"finding_id": finding_id},
            ConsistentRead=True,
        ).get("Item", {})

        if (
            existing.get("status") == "PUBLISHED"
            and existing.get("sns_message_id")
        ):
            return "SKIPPED_PUBLISHED"

        raise RuntimeError(
            f"Unresolved publication requires investigation: {finding_id}"
        )

    payload = {
        "schema_version": "1",
        "finding_id": finding_id,
        "rule_id": "AWSLAB-DET-001",
        "classification": "lab_authorization_failure",
        "context": "Controlled lab detection; not a confirmed incident.",
        "event_id": record["eventid"],
        "event_time": record["eventtime"],
        "event_name": record["eventname"],
        "region": record["awsregion"],
        "role_name": record["role_name"],
        "bucket_name": record["bucket_name"],
        "error_code": record["errorcode"],
        "athena_query_id": query_id,
        "created_at": now(),
    }

    response = sns.publish(
        TopicArn=topic,
        Subject="AWSLAB-DET-001: lab authorization failure",
        Message=json.dumps(payload),
    )
    message_id = response["MessageId"]

    print(json.dumps({
        "stage": "sns_accepted",
        "finding_id": finding_id,
        "sns_message_id": message_id,
        "request_id": request_id,
    }))

    table.update_item(
        Key={"finding_id": finding_id},
        UpdateExpression=(
            "SET #status = :published, sns_message_id = :message, "
            "updated_at = :updated"
        ),
        ConditionExpression=(
            "#status = :pending AND owner_request_id = :owner"
        ),
        ExpressionAttributeNames={"#status": "status"},
        ExpressionAttributeValues={
            ":published": "PUBLISHED",
            ":pending": "PENDING",
            ":message": message_id,
            ":updated": now(),
            ":owner": request_id,
        },
    )
    return "PUBLISHED_NOW"
