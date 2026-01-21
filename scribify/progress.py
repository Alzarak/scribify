from typing import Iterable, Optional, TypeVar

from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

T = TypeVar("T")


class ProgressReporter:
    def __init__(self, quiet: bool = False) -> None:
        self.quiet = quiet
        self._progress: Optional[Progress] = None

    def __enter__(self) -> "ProgressReporter":
        if not self.quiet:
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("{task.description}"),
                BarColumn(),
                TextColumn("{task.completed}/{task.total}"),
                TimeElapsedColumn(),
            )
            self._progress.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._progress:
            self._progress.stop()

    def add_task(self, description: str, total: int) -> Optional[int]:
        if not self._progress:
            return None
        return self._progress.add_task(description, total=total)

    def advance(self, task_id: Optional[int], advance: int = 1) -> None:
        if not self._progress or task_id is None:
            return
        self._progress.advance(task_id, advance)

    def track(self, items: Iterable[T], description: str) -> Iterable[T]:
        if not self._progress:
            return items
        return self._progress.track(items, description=description)
