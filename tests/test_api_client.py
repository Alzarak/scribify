import pytest

pytest.importorskip("openai")

from whisper_cli import api_client as api_client_module


class DummyResult:
    def __init__(self, text: str) -> None:
        self.text = text


class DummyTranscriptions:
    def create(self, model, file, response_format):
        return DummyResult("ok")


class DummyAudio:
    def __init__(self):
        self.transcriptions = DummyTranscriptions()


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.audio = DummyAudio()


def test_transcribe_file_returns_text(tmp_path, monkeypatch):
    monkeypatch.setattr(api_client_module, "OpenAI", lambda api_key: DummyClient())
    client = api_client_module.OpenAITranscriptionClient(api_key="test")

    audio_path = tmp_path / "sample.mp3"
    audio_path.write_bytes(b"audio")

    result = client.transcribe_file(str(audio_path))
    assert result == "ok"
