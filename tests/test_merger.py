from whisper_cli.merger import merge_transcriptions


def test_merge_transcriptions_skips_empty():
    result = merge_transcriptions(["hello", "", "  ", "world"])
    assert result == "hello\nworld"
