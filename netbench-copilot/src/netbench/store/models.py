"""Database models for storing benchmark runs and artifacts."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BenchmarkType(str, Enum):
    """Supported benchmark types."""

    CRYPTOPERF = "cryptoperf"
    TESTPMD = "testpmd"
    L3FWD = "l3fwd"
    L2FWD = "l2fwd"


class PlatformType(str, Enum):
    """Supported platform types."""

    EPYC7003 = "epyc7003"
    EPYC8004 = "epyc8004"
    EPYC9004 = "epyc9004"
    GENERIC = "generic"


class RunStatus(str, Enum):
    """Run execution status."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARSED = "parsed"


class Citation(BaseModel):
    """Citation metadata for KB-grounded responses."""

    doc_id: str = Field(description="Document identifier")
    chunk_id: str = Field(description="Chunk identifier")
    source_file: str = Field(description="Source PDF filename")
    page_start: int = Field(description="Starting page number")
    page_end: int = Field(description="Ending page number")
    section: Optional[str] = Field(default=None, description="Section/heading if available")
    score: float = Field(description="Similarity score")
    text_snippet: str = Field(description="Retrieved text snippet")


class RunRecord(BaseModel):
    """Complete record of a benchmark run."""

    run_id: str = Field(description="Unique run identifier")
    benchmark: BenchmarkType = Field(description="Benchmark type")
    platform: PlatformType = Field(description="Platform type")
    status: RunStatus = Field(default=RunStatus.PLANNED, description="Run status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Update timestamp")

    # Input
    nl_goal: Optional[str] = Field(default=None, description="Natural language goal")
    run_yaml: Optional[str] = Field(default=None, description="Run plan YAML content")
    tuning_profile_yaml: Optional[str] = Field(
        default=None, description="Tuning profile YAML content"
    )
    cmd_sh: Optional[str] = Field(default=None, description="Command script content")
    env_snapshot: Optional[Dict[str, Any]] = Field(
        default=None, description="Environment snapshot"
    )

    # Output
    metrics_json: Optional[str] = Field(default=None, description="Metrics JSON content")
    summary_md: Optional[str] = Field(default=None, description="Summary markdown content")
    citations_json: Optional[str] = Field(default=None, description="Citations JSON content")
    log_paths: Optional[List[str]] = Field(default=None, description="Log file paths")

    # Metadata
    requires_approval: bool = Field(
        default=False, description="Requires manual approval for execution"
    )
    approval_reason: Optional[str] = Field(
        default=None, description="Reason for requiring approval"
    )
    parse_warnings: Optional[List[str]] = Field(
        default=None, description="Warnings from parsing"
    )
    validation_errors: Optional[List[str]] = Field(
        default=None, description="Validation errors"
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True


class ComparisonResult(BaseModel):
    """Result of comparing two runs."""

    comparison_id: str = Field(description="Unique comparison identifier")
    baseline_run_id: str = Field(description="Baseline run ID")
    candidate_run_id: str = Field(description="Candidate run ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")

    delta_json: str = Field(description="Delta metrics JSON content")
    summary_md: str = Field(description="Summary markdown content")
    significant_changes: List[str] = Field(
        default_factory=list, description="List of significant changes"
    )


class DatasetRecord(BaseModel):
    """Record for dataset export."""

    dataset_id: str = Field(description="Unique dataset identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    source_run_ids: List[str] = Field(description="Source run IDs")
    split: str = Field(description="Dataset split: train/val/test")
    record_count: int = Field(description="Number of records")
    export_path: str = Field(description="Export file path")
    redacted: bool = Field(default=True, description="Whether data was redacted")


class EvalCase(BaseModel):
    """Evaluation test case."""

    case_id: str = Field(description="Unique case identifier")
    category: str = Field(description="Evaluation category")
    description: str = Field(description="Case description")
    input_data: Dict[str, Any] = Field(description="Input data for evaluation")
    expected_output: Optional[Dict[str, Any]] = Field(
        default=None, description="Expected output patterns"
    )
    rubric: Dict[str, Any] = Field(description="Scoring rubric")


class EvalResult(BaseModel):
    """Result of running an evaluation case."""

    eval_id: str = Field(description="Unique evaluation identifier")
    case_id: str = Field(description="Case identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    passed: bool = Field(description="Whether the case passed")
    score: float = Field(description="Numeric score (0-1)")
    details: Dict[str, Any] = Field(description="Detailed results")
    errors: Optional[List[str]] = Field(default=None, description="Errors encountered")

# Made with Bob
