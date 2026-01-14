import os

import pytest

pytest.importorskip("pydub")

from whisper_cli import chunker as chunker_module


class FakeAudio:
    def __init__(self, duration_ms: int) -> None:
        self.duration_ms = duration_ms

    def __len__(self) -> int:
        return self.duration_ms

    def __getitem__(self, item):
        start = item.start or 0
        stop = item.stop or self.duration_ms
        return FakeAudio(stop - start)

    def export(self, path: str, format: str) -> None:
        with open(path, "wb") as handle:
            handle.write(b"fake audio")


def test_chunker_creates_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(chunker_module, "TEMP_CHUNK_DIR", str(tmp_path))
    monkeypatch.setattr(chunker_module, "AudioSegment", type("X", (), {"from_file": lambda *_: FakeAudio(10000)}))
    monkeypatch.setattr(chunker_module, "get_file_size_mb", lambda *_: 50)

    audio_chunker = chunker_module.AudioChunker(chunk_size_mb=20)
    chunks = audio_chunker.chunk_audio("sample.mp3")

    assert len(chunks) == 3
    for chunk in chunks:
        assert os.path.exists(chunk)

    audio_chunker.cleanup_chunks(chunks)
    for chunk in chunks:
        assert not os.path.exists(chunk)
