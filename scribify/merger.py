from typing import Iterable, List


def merge_transcriptions(chunks: Iterable[str]) -> str:
    cleaned: List[str] = [chunk.strip() for chunk in chunks if chunk and chunk.strip()]
    return "\n".join(cleaned)
