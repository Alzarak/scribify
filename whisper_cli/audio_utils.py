import os
from typing import Dict

from pydub import AudioSegment
from pydub.utils import which

from .constants import SUPPORTED_FORMATS
from .exceptions import AudioFileError


def _check_ffmpeg() -> None:
    if not which("ffmpeg"):
        raise AudioFileError("FFmpeg not found. Install with: apt-get install ffmpeg")


def get_file_size_mb(file_path: str) -> float:
    if not os.path.exists(file_path):
        raise AudioFileError(f"Audio file not found: {file_path}")
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def validate_audio_file(file_path: str) -> None:
    if not os.path.exists(file_path):
        raise AudioFileError(f"Audio file not found: {file_path}")
    ext = os.path.splitext(file_path)[1].lstrip(".").lower()
    if ext and ext not in SUPPORTED_FORMATS:
        raise AudioFileError(
            f"Unsupported audio format: .{ext}. Supported: {', '.join(SUPPORTED_FORMATS)}"
        )
    _check_ffmpeg()


def get_audio_info(file_path: str) -> Dict[str, float]:
    validate_audio_file(file_path)
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as exc:
        raise AudioFileError(f"Failed to read audio file: {file_path}") from exc
    return {
        "size_mb": get_file_size_mb(file_path),
        "duration_seconds": len(audio) / 1000.0,
        "format": os.path.splitext(file_path)[1].lstrip(".").lower(),
    }
