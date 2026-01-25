from __future__ import annotations

import sqlite3
from pathlib import Path

from netbench.store.models import RunRecord


SCHEMA = """
CREATE TABLE IF NOT EXISTS run_records (
    run_id TEXT PRIMARY KEY,
    benchmark TEXT NOT NULL,
    platform TEXT NOT NULL,
    nl_goal TEXT,
    run_yaml TEXT,
    tuning_profile TEXT,
    cmd_sh TEXT,
    metrics_json TEXT,
    summary_md TEXT,
    citations_json TEXT,
    env_snapshot TEXT,
    log_snippet TEXT,
    created_at TEXT NOT NULL
);
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path) -> None:
    conn = connect(db_path)
    conn.executescript(SCHEMA)
    # Lightweight migration for new columns.
    cols = {row[1] for row in conn.execute("PRAGMA table_info(run_records)").fetchall()}
    if "log_snippet" not in cols:
        conn.execute("ALTER TABLE run_records ADD COLUMN log_snippet TEXT")
    conn.commit()
    conn.close()


def insert_run(db_path: Path, record: RunRecord) -> None:
    init_db(db_path)
    conn = connect(db_path)
    conn.execute(
        """
        INSERT INTO run_records (
            run_id, benchmark, platform, nl_goal, run_yaml, tuning_profile, cmd_sh,
            metrics_json, summary_md, citations_json, env_snapshot, log_snippet, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.run_id,
            record.benchmark,
            record.platform,
            record.nl_goal,
            record.run_yaml,
            record.tuning_profile,
            record.cmd_sh,
            record.metrics_json,
            record.summary_md,
            record.citations_json,
            record.env_snapshot,
            record.log_snippet,
            record.created_at,
        ),
    )
    conn.commit()
    conn.close()


def fetch_run(db_path: Path, run_id: str) -> RunRecord | None:
    init_db(db_path)
    conn = connect(db_path)
    row = conn.execute("SELECT * FROM run_records WHERE run_id = ?", (run_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return RunRecord(**dict(row))


def list_runs(db_path: Path) -> list[RunRecord]:
    init_db(db_path)
    conn = connect(db_path)
    rows = conn.execute("SELECT * FROM run_records ORDER BY created_at DESC").fetchall()
    conn.close()
    return [RunRecord(**dict(row)) for row in rows]
