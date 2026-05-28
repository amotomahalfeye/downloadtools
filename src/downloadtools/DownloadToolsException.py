class DownloadToolsException(Exception):
    """Base class for exceptions in this module."""

    ...


class NotMedia(DownloadToolsException):
    """File is not image or video"""

    def __init__(self, content_type: str | None) -> None:
        self.content_type = content_type

    def __str__(self) -> str:
        return f"Content-Type {self.content_type} not media"


class FileNameNone(DownloadToolsException):
    """File name is None"""

    def __str__(self) -> str:
        return "filename is None"


class ExceedsContentSize(DownloadToolsException):
    """Content size exceeds size limit"""

    def __init__(self, size_limit: int, content_length: int) -> None:
        self.size_limit = size_limit
        self.content_length = content_length

    def __str__(self) -> str:
        return f"content size {self.content_length} exceeds size limit {self.size_limit}"
