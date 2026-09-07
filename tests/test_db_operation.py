import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pytest

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schema.sql"


@pytest.fixture
def db_connect():
    """Fresh In-Memory Database, schema applied, for each test case."""
    connect_obj = sqlite3.connect(":memory:")
    connect_obj.execute("PRAGMA foreign_keys = ON;")
    connect_obj.executescript(SCHEMA_PATH.read_text())
    yield connect_obj
    connect_obj.close()
    
    
def utc_now_str() -> str:
    return datetime.now(timezone.utc).isoformat()

def test_task_table_exists(db_connect):
    cursor_obj = db_connect.cursor()
    cursor_obj.execute("SELECT name FROM sqlite_master WHERE type = 'table' and name = 'tasks';")
    assert cursor_obj.fetchone() is not None
    
def test_valid_insert_succeeds(db_connect):
    now = utc_now_str()
    cursor_obj = db_connect.cursor()
    cursor_obj.execute(
        "INSERT INTO tasks (description, deadline_time, last_aged_at, created_at)"
        "VALUES (?,?,?,?)",
        ("Workout", "8:00", now, now),
    )
    db_connect.commit()
    
    cursor_obj.execute("SELECT description, status, delay_count FROM tasks WHERE id = 1;")
    row = cursor_obj.fetchone()
    assert row == ("Workout", "pending", 0)
    
def test_null_description_rejected(db_connect):
    now = utc_now_str()
    with pytest.raises(sqlite3.IntegrityError):
        db_connect.execute(
            "INSERT INTO tasks (description, last_aged_at, created_at) VALUES (?,?,?)",
            (None, now, now),
            )
        
def test_invalid_description_rejected(db_connect):
    now = utc_now_str()
    with pytest.raises(sqlite3.IntegrityError):
        db_connect.execute(
            "INSERT INTO tasks (description, status, last_aged_at, created_at)"
            "VALUES (?,?,?,?)",
            ("bad status task", "not a real staus", now, now),
        )
        
def test_negative_delay_count_rejected(db_connect):
    now = utc_now_str()
    with pytest.raises(sqlite3.IntegrityError):
        db_connect.execute(
            "INSERT INTO tasks (description, delay_count, last_aged_at, created_at)"
            "VALUES (?,?,?,?)",
            ("Negative delay task", -1, now, now),
        )
        
def test_default_status_is_pending(db_connect):
    now = utc_now_str()
    cursor_obj = db_connect.cursor()
    cursor_obj.execute(
        "INSERT INTO tasks (description, last_aged_at, created_at) VALUES (?,?,?)",
        ("No status specified", now, now),
    )
    db_connect.commit()
    
    cursor_obj.execute("SELECT status, delay_count FROM tasks WHERE id = 1;")
    status, delay_count  = cursor_obj.fetchone()
    assert status == "pending"
    assert delay_count == 0
    
def test_marking_task_completed(db_connect):
    now = utc_now_str()
    cursor_obj = db_connect.cursor()
    
    cursor_obj.execute(
        "INSERT INTO tasks (description, last_aged_at, created_at) VALUES (?,?,?)",
        ("Project completed", now, now),
    )
    db_connect.commit()
    
    cursor_obj.execute("UPDATE tasks SET status = 'completed' WHERE id = 1;")
    db_connect.commit()
    
    cursor_obj.execute("SELECT status FROM tasks WHERE id = 1;")
    assert cursor_obj.fetchone()[0] == "completed"
    
def test_pending_query_excludes_completed(db_connect):
    now = utc_now_str()
    cursor_obj = db_connect.cursor()
    
    cursor_obj.execute(
        "INSERT INTO tasks (description, last_aged_at, created_at) VALUES (?, ?, ?)",
        ("Pending task", now, now)
    )
    
    cursor_obj.execute(
            "INSERT INTO tasks (description, status, last_aged_at, created_at) VALUES (?, ?, ?, ?)",
            ("Completed Task", "completed", now, now)
    )
    db_connect.commit()
    
    cursor_obj.execute("SELECT description FROM tasks WHERE status = 'pending'")
    results = [r[0] for r in cursor_obj.fetchall()]
    assert results == ["Pending task"]