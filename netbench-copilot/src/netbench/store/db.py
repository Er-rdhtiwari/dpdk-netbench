"""SQLite database access layer for storing runs and artifacts."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from netbench.config import settings
from netbench.store.models import (
    ComparisonResult,
    DatasetRecord,
    EvalResult,
    RunRecord,
    RunStatus,
)


class RunStore:
    """SQLite-based storage for benchmark runs and artifacts."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize the run store.

        Args:
            db_path: Path to SQLite database file. Uses settings.database_path if None.
        """
        self.db_path = db_path or settings.database_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    benchmark TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    nl_goal TEXT,
                    run_yaml TEXT,
                    tuning_profile_yaml TEXT,
                    cmd_sh TEXT,
                    env_snapshot TEXT,
                    metrics_json TEXT,
                    summary_md TEXT,
                    citations_json TEXT,
                    log_paths TEXT,
                    requires_approval INTEGER DEFAULT 0,
                    approval_reason TEXT,
                    parse_warnings TEXT,
                    validation_errors TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS comparisons (
                    comparison_id TEXT PRIMARY KEY,
                    baseline_run_id TEXT NOT NULL,
                    candidate_run_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    delta_json TEXT NOT NULL,
                    summary_md TEXT NOT NULL,
                    significant_changes TEXT,
                    FOREIGN KEY (baseline_run_id) REFERENCES runs(run_id),
                    FOREIGN KEY (candidate_run_id) REFERENCES runs(run_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    dataset_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    source_run_ids TEXT NOT NULL,
                    split TEXT NOT NULL,
                    record_count INTEGER NOT NULL,
                    export_path TEXT NOT NULL,
                    redacted INTEGER DEFAULT 1
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS eval_results (
                    eval_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    passed INTEGER NOT NULL,
                    score REAL NOT NULL,
                    details TEXT NOT NULL,
                    errors TEXT
                )
            """)

            conn.commit()

    def save_run(self, run: RunRecord) -> None:
        """Save or update a run record.

        Args:
            run: Run record to save
        """
        run.updated_at = datetime.utcnow()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO runs (
                    run_id, benchmark, platform, status, created_at, updated_at,
                    nl_goal, run_yaml, tuning_profile_yaml, cmd_sh, env_snapshot,
                    metrics_json, summary_md, citations_json, log_paths,
                    requires_approval, approval_reason, parse_warnings, validation_errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run.run_id,
                    run.benchmark.value,
                    run.platform.value,
                    run.status.value,
                    run.created_at.isoformat(),
                    run.updated_at.isoformat(),
                    run.nl_goal,
                    run.run_yaml,
                    run.tuning_profile_yaml,
                    run.cmd_sh,
                    json.dumps(run.env_snapshot) if run.env_snapshot else None,
                    run.metrics_json,
                    run.summary_md,
                    run.citations_json,
                    json.dumps(run.log_paths) if run.log_paths else None,
                    1 if run.requires_approval else 0,
                    run.approval_reason,
                    json.dumps(run.parse_warnings) if run.parse_warnings else None,
                    json.dumps(run.validation_errors) if run.validation_errors else None,
                ),
            )
            conn.commit()

    def get_run(self, run_id: str) -> Optional[RunRecord]:
        """Retrieve a run record by ID.

        Args:
            run_id: Run identifier

        Returns:
            Run record if found, None otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()

            if not row:
                return None

            return RunRecord(
                run_id=row["run_id"],
                benchmark=row["benchmark"],
                platform=row["platform"],
                status=RunStatus(row["status"]),
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                nl_goal=row["nl_goal"],
                run_yaml=row["run_yaml"],
                tuning_profile_yaml=row["tuning_profile_yaml"],
                cmd_sh=row["cmd_sh"],
                env_snapshot=json.loads(row["env_snapshot"]) if row["env_snapshot"] else None,
                metrics_json=row["metrics_json"],
                summary_md=row["summary_md"],
                citations_json=row["citations_json"],
                log_paths=json.loads(row["log_paths"]) if row["log_paths"] else None,
                requires_approval=bool(row["requires_approval"]),
                approval_reason=row["approval_reason"],
                parse_warnings=json.loads(row["parse_warnings"])
                if row["parse_warnings"]
                else None,
                validation_errors=json.loads(row["validation_errors"])
                if row["validation_errors"]
                else None,
            )

    def list_runs(
        self, benchmark: Optional[str] = None, status: Optional[RunStatus] = None, limit: int = 100
    ) -> List[RunRecord]:
        """List run records with optional filters.

        Args:
            benchmark: Filter by benchmark type
            status: Filter by status
            limit: Maximum number of records to return

        Returns:
            List of run records
        """
        query = "SELECT * FROM runs WHERE 1=1"
        params: List[str] = []

        if benchmark:
            query += " AND benchmark = ?"
            params.append(benchmark)

        if status:
            query += " AND status = ?"
            params.append(status.value)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(str(limit))

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

            return [
                RunRecord(
                    run_id=row["run_id"],
                    benchmark=row["benchmark"],
                    platform=row["platform"],
                    status=RunStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    nl_goal=row["nl_goal"],
                    run_yaml=row["run_yaml"],
                    tuning_profile_yaml=row["tuning_profile_yaml"],
                    cmd_sh=row["cmd_sh"],
                    env_snapshot=json.loads(row["env_snapshot"])
                    if row["env_snapshot"]
                    else None,
                    metrics_json=row["metrics_json"],
                    summary_md=row["summary_md"],
                    citations_json=row["citations_json"],
                    log_paths=json.loads(row["log_paths"]) if row["log_paths"] else None,
                    requires_approval=bool(row["requires_approval"]),
                    approval_reason=row["approval_reason"],
                    parse_warnings=json.loads(row["parse_warnings"])
                    if row["parse_warnings"]
                    else None,
                    validation_errors=json.loads(row["validation_errors"])
                    if row["validation_errors"]
                    else None,
                )
                for row in rows
            ]

    def save_comparison(self, comparison: ComparisonResult) -> None:
        """Save a comparison result.

        Args:
            comparison: Comparison result to save
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO comparisons (
                    comparison_id, baseline_run_id, candidate_run_id, created_at,
                    delta_json, summary_md, significant_changes
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    comparison.comparison_id,
                    comparison.baseline_run_id,
                    comparison.candidate_run_id,
                    comparison.created_at.isoformat(),
                    comparison.delta_json,
                    comparison.summary_md,
                    json.dumps(comparison.significant_changes),
                ),
            )
            conn.commit()

    def save_dataset(self, dataset: DatasetRecord) -> None:
        """Save a dataset export record.

        Args:
            dataset: Dataset record to save
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO datasets (
                    dataset_id, created_at, source_run_ids, split,
                    record_count, export_path, redacted
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset.dataset_id,
                    dataset.created_at.isoformat(),
                    json.dumps(dataset.source_run_ids),
                    dataset.split,
                    dataset.record_count,
                    dataset.export_path,
                    1 if dataset.redacted else 0,
                ),
            )
            conn.commit()

    def save_eval_result(self, result: EvalResult) -> None:
        """Save an evaluation result.

        Args:
            result: Evaluation result to save
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO eval_results (
                    eval_id, case_id, created_at, passed, score, details, errors
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.eval_id,
                    result.case_id,
                    result.created_at.isoformat(),
                    1 if result.passed else 0,
                    result.score,
                    json.dumps(result.details),
                    json.dumps(result.errors) if result.errors else None,
                ),
            )
            conn.commit()

    def get_all_runs_for_dataset(self) -> List[RunRecord]:
        """Get all completed runs for dataset generation.

        Returns:
            List of completed run records
        """
        return self.list_runs(status=RunStatus.PARSED, limit=10000)

# Made with Bob
