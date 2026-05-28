# downloadtools

Package for downloading media from urls.

## Table of Contents

<!-- TOC -->
* [DownloadTools](#downloadtools)
  * [Table of Contents](#table-of-contents)
    * [Documentation](#documentation)
      * [Available Attributes](#available-attributes)
        * [`special_case_urls`](#special_case_urls)
        * [`head_check`](#head_check)
        * [`follow_redirects`](#follow_redirects)
        * [`size_limit`](#size_limit)
        * [`file_overwrite`](#file_overwrite)
        * [`threads`](#threads)
        * [`fresh_folder`](#fresh_folder)
        * [`disable_tqdm`](#disable_tqdm)
      * [Downloading Method](#downloading-method)
      * [`DownloadToolsItem`](#downloadtoolsitem)
      * [`make_items`](#make_items)
      * [About `SpecialCaseUrl`s](#about-specialcaseurls)
      * [Exceptions](#exceptions)
<!-- TOC -->

### Documentation

#### Available Attributes

```python
import downloadtools

# basic usage
download_tools = downloadtools.DownloadTools()
```

##### `special_case_urls`

This is a list of `SpecialCaseUrl` objects. These objects are used to check if the url is a special case or not.

```python
import downloadtools

download_tools = downloadtools.DownloadTools(special_case_urls=[...])
```

##### `head_check`

This is used to send a HEADER request to verify the media type and size of the file. If the file is not of the specified
type or size, then it does not send the full request.

```python
import downloadtools

download_tools = downloadtools.DownloadTools(head_check=True)
```

##### `follow_redirects`

This is used to allow redirects while sending requests. sets `httpx` `follow_redirects` parameter.

##### `size_limit`

This is used to set the size limit of the file to be downloaded.

##### `file_overwrite`

This is used to set if the file should be overwritten if it already exists. example if `01.jpg` already exists and
`file_overwrite` is set to `False`, then the file will be saved as `01 (2).jpg`

##### `threads`

This is used to set of threads that need to be spanned for download media.

##### `fresh_folder`

If True, the main location will be cleared before downloading.

##### `disable_tqdm`

If True, tqdm progress bar will not be shown.

#### Downloading Method

```python
import downloadtools

downloadToolsItems = [...]

download_tools = downloadtools.DownloadTools()
download_tools.download_media(items=downloadToolsItems)
```

`download_media` has all the parameters of `DownloadTools` class. If a parameter is passed to `download_media`, then it
will override the value of the same parameter in `DownloadTools` class. In addition to it `download_media` has the
following parameters

- `items` - list of `DownloadToolsItem` to be downloaded
- `location` - main location where the files will be saved

#### `DownloadToolsItem`

This a `pydantic.dataclass`. Contains the following attributes

- `url` (`str`): url to be called
- `filename` (`Optional[FileName]`): filename for the media which is downloaded
- `location` (`Optional[Location]`): location relative to the main folder where the downloaded media has to be stored
- `disable_special_check` (`bool`): if `SpecialCaseUrl` check has to be disabled for this item

#### `make_items`

This helps to convert old `INPUT_TYPE` to new `DownloadToolsItem`. These are the input formats valid for this
conversion.

1. `str` - single url
2. tuple of (url, file_name)
3. tuple of (url, file_name | None, relative_location)
4. tuple of (url, file_name | None, relative_location | None, special_case_url_check)
5. list of the above

#### About `SpecialCaseUrl`s

SpecialCaseUrl is used to handle special cases with urls. For example, if you want to process an url of a gallery to
individual image urls, change the initially given filename, or change the location of the file. You can also use
this class to stop processing of an url.

```python
import downloadtools


class GalleyCheck(downloadtools.SpecialCaseUrl):

  def check_url(self, url: str, filename: str | None, location: str | None) -> ...:
    # this galley url map to a list of image urls
    image_items = [...]
    return image_items
```

#### Exceptions

- `DownloadToolsError` - base exception for this package
- `NoMedia` - no media found at the url
- `FileNameNone` - program failed to come up with a filename
- `ExceedsContentSize` - content size exceeds the size limit
