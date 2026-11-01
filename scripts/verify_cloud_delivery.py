import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from publish_findings import ROOT, command, save

def aws(service, *arguments):
    return json.loads(command([
        "aws", service, *arguments,
        "--profile", "investigation-lab",
        "--region", "eu-north-1",
        "--output", "json",
        "--no-cli-pager",
    ]) or "{}")

def terraform_output(name):
    return command([
        "terraform", f"-chdir={ROOT / 'infrastructure'}",
        "output", "-raw", name,
    ])

def main():
    os.umask(0o077)
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 scripts/verify_cloud_delivery.py INVOCATION_DIRECTORY"
        )

    invocation_dir = Path(sys.argv[1]).resolve()
    invocation = json.loads(
        (invocation_dir / "invocation.json").read_text()
    )
    response = json.loads(
        (invocation_dir / "response.json").read_text()
    )

    if invocation.get("FunctionError"):
        raise RuntimeError("Source invocation contains FunctionError.")
    if (
        response.get("mode") != "CLOUD_PUBLISHING"
        or response.get("query_state") != "SUCCEEDED"
    ):
        raise RuntimeError("Expected a successful cloud-publishing run.")

    findings = [
        finding for finding in response.get("findings", [])
        if finding.get("publication_result") == "PUBLISHED_NOW"
    ]
    if not findings:
        raise RuntimeError(
            "No newly published findings in this invocation. "
            "Use the invocation directory that actually published the finding."
        )

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = invocation_dir / f"delivery-{stamp}"
    evidence.mkdir()

    table = terraform_output("detection_publications_table_name")
    topic = terraform_output("detection_topic_arn")
    queue = terraform_output("detection_inbox_url")

    expected = {}
    for finding in findings:
        result = aws(
            "dynamodb", "get-item",
            "--table-name", table,
            "--key", json.dumps({
                "finding_id": {"S": finding["finding_id"]}
            }),
            "--consistent-read",
        )
        save(evidence / f"{finding['finding_id']}-ledger.json", result)
        item = result.get("Item", {})

        if (
            item.get("status", {}).get("S") != "PUBLISHED"
            or item.get("event_id", {}).get("S") != finding["event_id"]
            or item.get("owner_request_id", {}).get("S")
                != response["request_id"]
        ):
            raise RuntimeError("Ledger does not match this publication.")

        message_id = item.get("sns_message_id", {}).get("S")
        if not message_id:
            raise RuntimeError("Published ledger record has no SNS message ID.")
        expected[message_id] = finding

    received = aws(
        "sqs", "receive-message",
        "--queue-url", queue,
        "--max-number-of-messages", "10",
        "--wait-time-seconds", "20",
        "--visibility-timeout", "120",
    )
    save(evidence / "sqs-receipt.json", received)

    matched_ids = set()
    entries = []
    for message in received.get("Messages", []):
        try:
            envelope = json.loads(message["Body"])
            payload = json.loads(envelope["Message"])
        except (KeyError, TypeError, ValueError):
            continue

        finding = expected.get(envelope.get("MessageId"))
        if not finding:
            continue

        if (
            envelope.get("TopicArn") == topic
            and payload.get("rule_id") == "AWSLAB-DET-001"
            and payload.get("finding_id") == finding["finding_id"]
            and payload.get("event_id") == finding["event_id"]
            and payload.get("athena_query_id") == response["query_id"]
        ):
            matched_ids.add(finding["finding_id"])
            entries.append({
                "Id": str(len(entries)),
                "ReceiptHandle": message["ReceiptHandle"],
            })

    summary = {
        "expected_findings": len(findings),
        "correlated_findings": len(matched_ids),
        "matching_message_copies": len(entries),
        "acknowledgements_accepted": 0,
        "acknowledgements_failed": 0,
    }

    if entries:
        deleted = aws(
            "sqs", "delete-message-batch",
            "--queue-url", queue,
            "--entries", json.dumps(entries),
        )
        save(evidence / "ack-response.json", deleted)
        summary["acknowledgements_accepted"] = len(
            deleted.get("Successful", [])
        )
        summary["acknowledgements_failed"] = len(
            deleted.get("Failed", [])
        )

    complete = (
        len(matched_ids) == len(findings)
        and summary["acknowledgements_accepted"] == len(entries)
        and summary["acknowledgements_failed"] == 0
    )
    summary["result"] = "PASS" if complete else "INCOMPLETE"
    save(evidence / "summary.json", summary)

    for name, value in summary.items():
        print(f"{name}: {value}")
    print(f"Evidence: {evidence.relative_to(ROOT)}")
    return 0 if complete else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
