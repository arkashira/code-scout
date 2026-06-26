import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime, timedelta

import pytest

from logging import AuditLog, RoleManager, redact_pii, LogEntry


@pytest.fixture
def tmp_log_dir(tmp_path_factory):
    dir_path = tmp_path_factory.mktemp("logs")
    # monkeypatch LOG_DIR
    from logging import LOG_DIR

    original = LOG_DIR
    LOG_DIR = dir_path
    yield dir_path
    LOG_DIR = original
    shutil.rmtree(dir_path, ignore_errors=True)


def test_log_entry_creation(tmp_log_dir):
    log = AuditLog("cust1", retention_days=1)
    entry = log.log_search("user123", "search term", "repoA")
    assert isinstance(entry, LogEntry)
    assert entry.user_id == "user123"
    assert entry.repo_id == "repoA"
    assert entry.query_hash != "search term"
    # tamper-evident: prev_hash should be None for first entry
    assert entry.prev_hash is None
    # file contains the entry
    with open(log.file_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 1
    loaded = LogEntry.from_json(lines[0].strip())
    assert loaded == entry


def test_tamper_detection(tmp_log_dir):
    log = AuditLog("cust2")
    e1 = log.log_search("u1", "q1", "repo1")
    e2 = log.log_search("u2", "q2", "repo2")
    assert log.verify_integrity() is True
    # tamper with file
    with open(log.file_path, "r+") as f:
        f.seek(0)
        f.write("tampered\n")
    assert log.verify_integrity() is False


def test_retention(tmp_log_dir):
    log = AuditLog("cust3", retention_days=0)  # 0 days for test
    log.log_search("u1", "q1", "repo1")
    log.purge_old()
    with open(log.file_path, "r") as f:
        lines = f.readlines()
    assert len(lines) == 0


def test_export_and_redact(tmp_log_dir):
    log = AuditLog("cust4")
    e1 = log.log_search("u1", "q1", "repo1")
    e2 = log.log_search("u2", "q2", "repo2")
    export_path = tmp_log_dir / "export.jsonl"
    log.export_jsonl(export_path)
    with export_path.open("r") as f:
        lines = f.readlines()
    assert len(lines) == 2
    for line, original in zip(lines, [e1, e2]):
        data = json.loads(line.strip())
        redacted = redact_pii(original)
        assert data == redacted


def test_role_manager(tmp_log_dir):
    rm = RoleManager()
    rm.set_roles("alice", ["audit", "user"])
    rm.set_roles("bob", ["user"])
    assert rm.has_audit_permission("alice") is True
    assert rm.has_audit_permission("bob") is False
    assert rm.has_audit_permission("charlie") is False
