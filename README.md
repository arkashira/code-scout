# Code‑Scout Audit Log

A minimal, pure‑Python implementation of an immutable, tamper‑evident audit log for search activity.  
Features:

- Append‑only log file with hash chaining for tamper detection.
- Configurable retention period per customer.
- Export to JSONL with PII redacted (only hashed query token stored).
- Simple role manager to restrict export access to users with `audit` permission.

## Usage
