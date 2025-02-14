from playwright.async_api import Page
from playwright_stealth import Stealth
from wrighter.plugin import Plugin, context


class StealthAsync(Plugin):
    """Apply stealth to pages"""

    def __init__(self, stealth_config: Stealth | None = None) -> None:
        self.stealth = stealth_config if stealth_config is not None else Stealth()
        super().__init__()

    @context("on", "page")
    async def context_on_page(self, page: Page) -> None:
        self.logger.debug(f"Applied stealth to {page}")
        await self.stealth.apply_stealth_async(page)


__all__ = ["StealthAsync"]
