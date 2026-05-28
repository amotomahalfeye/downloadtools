from pydantic import ConfigDict, TypeAdapter

from .DownloadToolsItem import DownloadToolsItem
from .DownloadToolsItem import FileName, Location

config_dict = ConfigDict(strict=True)

ItemType1 = str
ItemType1Adapter = TypeAdapter(ItemType1, config=config_dict)
ItemType2 = tuple[str, FileName]
ItemType2Adapter = TypeAdapter(ItemType2, config=config_dict)
ItemType3 = tuple[str, FileName | None, Location]
ItemType3Adapter = TypeAdapter(ItemType3, config=config_dict)
ItemType4 = tuple[str, FileName | None, Location | None, bool]
ItemType4Adapter = TypeAdapter(ItemType4, config=config_dict)
ItemType5 = list[ItemType1 | ItemType2 | ItemType3 | ItemType4]
ItemType5Adapter = TypeAdapter(ItemType5, config=config_dict)
ItemType = ItemType1 | ItemType2 | ItemType3 | ItemType4 | ItemType5


def make_items(items: ItemType) -> list[DownloadToolsItem]:
    """
    Used to convert old import format to DownloadToolsItems

    :param items: items in old import format
    :return:
    """
    try:
        items = ItemType1Adapter.validate_python(items)
        return [DownloadToolsItem(items)]
    except ValueError:
        pass

    try:
        items = ItemType2Adapter.validate_python(items)
        return [DownloadToolsItem(items[0], items[1], None)]
    except ValueError:
        pass

    try:
        items = ItemType3Adapter.validate_python(items)
        return [DownloadToolsItem(items[0], items[1], items[2])]
    except ValueError:
        pass

    try:
        items = ItemType4Adapter.validate_python(items)
        return [DownloadToolsItem(items[0], items[1], items[2], items[3])]
    except ValueError:
        pass

    try:
        if isinstance(items, list):
            items = ItemType5Adapter.validate_python(items)
            return [make_items(item)[0] for item in items]
    except ValueError:
        pass

    raise ValueError("items didn't match ItemType")
