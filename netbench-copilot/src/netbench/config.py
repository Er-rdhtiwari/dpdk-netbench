from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class NetbenchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NETBENCH_", env_file=".env", extra="ignore")

    db_path: Path = Field(default=Path(".cache/netbench.db"))
    index_dir: Path = Field(default=Path(".cache/index"))
    out_dir: Path = Field(default=Path("out"))
    approval_token: str | None = Field(default=None)
    log_level: str = Field(default="INFO")
    model_id: str = Field(default="gpt2")

    kb_manifest: Path = Field(default=Path("data/kb/manifest.yaml"))
    kb_pdfs_dir: Path = Field(default=Path("data/kb/pdfs"))


settings = NetbenchSettings()
