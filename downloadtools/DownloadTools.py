from __future__ import annotations

import functools
import logging
import re
import shutil
import time
from pathlib import Path
from threading import Thread
from typing import Optional

import httpx

from .DownloadToolsException import NotMedia, FileNameNone, ExceedsContentSize
from .DownloadToolsItem import DownloadToolsItem
from .SpecialCaseUrl import SpecialCaseUrl
from .ThreadingHelper import ThreadingHelper
from .states import ProcessState, ResultState


class DownloadTools:
    """
    DownloadTools is a class that helps you download media from the internet.

    :param special_case_urls: A list of SpecialCaseUrl objects.
    :param head_check: If True, the program will send a HEAD request to the url to check if the url is a media file.
    :param follow_redirects: If True, the program will allow redirects.
    :param size_limit: The maximum size of the media file in bytes. If the size of the media file exceeds the limit,
        the program will raise an ExceedsContentSize exception.
    :param file_overwrite: If True, the program will overwrite the file if the file already exists.
    :param threads: The number of threads to use.
    :param fresh_folder: If True, the program will delete the folder if it already exists.
    :param disable_tqdm: If True, the program will disable tqdm.
    """

    def __init__(self,
                 threads: int = 100,
                 fresh_folder: bool = False,
                 special_case_urls: list[SpecialCaseUrl] = None,
                 head_check: bool = False,
                 follow_redirects: bool = True,
                 size_limit: int = float("inf"),
                 file_overwrite: bool = False,
                 disable_tqdm: bool = False) -> None:
        if special_case_urls is None:
            special_case_urls = []
        self.specialCaseUrls: list[SpecialCaseUrl] = special_case_urls
        self.head_check: bool = head_check
        self.follow_redirects: bool = follow_redirects
        self.size_limit: int = size_limit
        self.file_overwrite: bool = file_overwrite
        self.threads = threads
        self.fresh_folder = fresh_folder
        self.disable_tqdm = disable_tqdm

    @staticmethod
    def _resolve_folder(location: Path, fresh_folder: bool):
        if location.exists() is False:
            location.mkdir(parents=True, exist_ok=True)
        elif fresh_folder is False and location.is_dir() is False:
            raise NotADirectoryError(location)
        elif fresh_folder is True:
            if location.is_dir() is False:
                logging.warning(f"DownloadTools | {location} is not a directory. Deleting the file.")
                location.unlink()
            else:
                shutil.rmtree(location)
            location.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _extract_filename_content_disposition(content_disposition: str) -> tuple[str, str] | tuple[None, None]:
        temp = re.findall("filename=\"(.+)\"", content_disposition)
        if len(temp) == 0:
            return None, None
        filename = temp[0]
        filetype = filename.split(".")[-1]
        filename = filename[:len(filename) - (len(filetype) + 1)]
        return filename, filetype

    @staticmethod
    def _extract_filename_url(url: str) -> tuple[str, str] | tuple[None, None]:
        # remove query string
        filename = url.split("#")[0]
        filename = filename.split("?")[0]
        filename = filename.split("/")[-1]
        if filename == "":
            return None, None
        filetype = filename.split(".")[-1]
        if filetype == filename:
            return None, None
        filename = filename[:len(filename) - (len(filetype) + 1)]
        return filename, filetype

    @staticmethod
    def _extract_filename_user(user_filename: str) -> tuple[str, str | None]:
        filetype = user_filename.split(".")[-1]
        if filetype == user_filename:
            return user_filename, None
        filename = user_filename[:len(user_filename) - (len(filetype) + 1)]
        return filename, filetype

    @staticmethod
    def _extract_filetype_content_type(content_type: str) -> str:
        semicolon_index = content_type.find(";")
        if semicolon_index == -1:
            filetype = content_type[content_type.find("/") + 1:].strip()
        else:
            filetype = content_type[content_type.find("/") + 1:content_type.find(";")].strip()
        return filetype

    def _get_filename(self, url: str, user_filename: str = None, content_type: str = None,
                      content_disposition: str = None) -> tuple[str, str]:
        """
        1. user.filename and user.filetype
        2. user.filename and content_disposition.filetype
        3. user.filename and url.filetype
        4. user.filename and content_type.filetype
        5. content_disposition.filename and content_disposition.filetype
        6. url.filename and url.filetype
        """

        filename, filetype = None, None
        if user_filename is not None:
            filename, filetype = self._extract_filename_user(user_filename)
        if filename is not None:
            if filetype is not None:
                return filename, filetype
            if content_disposition is not None:
                _, filetype = self._extract_filename_content_disposition(content_disposition)
                if filetype is not None:
                    return filename, filetype
            _, filetype = self._extract_filename_url(url)
            if filetype is not None:
                return filename, filetype
            filetype = self._extract_filetype_content_type(content_type)
            return filename, filetype
        if content_disposition is not None:
            filename, filetype = self._extract_filename_content_disposition(content_disposition)
            if filename is not None:
                return filename, filetype
        filename, filetype = self._extract_filename_url(url)
        if filename is not None:
            return filename, filetype
        raise FileNameNone()

    @staticmethod
    def _resolve_filename(filename: str, filetype: str, location: Path, file_overwrite: bool) -> str:
        if file_overwrite:
            if (location / f'{filename}.{filetype}').exists() and (location / f'{filename}.{filetype}').is_dir():
                shutil.rmtree(location / f'{filename}.{filetype}')
            return f'{filename}.{filetype}'
        temp_filename = filename
        i = 2
        while (location / f'{temp_filename}.{filetype}').exists():
            temp_filename = f'{filename} ({i})'
            i += 1
        return f'{temp_filename}.{filetype}'

    @staticmethod
    def _check_media(content_type: str | None) -> None:
        if content_type is None or content_type.startswith(("image", "video")) is False:
            raise NotMedia(content_type)

    @staticmethod
    def _check_size(size_limit: int, content_length: str) -> None:
        if size_limit < int(content_length):
            raise ExceedsContentSize(size_limit, int(content_length))

    @staticmethod
    def _check_location(location: Path) -> None:
        try:
            location.mkdir(parents=True, exist_ok=True)
        except FileExistsError:
            raise NotADirectoryError(location)

    def _download_media_thread(self, helper: ThreadingHelper, thread_no: int) -> None:
        while True:
            process_state, item = helper.get_next()
            if process_state == ProcessState.EXIT:
                return
            if process_state == ProcessState.SLEEP:
                time.sleep(item)
                return
            url = item.url
            user_filename = item.filename
            location = helper.location / item.location if item.location else helper.location
            try:
                # special case urls
                if not item.disable_special_check:
                    for special_case_url in helper.special_case_urls:
                        special_case_url_output = special_case_url.check_url(url, user_filename, item.location)
                        if special_case_url_output is not None:
                            helper.store_output(ResultState.SPECIAL_CASE_URL, item, special_case_url_output)
                            break
                # head check
                if helper.head_check:
                    response = httpx.head(url, follow_redirects=helper.follow_redirects)
                    content_type = response.headers.get("Content-Type")
                    content_length = response.headers.get("Content-Length")
                    self._check_media(content_type)
                    self._check_size(helper.size_limit, content_length)
                # get media
                response = httpx.get(url, follow_redirects=helper.follow_redirects)
                content_type = response.headers.get("Content-Type")
                content_length = response.headers.get("Content-Length")
                self._check_media(content_type)
                self._check_size(helper.size_limit, content_length)
                self._check_location(location)

                content_disposition = response.headers.get("Content-Disposition")
                filename, filetype = self._get_filename(url, user_filename, content_type, content_disposition)
                filename = self._resolve_filename(filename, filetype, location, helper.file_overwrite)
                location /= filename
                with open(location, "wb") as media_file:
                    media_file.write(response.content)

                helper.store_output(ResultState.SUCCESS, item, filename)
            except FileNameNone as error:
                logging.error(f"DownloadTools | error {thread_no} | {error} while processing {url}")
                helper.store_output(ResultState.FAILED, item, error)
            except NotMedia as error:
                logging.error(f"DownloadTools | error {thread_no} | {error} while processing {url}")
                helper.store_output(ResultState.FAILED, item, error)
            except ExceedsContentSize as error:
                logging.error(f"DownloadTools | error {thread_no} | {error} while processing {url}")
                helper.store_output(ResultState.FAILED, item, error)
            except NotADirectoryError as error:
                logging.error(f"DownloadTools | error {thread_no} | {error} while processing {url}")
                helper.store_output(ResultState.FAILED, item, error)

    def download_media(self, items: list[DownloadToolsItem],
                       location: str = ".",
                       threads: Optional[int] = None,
                       fresh_folder: Optional[bool] = None,
                       special_case_urls: Optional[list[SpecialCaseUrl]] = None,
                       head_check: Optional[bool] = None,
                       follow_redirects: Optional[bool] = None,
                       size_limit: Optional[int] = None,
                       file_overwrite: Optional[bool] = None,
                       disable_tqdm: Optional[bool] = None) \
            -> list[tuple[DownloadToolsItem, str | Exception]]:
        """
        Download media from the internet.

        :param items: list of DownloadToolsItem or dict that complies with the DownloadToolsItem schema.
        :param location: The location to store the media files.
        :param special_case_urls: Optional. Temporarily override for the special_case_urls parameter in the constructor.
        :param head_check: Optional. Temporarily override for the head_check parameter in the constructor.
        :param follow_redirects: Optional. Temporarily override for the follow_redirects parameter in the constructor.
        :param size_limit: Optional. Temporarily override for the size_limit parameter in the constructor.
        :param file_overwrite: Optional. Temporarily override for the file_overwrite parameter in the constructor.
        :param threads: Optional. Temporarily override for the threads parameter in the constructor.
        :param fresh_folder: Optional. Temporarily override for the fresh_folder parameter in the constructor.
        :param disable_tqdm: Optional. Temporarily override for the disable_tqdm parameter in the constructor.
        :return: A list of tuples of DownloadToolsItem and filename or exception.
        """

        if special_case_urls is None:
            special_case_urls = self.specialCaseUrls
        if head_check is None:
            head_check = self.head_check
        if follow_redirects is None:
            follow_redirects = self.follow_redirects
        if size_limit is None:
            size_limit = self.size_limit
        if file_overwrite is None:
            file_overwrite = self.file_overwrite
        if threads is None:
            threads = self.threads
        if fresh_folder is None:
            fresh_folder = self.fresh_folder
        if disable_tqdm is None:
            disable_tqdm = self.disable_tqdm
        path_obj = Path(location)
        self._resolve_folder(path_obj, fresh_folder)
        helper = ThreadingHelper(items, path_obj, special_case_urls, head_check, follow_redirects, size_limit,
                                 file_overwrite, disable_tqdm)
        tasks: list[Thread] = []
        for i in range(threads):
            tasks.append(Thread(target=functools.partial(self._download_media_thread, helper, i)))
        for task in tasks:
            task.start()
        for task in tasks:
            task.join()
        return helper.get_output()
