import json
from fnmatch import fnmatch
from json import JSONDecodeError

from jsonpath_ng import parse
from jsonschema import ValidationError, validate
from stdl import fs
from stdl.fs import bytes_readable
from wrighter.plugin import Plugin, Response, page


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
        self.data: list[dict] = []

    def is_schema_valid(self, data: dict) -> bool:
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
        except Exception as e:
            self.logger.debug(
                "Unknown exception occured while parsing response as JSON", exception=e
            )
            return

        if not self.is_schema_valid(data):
            self.logger.debug(f"JSON response from '{response.url}' doesn't match provided schema")
            return
        json_data = self.process_data(data)  # type:ignore
        if json_data:
            self.logger.info(
                f"Extracted data from '{response.url}'", size=bytes_readable(len(json.dumps(data)))
            )
            data = {"data": json_data, "url": response.url}
            self.data.append(data)

    def export_data(self, filepath: str) -> None:
        self.logger.info(f"Exporting extracted data to '{filepath}'")
        fs.json_dump(self.data, filepath)


__all__ = ["JsonScraper"]
