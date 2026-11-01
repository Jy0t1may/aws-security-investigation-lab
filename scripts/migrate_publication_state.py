import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from publish_findings import ROOT, command, save

def main():
    os.umask(0o077)
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: python3 scripts/migrate_publication_state.py "
            "LOCAL_RUN_DIRECTORY CLOUD_RUN_DIRECTORY"
        )

    local_run = Path(sys.argv[1]).resolve()
    cloud_run = Path(sys.argv[2]).resolve()

    invocation = json.loads((cloud_run / "invocation.json").read_text())
    response = json.loads((cloud_run / "response.json").read_text())

    if invocation.get("FunctionError"):
        raise RuntimeError("Source cloud invocation contains FunctionError.")
    if (
        response.get("mode") != "EVALUATION_ONLY"
        or response.get("query_state") != "SUCCEEDED"
    ):
        raise RuntimeError("Expected a successful evaluation-only cloud run.")

    database = ROOT / "evidence/private/notification-state/publications.sqlite3"
    table = command([
        "terraform", f"-chdir={ROOT / 'infrastructure'}",
        "output", "-raw", "detection_publications_table_name",
    ])

    migration = cloud_run / "publication-migration"
    migration.mkdir(exist_ok=True)

    plans = []
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as db:
        for finding in response["findings"]:
            event_id = finding["event_id"]
            finding_id = hashlib.sha256(
                f"AWSLAB-DET-001:{event_id}".encode()
            ).hexdigest()

            if finding_id != finding["finding_id"]:
                raise RuntimeError("Finding ID does not match its event ID.")

            row = db.execute(
                "SELECT status, sns_message_id FROM publications "
                "WHERE finding_id = ?",
                (finding_id,),
            ).fetchone()

            if not row or row[0] != "PUBLISHED" or not row[1]:
                raise RuntimeError(
                    "No completed local publication for this cloud finding."
                )

            notifications = local_run / "notifications"
            payload = json.loads(
                (notifications / f"{finding_id}-payload.json").read_text()
            )
            published = json.loads(
                (notifications / f"{finding_id}-publish.json").read_text()
            )

            if (
                payload.get("finding_id") != finding_id
                or payload.get("event_id") != event_id
                or payload.get("rule_id") != "AWSLAB-DET-001"
                or published.get("MessageId") != row[1]
            ):
                raise RuntimeError("Local publication evidence does not match.")

            record = {
                "finding_id": finding_id,
                "status": "PUBLISHED",
                "rule_id": "AWSLAB-DET-001",
                "event_id": event_id,
                "sns_message_id": row[1],
                "origin": "LOCAL_LEDGER_MIGRATION",
                "migrated_at": datetime.now(timezone.utc).isoformat(),
                "source_query_id": payload["athena_query_id"],
            }
            plans.append(record)

    if not plans:
        raise RuntimeError("No publication records available to migrate.")

    migrated = 0
    for record in plans:
        finding_id = record["finding_id"]
        item = {key: {"S": value} for key, value in record.items()}
        request_file = migration / f"{finding_id}-item.json"
        save(request_file, item)

        result = command([
            "aws", "dynamodb", "put-item",
            "--table-name", table,
            "--item", f"file://{request_file}",
            "--condition-expression", "attribute_not_exists(finding_id)",
            "--profile", "investigation-lab",
            "--region", "eu-north-1",
            "--output", "json",
            "--no-cli-pager",
        ])
        save(
            migration / f"{finding_id}-write-response.json",
            json.loads(result or "{}"),
        )
        migrated += 1

    save(migration / "summary.json", {
        "records_migrated": migrated,
        "notifications_published": 0,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    })
    print(f"Publication records migrated: {migrated}")
    print("Notifications published: 0")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
