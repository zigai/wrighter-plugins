from playwright.async_api import Page
from playwright_stealth import StealthConfig, stealth_async
from wrighter.plugin import Plugin, context


class StealthAsync(Plugin):
    """Apply stealth to pages"""

    def __init__(self, stealth_config: StealthConfig | None = None) -> None:
        self.stealth_config = stealth_config if stealth_config is not None else StealthConfig()
        super().__init__()

    @context("on", "page")
    async def context_on_page(self, page: Page) -> None:
        self.logger.debug(f"Applied stealth to {page}")
        await stealth_async(page, config=self.stealth_config)


__all__ = ["StealthAsync"]
