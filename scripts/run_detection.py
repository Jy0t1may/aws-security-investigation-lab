import csv
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SQL_FILE = ROOT / "queries/detections/AWSLAB-DET-001-windowed.sql"
PROFILE = "investigation-lab"
REGION = "eu-north-1"
WORKGROUP = "awslab-investigation"

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def aws(*arguments):
    command = [
        "aws", "athena", *arguments,
        "--profile", PROFILE,
        "--region", REGION,
        "--output", "json",
        "--no-cli-pager",
    ]
    result = subprocess.run(
        command, capture_output=True, text=True, timeout=90
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "AWS CLI failed.")
    return json.loads(result.stdout)

def save_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

def main():
    os.umask(0o077)
    sql = SQL_FILE.read_text()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run = ROOT / "evidence/private/detection-runs" / (
        stamp + "-" + uuid.uuid4().hex[:8]
    )
    run.mkdir(parents=True)

    manifest = {
        "rule_id": "AWSLAB-DET-001",
        "started_at": utc_now(),
        "profile": PROFILE,
        "region": REGION,
        "workgroup": WORKGROUP,
        "sql_sha256": hashlib.sha256(sql.encode()).hexdigest(),
        "status": "STARTING",
    }
    (run / "query.sql").write_text(sql)
    save_json(run / "manifest.json", manifest)

    try:
        started = aws(
            "start-query-execution",
            "--query-string", sql,
            "--work-group", WORKGROUP,
            "--query-execution-context",
            "Database=awslab_investigation,Catalog=AwsDataCatalog",
            "--client-request-token", str(uuid.uuid4()),
            "--result-reuse-configuration",
            '{"ResultReuseByAgeConfiguration":{"Enabled":false}}',
        )
        query_id = started["QueryExecutionId"]
        manifest.update(query_id=query_id, status="RUNNING")
        save_json(run / "manifest.json", manifest)

        deadline = time.monotonic() + 240
        while True:
            execution = aws(
                "get-query-execution",
                "--query-execution-id", query_id,
            )
            save_json(run / "execution.json", execution)
            state = execution["QueryExecution"]["Status"]["State"]

            if state in {"SUCCEEDED", "FAILED", "CANCELLED"}:
                break

            if time.monotonic() >= deadline:
                aws("stop-query-execution", "--query-execution-id", query_id)
                raise RuntimeError(
                    "Polling deadline exceeded; query cancellation requested."
                )
            time.sleep(5)

        if state != "SUCCEEDED":
            reason = execution["QueryExecution"]["Status"].get(
                "StateChangeReason", "No reason supplied."
            )
            raise RuntimeError(f"Query {state}: {reason}")

        results = aws(
            "get-query-results",
            "--query-execution-id", query_id,
        )
        save_json(run / "results.json", results)

        result_set = results["ResultSet"]
        columns = [
            column["Name"]
            for column in result_set["ResultSetMetadata"]["ColumnInfo"]
        ]
        rows = [
            [cell.get("VarCharValue", "") for cell in row["Data"]]
            for row in result_set.get("Rows", [])
        ]

        if not rows or rows[0] != columns:
            raise RuntimeError("Unexpected SELECT result header.")
        findings = [
            dict(zip(columns, row))
            for row in rows[1:]
        ]

        with (run / "findings.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(findings)

        statistics = execution["QueryExecution"].get("Statistics", {})
        manifest.update(
            status="SUCCEEDED",
            finished_at=utc_now(),
            finding_count=len(findings),
            bytes_scanned=statistics.get("DataScannedInBytes"),
        )
        save_json(run / "manifest.json", manifest)

        print("Query state: SUCCEEDED")
        print(f"Finding count: {len(findings)}")
        print(f"Bytes scanned: {manifest['bytes_scanned']}")
        print(f"Evidence: {run.relative_to(ROOT)}")
        return 0

    except Exception as error:
        manifest.update(
            status="ERROR",
            finished_at=utc_now(),
            error=str(error),
        )
        save_json(run / "manifest.json", manifest)
        print(f"STOP: {error}", file=sys.stderr)
        print(f"Evidence: {run.relative_to(ROOT)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
