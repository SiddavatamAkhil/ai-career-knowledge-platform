"""
Lightweight local persistence layer.

No real database is set up for this project, so every "table" (chat
history, resumes, quizzes, feedback, users, ...) is just a JSON file under
storage/. This is deliberately simple: it keeps the demo runnable with zero
setup (no Postgres/SQLite server, no migrations) while still giving every
page real persistence across reruns and restarts.

Swap-out point: replace load()/save() bodies with real DB calls and every
page in pages/ keeps working unchanged, since they only ever call
storage.load(name) / storage.save(name, data).
"""
import json
import os
import time
import uuid
from typing import Any

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage")
os.makedirs(STORAGE_DIR, exist_ok=True)


def _path(name: str) -> str:
    return os.path.join(STORAGE_DIR, f"{name}.json")


def load(name: str, default: Any = None):
    path = _path(name)
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def save(name: str, data: Any):
    with open(_path(name), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def append_record(name: str, record: dict):
    """Append a dict to a JSON list, auto-adding id + created_at."""
    records = load(name, [])
    record = dict(record)
    record.setdefault("id", str(uuid.uuid4())[:8])
    record.setdefault("created_at", time.strftime("%Y-%m-%d %H:%M:%S"))
    records.append(record)
    save(name, records)
    return record


def clear(name: str):
    save(name, [])
