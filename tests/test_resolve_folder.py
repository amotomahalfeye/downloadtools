import pathlib
import shutil

from src.downloadtools import DownloadTools


def cleanup():
    location = pathlib.Path("media")
    if location.exists():
        if location.is_dir():
            shutil.rmtree(location)
        else:
            location.unlink()


def test_resolve_folder_1():
    """
    Env conditions:
    - folder `media` exists
    - folder `media` contains a file `file.txt`
    - fresh_folder is False

    Expected:
    - no changes in the folder
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Create folder `media`
    location.mkdir()

    # Create file `file.txt` in folder `media`
    with open(location / "file.txt", "w") as f:
        f.write("Hello, World!")

    # Resolve folder `media`
    DownloadTools()._resolve_folder(location, fresh_folder=False)

    # Check if the folder is the same
    assert location.is_dir()
    assert (location / "file.txt").is_file()
    with open(location / "file.txt", "r") as f:
        assert f.read() == "Hello, World!"

    # Clean up
    cleanup()


def test_resolve_folder_2():
    """
    Env conditions:
    - folder `media` exists
    - folder `media` contains a file `file.txt`
    - fresh_folder is True

    Expected:
    - folder `media` is empty
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Create folder `media`
    location.mkdir()

    # Create file `file.txt` in folder `media`
    with open(location / "file.txt", "w") as f:
        f.write("Hello, World!")

    # Resolve folder `media`
    DownloadTools()._resolve_folder(location, fresh_folder=True)

    # Check if the folder is empty
    assert location.is_dir()
    assert not (location / "file.txt").exists()

    # Clean up
    cleanup()


def test_resolve_folder_3():
    """
    Env conditions:
    - folder `media` does not exist
    - fresh_folder is False

    Expected:
    - folder `media` is created
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Resolve folder `media`
    DownloadTools()._resolve_folder(location, fresh_folder=False)

    # Check if the folder is created
    assert location.is_dir()

    # Clean up
    cleanup()


def test_resolve_folder_4():
    """
    Env conditions:
    - folder `media` does not exist
    - fresh_folder is True

    Expected:
    - folder `media` is created
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Resolve folder `media`
    DownloadTools()._resolve_folder(location, fresh_folder=True)

    # Check if the folder is created
    assert location.is_dir()

    # Clean up
    cleanup()


def test_resolve_folder_5():
    """
    Env conditions:
    - file `media` exists
    - fresh_folder is False

    Expected:
    - raises NotADirectoryError
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Create file `media`
    with open(location, "w") as f:
        f.write("Hello, World!")

    # Resolve folder `media`
    try:
        DownloadTools()._resolve_folder(location, fresh_folder=False)
    except NotADirectoryError:
        pass
    else:
        assert False, "NotADirectoryError not raised"

    # Clean up
    cleanup()


def test_resolve_folder_6():
    """
    Env conditions:
    - file `media` exists
    - fresh_folder is True

    Expected:
    - folder `media` is created
    """

    # Delete folder/file `media` if exists
    cleanup()

    location = pathlib.Path("media")

    # Create file `media`
    with open(location, "w") as f:
        f.write("Hello, World!")

    # Resolve folder `media`
    DownloadTools()._resolve_folder(location, fresh_folder=True)

    # Check if the folder is created
    assert location.is_dir()

    # Clean up
    cleanup()
