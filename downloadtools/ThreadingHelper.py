from __future__ import annotations

from pathlib import Path
from threading import Lock

from pydantic import TypeAdapter
from tqdm import tqdm

from .DownloadToolsItem import DownloadToolsItem
from .SpecialCaseUrl import SpecialCaseUrl
from .states import ProcessState, ResultState


class ThreadingHelper:
    def __init__(self, items: list[DownloadToolsItem],
                 location: Path,
                 special_case_urls: list[SpecialCaseUrl] = None,
                 head_check: bool = False,
                 follow_redirects: bool = True,
                 size_limit: int = float("inf"),
                 file_overwrite: bool = False,
                 disable_tqdm: bool = False) -> None:
        self.location = location
        self.special_case_urls = special_case_urls
        self.head_check = head_check
        self.follow_redirects = follow_redirects
        self.size_limit = size_limit
        self.file_overwrite = file_overwrite
        self._lock = Lock()
        self._items: list[DownloadToolsItem] = TypeAdapter(list[DownloadToolsItem]).validate_python(items)
        self._bar = tqdm(total=len(self._items), disable=disable_tqdm)
        self._output: list[tuple[DownloadToolsItem, str | Exception]] = []
        self._active_threads = 0

    def store_output(self, result_state: ResultState, item: DownloadToolsItem,
                     output: Exception | str | list[DownloadToolsItem]) -> None:
        with self._lock:
            if result_state == ResultState.SUCCESS:
                self._output.append((item, output))
            if result_state == ResultState.FAILED:
                self._output.append((item, output))
            if result_state == ResultState.SPECIAL_CASE_URL:
                self._output.append((item, "SPECIAL_CASE_URL"))
                items = TypeAdapter(list[DownloadToolsItem]).validate_python(output)
                self._items.extend(items)
                self._bar.total += len(items)
                self._bar.refresh()
            self._active_threads -= 1
            self._bar.update()

    def get_output(self) -> list[tuple[DownloadToolsItem, str | Exception]]:
        self._bar.close()
        return self._output

    def get_next(self) -> tuple[ProcessState, DownloadToolsItem | int | None]:
        with self._lock:
            if len(self._items) == 0 and self._active_threads == 0:
                return ProcessState.EXIT, None
            elif len(self._items) == 0:
                return ProcessState.SLEEP, 1
            else:
                self._active_threads += 1
                return ProcessState.PROCESS, self._items.pop(0)
