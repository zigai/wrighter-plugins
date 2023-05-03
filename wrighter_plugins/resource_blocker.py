from playwright.sync_api import Page, Route
from wrighter.plugin import Plugin, context

DEFAULT_RESOURCE_EXCLUSIONS = ["image", "stylesheet", "media", "font", "other"]


class ResourceBlocker(Plugin):
    """
    A plugin that blocks requests with specified resource types.
    """

    def __init__(
        self,
        url_pattern: str = "**/*",
        blocked_resources: list[str] = DEFAULT_RESOURCE_EXCLUSIONS,
        verbose: bool = False,
    ) -> None:
        self.url_pattern = url_pattern
        self.blocked_resoruces = blocked_resources
        self.verbose = verbose

        super().__init__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url_pattern={self.url_pattern}, blocked_resources={self.blocked_resoruces})"

    def handler(self, route: Route):
        if route.request.resource_type in self.blocked_resoruces:
            self.logger.info(f"BLOCKED {route.request.url}")
            return route.abort()
        return route.continue_()

    @context("on", "page")
    def context_on_page(self, page: Page) -> None:
        page.route(url=self.url_pattern, handler=self.handler)


__all__ = ["DEFAULT_RESOURCE_EXCLUSIONS", "ResourceBlocker"]
