"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="LLM model name")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", description="Embedding model name"
    )
    openai_api_base: Optional[str] = Field(
        default=None, description="Optional custom API base URL"
    )

    # MCP Server Configuration
    mcp_server_host: str = Field(default="localhost", description="MCP server host")
    mcp_server_port: int = Field(default=8765, description="MCP server port")

    # Safety Configuration
    netbench_approval_token: Optional[str] = Field(
        default=None, description="Approval token for BIOS changes and reboots"
    )

    # Database Configuration
    database_path: Path = Field(
        default=Path(".cache/netbench.db"), description="SQLite database path"
    )

    # Index Configuration
    index_path: Path = Field(default=Path(".cache/index"), description="Vector index path")
    chunk_size: int = Field(default=512, description="Text chunk size for indexing")
    chunk_overlap: int = Field(default=50, description="Chunk overlap size")

    # Retrieval Configuration
    top_k: int = Field(default=5, description="Number of chunks to retrieve")
    similarity_threshold: float = Field(
        default=0.7, description="Minimum similarity score for retrieval"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")

    # Dataset Configuration
    dataset_train_split: float = Field(default=0.8, description="Training split ratio")
    dataset_val_split: float = Field(default=0.1, description="Validation split ratio")
    dataset_test_split: float = Field(default=0.1, description="Test split ratio")

    # Optional Fine-tuning Configuration
    model_id: str = Field(
        default="mistralai/Mistral-7B-v0.1", description="Base model for fine-tuning"
    )
    lora_r: int = Field(default=8, description="LoRA rank")
    lora_alpha: int = Field(default=16, description="LoRA alpha")
    lora_dropout: float = Field(default=0.05, description="LoRA dropout")
    training_epochs: int = Field(default=3, description="Training epochs")
    batch_size: int = Field(default=4, description="Training batch size")
    learning_rate: float = Field(default=2e-4, description="Learning rate")

    def ensure_paths(self) -> None:
        """Ensure required directories exist."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.index_path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Made with Bob
