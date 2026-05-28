import os
import pathlib
import shutil

import downloadtools

urls = [
    "https://picsum.photos/200/200.jpg",
    "https://picsum.photos/300/300.jpg",
    "https://picsum.photos/300/400.jpg",
    "https://picsum.photos/500/500.jpg",
    "https://picsum.photos/600/600.jpg",
]


def cleanup():
    location = pathlib.Path(".media")
    if location.exists():
        if location.is_dir():
            shutil.rmtree(location)
        else:
            location.unlink()


def test_basic() -> None:
    """
    Env conditions:
    - media folder does not exist

    Expected:
    - media folder is created
    - 5 files in media folder
    """
    cleanup()
    try:
        shutil.rmtree(".media")
    except FileNotFoundError:
        pass

    items = []
    for i, url in enumerate(urls):
        items.append((url, str(i + 1)))

    obj = downloadtools.DownloadTools()
    obj.download_media(downloadtools.make_items(items), location=".media")

    assert os.path.exists(".media")
    assert os.path.exists(".media/1.jpg")
    assert os.path.exists(".media/2.jpg")
    assert os.path.exists(".media/3.jpg")
    assert os.path.exists(".media/4.jpg")
    assert os.path.exists(".media/5.jpg")
    cleanup()
