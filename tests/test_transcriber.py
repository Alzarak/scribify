import pytest

pytest.importorskip("openai")

from whisper_cli.transcriber import Transcriber


class DummyClient:
    def __init__(self):
        self.calls = []

    def transcribe_file(self, path: str) -> str:
        self.calls.append(path)
        return f"text-{len(self.calls)}"


class DummyChunker:
    def __init__(self, chunks):
        self._chunks = chunks
        self.cleaned = False

    def chunk_audio(self, file_path: str):
        return self._chunks

    def cleanup_chunks(self, chunk_paths):
        self.cleaned = True


def test_transcriber_small_file(monkeypatch):
    monkeypatch.setattr("whisper_cli.transcriber.validate_audio_file", lambda *_: None)
    monkeypatch.setattr("whisper_cli.transcriber.get_file_size_mb", lambda *_: 1)

    client = DummyClient()
    transcriber = Transcriber(client=client, quiet=True)
    result = transcriber.transcribe("audio.mp3")

    assert result == "text-1"
    assert client.calls == ["audio.mp3"]


def test_transcriber_chunked(monkeypatch, tmp_path):
    monkeypatch.setattr("whisper_cli.transcriber.validate_audio_file", lambda *_: None)
    monkeypatch.setattr("whisper_cli.transcriber.get_file_size_mb", lambda *_: 30)

    chunks = [str(tmp_path / "chunk1.mp3"), str(tmp_path / "chunk2.mp3")]
    chunker = DummyChunker(chunks)
    client = DummyClient()
    transcriber = Transcriber(client=client, chunker=chunker, quiet=True)

    result = transcriber.transcribe("audio.mp3")

    assert result == "text-1\ntext-2"
    assert chunker.cleaned
