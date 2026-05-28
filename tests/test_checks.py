from downloadtools import DownloadTools, NotMedia, ExceedsContentSize


def test_filetype_from_content_type_video():
    content_type = "video/mp4"
    DownloadTools()._check_media(content_type)
    assert True


def test_filetype_from_content_type_image():
    content_type = "image/jpeg"
    DownloadTools()._check_media(content_type)
    assert True


def test_filetype_from_content_type_none():
    content_type = None
    try:
        DownloadTools()._check_media(content_type)
    except NotMedia:
        assert True


def test_filetype_from_content_type_text():
    content_type = "text/html"
    try:
        DownloadTools()._check_media(content_type)
    except NotMedia:
        assert True


def test_filetype_from_content_type_image_size():
    content_length = "100"
    DownloadTools()._check_size(1000, content_length)
    assert True


def test_filetype_from_content_type_image_size_exceeds():
    content_length = "1000"
    try:
        DownloadTools()._check_size(100, content_length)
    except ExceedsContentSize:
        assert True
