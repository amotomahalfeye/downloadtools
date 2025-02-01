import pathlib
import shutil

from downloadtools import DownloadTools, FileNameNone


def test_filename_content_disposition():
    content_disposition = "attachment; filename=\"test_filename_content_disposition.jpg\""

    filename = DownloadTools()._extract_filename_content_disposition(content_disposition)
    assert filename == ("test_filename_content_disposition", "jpg")


def test_filename_content_disposition_no_filename():
    content_disposition = "attachment;"

    filename = DownloadTools()._extract_filename_content_disposition(content_disposition)
    assert filename == (None, None)


def test_extract_filename_from_url():
    url = "https://www.example.com/test_filename_from_url.jpg"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == ("test_filename_from_url", "jpg")


def test_filename_from_url_no_filename():
    url = "https://www.example.com/"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == (None, None)


def test_filename_from_url_no_extension():
    url = "https://www.example.com/test_filename_from_url"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == (None, None)


def test_filename_from_url_with_query():
    url = "https://www.example.com/test_filename_from_url.jpg?query=1"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == ("test_filename_from_url", "jpg")


def test_filename_from_url_with_fragment():
    url = "https://www.example.com/test_filename_from_url.jpg#fragment"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == ("test_filename_from_url", "jpg")


def test_filename_from_url_with_query_and_fragment():
    url = "https://www.example.com/test_filename_from_url.jpg?query=1#fragment"

    filename = DownloadTools()._extract_filename_url(url)
    assert filename == ("test_filename_from_url", "jpg")


def test_filename_from_user():
    filename = "test_filename_from_user.jpg"

    filename = DownloadTools()._extract_filename_user(filename)
    assert filename == ("test_filename_from_user", "jpg")


def test_filename_from_user_no_extension():
    filename = "test_filename_from_user"

    filename = DownloadTools()._extract_filename_user(filename)
    assert filename == ("test_filename_from_user", None)


def test_filetype_from_content_type():
    content_type = "image/jpeg"

    filetype = DownloadTools()._extract_filetype_content_type(content_type)
    assert filetype == "jpeg"


def test_filetype_from_content_type_video():
    content_type = "video/mp4; codecs=\"avc1.42E01E, mp4a.40.2\""

    filetype = DownloadTools()._extract_filetype_content_type(content_type)
    assert filetype == "mp4"


def test_get_filename_1():
    user_filename = "test_get_filename_1.jpg"

    url = "https://www.example.com/test_get_filename_1.jpg"

    filename = DownloadTools()._get_filename(url, user_filename=user_filename)
    assert filename == ("test_get_filename_1", "jpg")


def test_get_filename_2():
    user_filename = "test_get_filename_2"

    content_disposition = "attachment; filename=\"test_get_filename_2.jpeg\""
    url = "https://www.example.com/test_get_filename_2.jpg"

    filename = DownloadTools()._get_filename(url, content_disposition=content_disposition,
                                             user_filename=user_filename)
    assert filename == ("test_get_filename_2", "jpeg")


def test_get_filename_3():
    user_filename = "test_get_filename_3"

    url = "https://www.example.com/test_get_filename_3.jpg"

    filename = DownloadTools()._get_filename(url, user_filename=user_filename)
    assert filename == ("test_get_filename_3", "jpg")


def test_get_filename_4():
    user_filename = "test_get_filename_4"

    content_type = "image/jpeg"
    url = "https://www.example.com/"

    filename = DownloadTools()._get_filename(url, content_type=content_type, user_filename=user_filename)
    assert filename == ("test_get_filename_4", "jpeg")


def test_get_filename_5():
    content_disposition = "attachment; filename=\"test_get_filename_5.jpg\""
    url = "https://www.example.com/"

    filename = DownloadTools()._get_filename(url, content_disposition=content_disposition)
    assert filename == ("test_get_filename_5", "jpg")


def test_get_filename_6():
    url = "https://www.example.com/test_get_filename_6.jpg"

    filename = DownloadTools()._get_filename(url)
    assert filename == ("test_get_filename_6", "jpg")


def test_get_filename_7():
    url = "https://www.example.com/"

    try:
        DownloadTools()._get_filename(url)
    except FileNameNone:
        return
    raise AssertionError("FileNameNone error not raised")


def clean_up():
    location = pathlib.Path("example.jpg")
    if location.exists():
        if location.is_file():
            location.unlink()
        else:
            shutil.rmtree(location)


def test_resolve_filename_1():
    """
    Env conditions:
    - file `example.jpg` exists in the current directory
    - file_overwrite is False

    Expected:
    - file `example.jpg` is untouched
    - filename is `example (1).jpg`
    """
    clean_up()
    location = pathlib.Path("example.jpg")
    location.touch()
    filename = DownloadTools()._resolve_filename("example", "jpg", pathlib.Path("."), file_overwrite=False)
    assert filename == "example (2).jpg"
    assert location.exists()
    clean_up()


def test_resolve_filename_2():
    """
    Env conditions:
    - file `example.jpg` exists in the current directory
    - file_overwrite is True

    Expected:
    - file `example.jpg` is untouched
    - filename is `example.jpg`
    """
    clean_up()
    location = pathlib.Path("example.jpg")
    location.touch()
    filename = DownloadTools()._resolve_filename("example", "jpg", pathlib.Path("."), file_overwrite=True)
    assert filename == "example.jpg"
    assert location.exists()
    clean_up()


def test_resolve_filename_3():
    """
    Env conditions:
    - folder `example.jpg` exists in the current directory
    - file_overwrite is False

    Expected:
    - folder `example.jpg` is untouched
    - filename is `example (1).jpg`
    """
    clean_up()
    location = pathlib.Path("example.jpg")
    location.mkdir()
    filename = DownloadTools()._resolve_filename("example", "jpg", pathlib.Path("."), file_overwrite=False)
    assert filename == "example (2).jpg"
    assert location.exists()
    clean_up()


def test_resolve_filename_4():
    """
    Env conditions:
    - folder `example.jpg` exists in the current directory
    - file_overwrite is True

    Expected:
    - folder `example.jpg` is deleted
    - filename is `example.jpg`
    """
    clean_up()
    location = pathlib.Path("example.jpg")
    location.mkdir()
    filename = DownloadTools()._resolve_filename("example", "jpg", pathlib.Path("."), file_overwrite=True)
    assert filename == "example.jpg"
    assert not location.exists()
    clean_up()


def test_resolve_filename_5():
    """
    Env conditions:
    - file `example.jpg` does not exist in the current directory

    Expected:
    - filename is `example.jpg`
    """
    clean_up()
    filename = DownloadTools()._resolve_filename("example", "jpg", pathlib.Path("."), file_overwrite=False)
    assert filename == "example.jpg"
    clean_up()
