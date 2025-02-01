import os
import shutil

import downloadtools


def test_basic() -> None:
    """
    Env conditions:
    - media folder does not exist

    Expected:
    - media folder is created
    - 5 files in media folder
    """
    try:
        shutil.rmtree(".media")
    except FileNotFoundError:
        pass

    urls = []
    with open('urls.txt') as f:
        for line in f:
            urls.append(line.strip())

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


def test_file_name_space() -> None:
    urls = []
    with open('urls.txt') as f:
        i = 1
        for line in f:
            urls.append((line.strip(), f'{i}.jpg '))
            i += 1

    obj = downloadtools.DownloadTools()
    result = obj.download_media(downloadtools.make_items(urls[:10]), location=".media", fresh_folder=True)
    print(result)
