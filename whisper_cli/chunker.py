import math
import os
import uuid
from typing import List

from pydub import AudioSegment

from .audio_utils import get_file_size_mb
from .constants import CHUNK_SIZE_MB, TEMP_CHUNK_DIR
from .exceptions import ChunkingError


class AudioChunker:
    def __init__(self, chunk_size_mb: int = CHUNK_SIZE_MB) -> None:
        self.chunk_size_mb = chunk_size_mb
        self.temp_dir = None

    def chunk_audio(self, file_path: str) -> List[str]:
        try:
            audio = AudioSegment.from_file(file_path)
        except Exception as exc:
            raise ChunkingError(f"Failed to load audio for chunking: {file_path}") from exc

        file_size_mb = get_file_size_mb(file_path)
        num_chunks = max(1, math.ceil(file_size_mb / float(self.chunk_size_mb)))
        chunk_duration_ms = int(len(audio) / num_chunks)

        source_ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        export_format = "mp3"
        ext = export_format
        run_id = uuid.uuid4().hex[:8]
        self.temp_dir = os.path.join(TEMP_CHUNK_DIR, f"run_{run_id}")
        os.makedirs(self.temp_dir, exist_ok=True)

        chunk_paths: List[str] = []
        for idx in range(num_chunks):
            start_ms = idx * chunk_duration_ms
            end_ms = len(audio) if idx == num_chunks - 1 else (idx + 1) * chunk_duration_ms
            chunk = audio[start_ms:end_ms]
            chunk_name = f"chunk_{idx + 1:03d}.{ext}"
            chunk_path = os.path.join(self.temp_dir, chunk_name)
            try:
                chunk.export(chunk_path, format=export_format)
            except Exception as exc:
                raise ChunkingError(f"Failed to export chunk {chunk_name}") from exc
            chunk_paths.append(chunk_path)

        return chunk_paths

    def cleanup_chunks(self, chunk_paths: List[str]) -> None:
        errors = []
        for path in chunk_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError as exc:
                errors.append(str(exc))
        if self.temp_dir and os.path.isdir(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except OSError:
                pass
        if errors:
            raise ChunkingError("Failed to clean up chunk files")
