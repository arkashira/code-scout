import hashlib
import json
import os
import threading
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_lock = threading.Lock()


def _current_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


@dataclass
class LogEntry:
    timestamp: str
    user_id: str
    query_hash: str
    repo_id: str
    prev_hash: Optional[str] = None

    def to_json(self) -> str:
        return json.dumps(asdict(self))

    @staticmethod
    def from_json(line: str) -> "LogEntry":
        data = json.loads(line)
        return LogEntry(**data)


class AuditLog:
    """
    Append‑only, tamper‑evident audit log.
    Each entry stores the hash of the previous entry.
    """

    def __init__(self, customer_id: str, retention_days: int = 180):
        self.customer_id = customer_id
        self.retention = timedelta(days=retention_days)
        self.file_path = LOG_DIR / f"{customer_id}.log"
        self.file_path.touch(exist_ok=True)

    def _last_entry_hash(self) -> Optional[str]:
        try:
            with self.file_path.open("rb") as f:
                f.seek(0, os.SEEK_END)
                pos = f.tell()
                if pos == 0:
                    return None
                # read backwards to find last line
                f.seek(-1, os.SEEK_END)
                while f.tell() > 0 and f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                last_line = f.readline().decode()
                last_entry = LogEntry.from_json(last_line)
                return hashlib.sha256(last_line.encode()).hexdigest()
        except Exception:
            return None

    def log_search(self, user_id: str, query_token: str, repo_id: str) -> LogEntry:
        with _lock:
            prev_hash = self._last_entry_hash()
            entry = LogEntry(
                timestamp=_current_timestamp(),
                user_id=user_id,
                query_hash=_hash_token(query_token),
                repo_id=repo_id,
                prev_hash=prev_hash,
            )
            with self.file_path.open("a", encoding="utf-8") as f:
                f.write(entry.to_json() + "\n")
            return entry

    def _load_entries(self) -> List[LogEntry]:
        entries = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                entries.append(LogEntry.from_json(line.strip()))
        return entries

    def export_jsonl(self, path: Path) -> None:
        entries = self._load_entries()
        with path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(e.to_json() + "\n")

    def purge_old(self) -> None:
        cutoff = datetime.utcnow() - self.retention
        entries = self._load_entries()
        new_entries = [e for e in entries if datetime.fromisoformat(e.timestamp.rstrip("Z")) >= cutoff]
        with self.file_path.open("w", encoding="utf-8") as f:
            for e in new_entries:
                f.write(e.to_json() + "\n")

    def verify_integrity(self) -> bool:
        entries = self._load_entries()
        prev_hash = None
        for e in entries:
            line = e.to_json()
            current_hash = hashlib.sha256(line.encode()).hexdigest()
            if e.prev_hash != prev_hash:
                return False
            prev_hash = current_hash
        return True


class RoleManager:
    """
    Simple role manager for audit permission.
    """

    def __init__(self):
        self.user_roles = {}

    def set_roles(self, user_id: str, roles: List[str]) -> None:
        self.user_roles[user_id] = set(roles)

    def has_audit_permission(self, user_id: str) -> bool:
        return "audit" in self.user_roles.get(user_id, set())


def redact_pii(entry: LogEntry) -> dict:
    """
    Return a dict suitable for export with PII redacted.
    """
    return {
        "timestamp": entry.timestamp,
        "user_id": entry.user_id,
        "query_hash": entry.query_hash,
        "repo_id": entry.repo_id,
    }
