import csv
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def now():
    return datetime.now(timezone.utc).isoformat()

def command(arguments, timeout=90):
    result = subprocess.run(
        arguments, capture_output=True, text=True, timeout=timeout
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Command failed.")
    return result.stdout.strip()

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")

def main():
    os.umask(0o077)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/publish_findings.py RUN_DIRECTORY")

    run = Path(sys.argv[1]).resolve()
    manifest = json.loads((run / "manifest.json").read_text())
    if manifest.get("status") != "SUCCEEDED":
        raise SystemExit("STOP: source detection run did not succeed.")

    with (run / "findings.csv").open(newline="") as handle:
        findings = list(csv.DictReader(handle))

    topic = command([
        "terraform", f"-chdir={ROOT / 'infrastructure'}",
        "output", "-raw", "detection_topic_arn",
    ])

    state_dir = ROOT / "evidence/private/notification-state"
    state_dir.mkdir(parents=True, exist_ok=True)
    output = run / "notifications"
    output.mkdir(exist_ok=True)

    published = skipped = 0

    with sqlite3.connect(state_dir / "publications.sqlite3") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS publications (
                finding_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                sns_message_id TEXT
            )
        """)
        db.commit()

        for event in findings:
            rule_id = manifest["rule_id"]
            event_id = event["eventid"]
            finding_id = hashlib.sha256(
                f"{rule_id}:{event_id}".encode()
            ).hexdigest()

            cursor = db.execute(
                "INSERT OR IGNORE INTO publications "
                "(finding_id, status, updated_at) VALUES (?, ?, ?)",
                (finding_id, "PENDING", now()),
            )
            db.commit()

            if cursor.rowcount == 0:
                status = db.execute(
                    "SELECT status FROM publications WHERE finding_id = ?",
                    (finding_id,),
                ).fetchone()[0]
                if status != "PUBLISHED":
                    raise RuntimeError(
                        "STOP: unresolved prior publication. "
                        "Inspect evidence before retrying."
                    )
                skipped += 1
                continue

            payload = {
                "schema_version": "1",
                "finding_id": finding_id,
                "rule_id": rule_id,
                "classification": "lab_authorization_failure",
                "context": "Controlled exercise; not a confirmed incident.",
                "event_id": event_id,
                "event_time": event["eventtime"],
                "event_name": event["eventname"],
                "region": event["awsregion"],
                "role_name": event["role_name"],
                "bucket_name": event["bucket_name"],
                "error_code": event["errorcode"],
                "athena_query_id": manifest["query_id"],
                "created_at": now(),
            }
            payload_file = output / f"{finding_id}-payload.json"
            save(payload_file, payload)

            response = json.loads(command([
                "aws", "sns", "publish",
                "--topic-arn", topic,
                "--subject", f"{rule_id}: lab authorization failure",
                "--message", f"file://{payload_file}",
                "--profile", "investigation-lab",
                "--region", "eu-north-1",
                "--output", "json",
                "--no-cli-pager",
            ]))
            save(output / f"{finding_id}-publish.json", response)

            db.execute(
                "UPDATE publications SET status = ?, updated_at = ?, "
                "sns_message_id = ? WHERE finding_id = ?",
                ("PUBLISHED", now(), response["MessageId"], finding_id),
            )
            db.commit()
            published += 1

    summary = {
        "finished_at": now(),
        "published": published,
        "skipped_previously_published": skipped,
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    save(output / f"{stamp}-summary.json", summary)
    print(f"Published: {published}")
    print(f"Skipped previously published: {skipped}")

if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
