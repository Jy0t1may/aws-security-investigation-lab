import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from publish_findings import ROOT, command, save

def sqs(*arguments):
    return json.loads(command([
        "aws", "sqs", *arguments,
        "--profile", "investigation-lab",
        "--region", "eu-north-1",
        "--output", "json",
        "--no-cli-pager",
    ]) or "{}")

def main():
    os.umask(0o077)
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/ack_notifications.py RUN_DIRECTORY")

    folder = Path(sys.argv[1]).resolve() / "notifications"
    publications = {}

    for path in folder.glob("*-publish.json"):
        finding_id = path.name.removesuffix("-publish.json")
        response = json.loads(path.read_text())
        publications[response["MessageId"]] = finding_id

    if not publications:
        raise SystemExit("STOP: no recorded SNS publications.")

    queue = command([
        "terraform", f"-chdir={ROOT / 'infrastructure'}",
        "output", "-raw", "detection_inbox_url",
    ])

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    received = sqs(
        "receive-message",
        "--queue-url", queue,
        "--max-number-of-messages", "10",
        "--wait-time-seconds", "20",
        "--visibility-timeout", "120",
    )
    save(folder / f"{stamp}-ack-receipt.json", received)

    entries = []
    for message in received.get("Messages", []):
        try:
            envelope = json.loads(message["Body"])
            payload = json.loads(envelope["Message"])
        except (KeyError, TypeError, ValueError):
            continue

        expected = publications.get(envelope.get("MessageId"))
        if expected and payload.get("finding_id") == expected:
            entries.append({
                "Id": str(len(entries)),
                "ReceiptHandle": message["ReceiptHandle"],
            })

    if not entries:
        print("No matching visible messages; nothing deleted.")
        return 2

    response = sqs(
        "delete-message-batch",
        "--queue-url", queue,
        "--entries", json.dumps(entries),
    )
    save(folder / f"{stamp}-ack-response.json", response)

    successful = len(response.get("Successful", []))
    failed = len(response.get("Failed", []))
    print(f"Matched messages: {len(entries)}")
    print(f"Acknowledgements accepted: {successful}")
    print(f"Failed acknowledgements: {failed}")

    return 0 if failed == 0 and successful == len(entries) else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
