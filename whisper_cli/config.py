import os
from dataclasses import dataclass
from typing import Optional

from .constants import CHUNK_SIZE_MB, DEFAULT_MODEL, OPENAI_ENV_VAR
from .exceptions import ConfigurationError


@dataclass
class Config:
    api_key: str
    model: str = DEFAULT_MODEL
    chunk_size_mb: int = CHUNK_SIZE_MB
    verbose: bool = False
    quiet: bool = False

    @classmethod
    def load(
        cls,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        chunk_size_mb: Optional[int] = None,
        verbose: bool = False,
        quiet: bool = False,
    ) -> "Config":
        resolved_key = api_key or os.getenv(OPENAI_ENV_VAR)
        if not resolved_key:
            raise ConfigurationError(f"Missing API key. Set {OPENAI_ENV_VAR}.")
        resolved_model = model or DEFAULT_MODEL
        resolved_chunk = chunk_size_mb or CHUNK_SIZE_MB
        if resolved_chunk <= 0:
            raise ConfigurationError("Chunk size must be a positive integer (MB).")
        return cls(
            api_key=resolved_key,
            model=resolved_model,
            chunk_size_mb=resolved_chunk,
            verbose=verbose,
            quiet=quiet,
        )
