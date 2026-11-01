import json
import os
import sys
from datetime import datetime, timedelta, timezone
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

def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

def main():
    os.umask(0o077)
    config = json.loads((
        ROOT / "infrastructure/schedule-validation.auto.tfvars.json"
    ).read_text())

    configured_time = config["detection_validation_time_utc"]
    target = parse_time(configured_time).replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    ready = target + timedelta(minutes=5)

    print(f"Scheduled UTC: {target.isoformat()}")
    if now < ready:
        print(f"Collect evidence after: {ready.isoformat()}")
        print("Not ready yet. Do not invoke or reschedule the function.")
        return 0

    stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
    evidence = ROOT / "evidence/private/scheduled-runs" / stamp
    evidence.mkdir(parents=True)

    schedule = aws(
        "scheduler", "get-schedule",
        "--name", "awslab-detection-validation",
        "--group-name", "awslab-detection",
    )
    save(evidence / "schedule.json", schedule)

    if schedule.get("ScheduleExpression") != f"at({configured_time})":
        raise RuntimeError("Deployed schedule differs from local configuration.")

    start = target - timedelta(minutes=2)
    end = min(now, target + timedelta(minutes=65))

    logs = aws(
        "logs", "filter-log-events",
        "--log-group-name", "/aws/lambda/awslab-detection-runner",
        "--start-time", str(int(start.timestamp() * 1000)),
        "--end-time", str(int(end.timestamp() * 1000)),
    )
    save(evidence / "cloudwatch-events.json", logs)

    decoder = json.JSONDecoder()
    summaries = {}

    for entry in logs.get("events", []):
        message = entry.get("message", "")
        position = message.find("{")
        if position < 0:
            continue
        try:
            record, _ = decoder.raw_decode(message[position:])
        except ValueError:
            continue
        if not isinstance(record, dict):
            continue

        context = record.get("trigger_context", {})
        if (
            context.get("trigger") == "SCHEDULED_VALIDATION"
            and context.get("schedule_arn") == schedule["Arn"]
            and record.get("request_id")
            and record.get("query_state")
        ):
            scheduled = context.get("scheduled_time")
            if scheduled and parse_time(scheduled) == target:
                summaries[record["request_id"]] = record

    save(evidence / "scheduled-summaries.json", list(summaries.values()))

    results = []
    for record in summaries.values():
        passed = (
            record.get("mode") == "CLOUD_PUBLISHING"
            and record.get("query_state") == "SUCCEEDED"
            and record.get("finding_count") == 1
            and record.get("notifications_published") == 0
            and record.get("notifications_skipped") == 1
        )
        results.append({
            "request_id": record["request_id"],
            "query_id": record.get("query_id"),
            "query_state": record.get("query_state"),
            "finding_count": record.get("finding_count"),
            "notifications_published": record.get("notifications_published"),
            "notifications_skipped": record.get("notifications_skipped"),
            "bytes_scanned": record.get("bytes_scanned"),
            "expected_scenario": "PASS" if passed else "REVIEW",
        })

    save(evidence / "verification.json", {
        "matching_completed_executions": len(results),
        "results": results,
    })

    print(f"Matching completed executions: {len(results)}")
    for result in results:
        for field in (
            "query_state",
            "finding_count",
            "notifications_published",
            "notifications_skipped",
            "bytes_scanned",
            "expected_scenario",
        ):
            print(f"  {field}: {result[field]}")

    if not results:
        print("No matching completion summary found; preserve evidence and investigate.")

    print(f"Evidence: {evidence.relative_to(ROOT)}")
    return 0 if results and all(
        result["expected_scenario"] == "PASS" for result in results
    ) else 2

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
