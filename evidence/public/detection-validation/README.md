# Evidence: Detection Logic Validation (AWSLAB-DET-001)

## What was tested

The SQL detection rule `AWSLAB-DET-001` was validated using two distinct testing methods:
1. **Recorded-event integration tests (`queries/tests/AWSLAB-DET-001-validation.sql`):** Evaluated against delivered CloudTrail records. Tested that the denied `GetBucketTagging` event returned 1 match (positive PASS) and that the allowed `GetBucketLocation` event returned 0 matches (negative PASS).
2. **Synthetic predicate unit tests (`queries/tests/AWSLAB-DET-001-unit-tests.sql`):** Evaluated against 9 synthetic fixture rows to verify predicate boundary conditions (different operations, services, error codes, roles, identity types, and SQL NULL values).
3. **Operational rolling-window execution (`scripts/run_detection.py`):** Executed the 24-hour lookback query via Athena over partition-projected CloudTrail logs.

---

## Files in this directory

| File | Origin | Description |
| :--- | :--- | :--- |
| `AWSLAB-DET-001-validation.csv` | Athena query export | Results of positive and negative integration test queries showing 1 match on denied tagging and 0 matches on allowed location. |
| `AWSLAB-DET-001-unit-tests.csv` | Athena query export | Results of 9 synthetic predicate test cases (01_positive through 09_missing_identity_type), all reporting PASS. |
| `findings.csv` | Athena query export | Result of operational detection query `AWSLAB-DET-001-windowed.sql` identifying candidate finding for event `7d900e24-00d4-45ed-979b-f7b80a0d8850`. |
| `athena-execution.json` | Athena API (`GetQueryExecution`) | Metadata for the operational detection query execution (`5ee023bd-3b91-4b4e-90c4-117222d1ce32`). |
| `run-manifest.json` | Script output | Execution manifest recording SQL SHA-256 (`de15fd09...`), bytes scanned (162,853 bytes), and execution timing. |
| `checksums.sha256` | Local verification | SHA-256 hashes of all published files in this directory. |

---

## Fields removed or replaced

None. The query result CSVs and execution metadata contain only structured detection output, query identifiers, execution statistics, and lab resource names. No secrets or personal addresses exist in these files.

---

## Artifact correlation

- **Event correlation:** `findings.csv` matches event ID `7d900e24-00d4-45ed-979b-f7b80a0d8850` from `evidence/public/authorization/matched-event-tagging.json`.
- **Query correlation:** Query ID `5ee023bd-3b91-4b4e-90c4-117222d1ce32` connects `athena-execution.json`, `run-manifest.json`, and subsequent notification payloads.
- **Log correlation:** The source log identified in `findings.csv` (`..._ZKinf66FSNOdVER8.json.gz`) corresponds to the log validated in `evidence/public/log-integrity/validation.txt`.

---

## What the evidence establishes

- Proves that the SQL predicate correctly filters for the target unauthorized action while excluding permitted actions and alternative operations.
- Demonstrates successful query execution against partition-projected Athena tables with enforced scan cutoffs.

---

## What remains outside scope

- Synthetic test cases test SQL filter logic only; they do not test log delivery latency or JSON parsing in CloudTrail.
- The 24-hour lookback window is bounded to the regional Stockholm trail.

