from .DownloadToolsItem import DownloadToolsItem


class SpecialCaseUrl:
    """
    SpecialCaseUrl is used to handle special cases with urls. For example, if you want to process an url to a gallery to
    individual image urls, change the initially given filename, or change the location of the file. You can also use
    this class to stop processing of an url.
    """

    def check_url(self, url: str, filename: str | None, location: str | None) -> list[DownloadToolsItem] | None:
        """
        Check if an url is a special case url.

        :param url: The url to check
        :param filename: The filename of the url
        :param location: The location of the url
        :return: if matched, return data in INPUT_TYPE, and location, else return None. Note. if you don't want to
            expand further on this search then return empty list.
        """
        ...
