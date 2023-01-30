from fnmatch import fnmatch
from json import JSONDecodeError

from jsonpath_ng import jsonpath, parse
from jsonschema import ValidationError, validate
from stdl import fs
from wrighter.plugin import Plugin, Request, Response, page


class JsonScraper(Plugin):
    def __init__(
        self,
        url_pattern: str = "*://*.*/*",
        schema: dict | None = None,
        json_path: str | None = None,
        verbose: bool = False,
    ) -> None:
        self.verbose = verbose
        super().__init__()
        self.url_pattern = url_pattern
        self.schema = schema
        self.jsonpath = parse(json_path) if json_path else None
        self.data = []

    def log(self, text: str):
        if self.verbose:
            print(text)

    def is_schema_valid(self, data: dict):
        if self.schema is None:
            return True
        try:
            validate(data, schema=self.schema)
            return True
        except ValidationError:
            return False

    def process_data(self, data: dict):
        if self.jsonpath is None:
            return data
        return [i.value for i in self.jsonpath.find(data)]

    @page("on", "response")
    def handler(self, response: Response) -> None:
        if not fnmatch(response.url, self.url_pattern):
            return
        try:
            data: dict = response.json()
        except (JSONDecodeError, UnicodeDecodeError):
            return
        if not self.is_schema_valid(data):
            return
        data = self.process_data(data)  # type:ignore
        if data:
            self.log(data)
            self.data.append(data)

    def export_data(self, filepath: str) -> None:
        fs.json_dump(self.data, filepath)


__all__ = ["JsonScraper"]
