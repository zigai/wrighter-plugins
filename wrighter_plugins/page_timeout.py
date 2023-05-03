from playwright.sync_api import Page
from wrighter.plugin import Plugin, context


class PageTimeout(Plugin):
    """A plugin that sets the default timeout to a page"""

    def __init__(self, ms: float) -> None:
        self.ms = ms
        super().__init__()

    @context("on", "page")
    def context_on_page(self, page: Page) -> None:
        self.logger.debug(f"Applied {self.ms}ms timeout to {page}")
        page.set_default_timeout(timeout=self.ms)


__all__ = ["PageTimeout"]
