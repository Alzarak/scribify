from typing import List, Optional

from .api_client import OpenAITranscriptionClient
from .audio_utils import get_file_size_mb, validate_audio_file
from .chunker import AudioChunker
from .constants import MAX_FILE_SIZE_MB
from .exceptions import WhisperCLIError
from .merger import merge_transcriptions
from .progress import ProgressReporter


class Transcriber:
    def __init__(
        self,
        client: OpenAITranscriptionClient,
        chunker: Optional[AudioChunker] = None,
        quiet: bool = False,
    ) -> None:
        self.client = client
        self.chunker = chunker or AudioChunker()
        self.quiet = quiet

    def transcribe(self, audio_file: str) -> str:
        validate_audio_file(audio_file)
        size_mb = get_file_size_mb(audio_file)

        if size_mb <= MAX_FILE_SIZE_MB:
            return self.client.transcribe_file(audio_file)

        chunk_paths: List[str] = []
        try:
            chunk_paths = self.chunker.chunk_audio(audio_file)
            with ProgressReporter(quiet=self.quiet) as progress:
                task_id = progress.add_task("Transcribing chunks", total=len(chunk_paths))
                results: List[str] = []
                for chunk_path in chunk_paths:
                    results.append(self.client.transcribe_file(chunk_path))
                    progress.advance(task_id)
            return merge_transcriptions(results)
        except WhisperCLIError:
            raise
        except Exception as exc:
            raise WhisperCLIError("Unexpected transcription error.") from exc
        finally:
            if chunk_paths:
                try:
                    self.chunker.cleanup_chunks(chunk_paths)
                except Exception:
                    if not self.quiet:
                        print("Warning: failed to clean up temp chunks")
