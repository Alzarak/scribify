class WhisperCLIError(Exception):
    """Base error for whisper CLI."""


class AudioFileError(WhisperCLIError):
    """Issues with audio files or metadata."""


class APIError(WhisperCLIError):
    """OpenAI API related issues."""


class ChunkingError(WhisperCLIError):
    """Errors during chunking or cleanup."""


class ConfigurationError(WhisperCLIError):
    """Invalid or missing configuration."""
