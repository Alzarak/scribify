import os
import pytest

from whisper_cli.config import Config
from whisper_cli.exceptions import ConfigurationError


def test_config_load_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    config = Config.load()
    assert config.api_key == "test-key"


def test_config_missing_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        Config.load()
