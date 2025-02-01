from typing import Optional

from pydantic import AfterValidator, ConfigDict
from pydantic.dataclasses import dataclass
from typing_extensions import Annotated


def check_filename(var: str) -> str:
    for ch in var:
        if ch in '<>:"/\\|?*':
            raise ValueError(f"Invalid character '{ch}' in filename '{var}'")
    return var


def check_location(var: str) -> str:
    for ch in var:
        if ch in '<>:"|?*':
            raise ValueError(f"Invalid character '{ch}' in location '{var}'")
    return var


FileName = Annotated[str, AfterValidator(check_filename)]
Location = Annotated[str, AfterValidator(check_location)]


@dataclass(frozen=True, config=ConfigDict(extra="forbid"))
class DownloadToolsItem:
    """Dataclass for storing information about a file to be downloaded."""

    url: str
    filename: Optional[FileName] = None
    location: Optional[Location] = None
    disable_special_check: bool = False
