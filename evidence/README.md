# AWSLab Evidence Archive

This directory organizes the verification artifacts and execution evidence for the AWSLab project across two distinct tiers: **public reviewed exports** and **private raw records**.

---

## Architecture and Boundaries

```text
evidence/
├── README.md               # Evidence model, provenance, and redaction philosophy
├── public/                 # Reviewed, machine-readable exports eligible for Git
│   ├── authorization/         # Least-privilege allowed vs denied execution evidence
│   ├── detection-validation/  # Athena validation results and 9 synthetic predicate test outputs
│   ├── cloud-publication/     # Cloud detection run, DynamoDB ledger state, SNS/SQS delivery receipts
│   ├── scheduled-validation/  # EventBridge Scheduler run summaries, verifier receipts, diagnostics
│   ├── log-integrity/         # Cryptographic CloudTrail validate-logs verbose output and scope
│   ├── iam-review/            # Nine policy snapshots and IAM Access Analyzer zero-finding results
│   ├── human-alert/           # CloudTrail event correlation, Lambda response, email notification payload
│   └── object-events/         # Controlled PutObject/GetObject/DeleteObject Data events and cleanup plan
└── private/                # Raw logs, binary plans, state, credentials, local databases (git-ignored)
```

---

## Evidence Standard

Every public claim in AWSLab is grounded in recorded execution evidence:

1. **Origin in real executions:** Artifacts in `evidence/public/` are reviewed exports derived directly from actual AWS CLI executions, Athena queries, Lambda function runs, and service responses. They are not fabricated or reconstructed mocks.
2. **Correlation integrity:** Correlation identifiers—such as CloudTrail Event IDs, Athena Query IDs, DynamoDB Finding IDs, AWS Account IDs, IAM Role names, and S3 Bucket names—are preserved consistently across files so that readers can trace an action from request to audit log, query result, publication ledger, and delivery inbox.
3. **Deliberate, documented review:** Sensitive personal and operational fields are reviewed and transformed transparently:
   - Personal client IP addresses (e.g., operator home/workstation IPs) are replaced with RFC 5737 documentation IP addresses (`198.51.100.24`).
   - Temporary STS session access key IDs are masked (`ASIA...[REDACTED]...`).
   - Actionable confirmation links, personal email addresses, and subscription unsubscribe URLs are removed.
   - CloudTrail event structures, timestamps, parameters, error codes, and audit metadata are preserved.
4. **Byte integrity vs. cryptographic provenance:**
   - Each public evidence directory includes a `checksums.sha256` file documenting the SHA-256 digests of the published files.
   - Because reviewed and redacted files undergo formatting or masking, their hashes differ from the original raw logs in `evidence/private/`. A file's SHA-256 verifies its byte integrity in this repository; it does not claim to match AWS CloudTrail's original unredacted digest signatures.
5. **Private tier:** `evidence/private/` retains untouched original compressed logs (`.json.gz`), unredacted event exports, local SQLite databases, and environment configuration. It is excluded from version control via `.gitignore`.

