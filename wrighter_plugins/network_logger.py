from os import get_terminal_size

from stdl.fs import bytes_readable
from stdl.str_u import BG, FG, ST, colored, terminal_link
from wrighter.plugin import Plugin, Request, Response, page

HTTP_STATUS_COLORS = {"2": BG.GREEN, "3": BG.BLUE, "4": BG.RED, "5": BG.YELLOW}


def get_terminal_width():
    try:
        length = get_terminal_size().columns
    except OSError:  # OSError: [Errno 25] Inappropriate ioctl for device
        length = 80
    return length


def colorize_status(code: int, status_text: str | None = None) -> str:
    code_str = str(code)
    if not code_str:
        return "unknown"
    value = code_str + (" " + status_text if status_text else "")
    return colored(value, HTTP_STATUS_COLORS.get(code_str[0], FG.WHITE))


def get_status(status_code: int, status_text: str | None = None):
    return str(status_code) + (" " + status_text if status_text else "")


def get_body_info(response) -> str:
    try:
        body = response.body()
    except:
        body = ""
    lenght = len(body)
    return bytes_readable(lenght) if body else "No body"


def clip_str(value: str, max_len: int):
    if len(value) + 6 < max_len:
        return value
    return value[:max_len] + "..."


class NetworkLogger(Plugin):
    """A plugin that logs network events such as responses and requests."""

    indicator_response = "<< |"
    indicator_request = ">> |"

    def __init__(
        self,
        response_codes: list[int] | None = None,
        requests: bool = False,
        tablefmt: str = "plain",
    ) -> None:
        """
        Args:
            response_codes (list[int], optional): A list of HTTP status codes to log. If not provided, all status codes will be logged.
            requests (bool, optional): Whether to log requests. Defaults to `False`.
            theme (dict, optional): A dictionary of colors to use for the log messages.
        """
        self.response_codes = response_codes or list(range(100, 600))
        self.requests = requests
        self.tablefmt = tablefmt
        super().__init__()

    def _get_url(self, url: str, max_len: int, min_len: int = 10):
        if max_len < min_len:
            return "\n" + terminal_link(url, color=FG.LIGHT_BLUE)
        return terminal_link(url, label=clip_str(url, max_len), color=FG.LIGHT_BLUE)

    @page("on", "response")
    def page_on_response(self, response: Response) -> None:
        if response.status not in self.response_codes:
            return

        status = get_status(response.status, response.status_text).ljust(6)
        body_info = get_body_info(response).ljust(9)

        current_len = len(status) + len(self.indicator_response) + len(body_info)
        max_url_len = get_terminal_width() - current_len - 16

        data = [
            colored(self.indicator_response, style=ST.BOLD),
            colored(status, HTTP_STATUS_COLORS.get(str(response.status)[0], FG.WHITE)),
            colored(body_info, color=FG.BLACK, background=BG.WHITE),
            self._get_url(response.url, max_url_len),
        ]
        print(*data, sep="  ")

    @page("on", "request")
    def page_on_request(self, request: Request) -> None:
        if not self.requests:
            return
        method = request.method.ljust(6)
        current_len = len(method) + len(self.indicator_request)
        max_url_len = get_terminal_width() - current_len - 16

        data = [
            colored(self.indicator_request, style=ST.BOLD),
            colored(method, style=ST.BOLD, background=BG.WHITE, color=FG.BLACK),
            self._get_url(request.url, max_url_len),
        ]
        print(*data, sep="  ")


__all__ = ["NetworkLogger"]
