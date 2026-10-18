#Robust Locator Challenge
import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_robust_product_locator():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000,
        )
        # Create context to track multi-page navigation cleanly
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto("https://www.amazon.in/")

            product_name = "Atomic Habits"
            await page.locator("//input[@id='twotabsearchtextbox']").fill("Atomic Habits")
            await page.locator("//*[@id='nav-search-submit-button']").click()


            cards = page.locator("div[data-component-type='s-search-result']")

            matching_cards = (
                cards
                .filter(has=page.locator("h2", has_text=product_name))
                .filter(has_not=page.locator("[aria-label*='Sponsored']"))
                .filter(has_not_text="Sponsored")
            )
            await expect(matching_cards.first).to_be_visible(timeout=15000)

            product_card = matching_cards.first

            # Assert the title
            product_title = product_card.locator("h2").first
            await expect(product_title).to_contain_text(product_name)

            product_link = product_card.locator("a[href*='/dp/']").first
            await expect(product_link).to_be_visible(timeout=15000)

            # Catch the new tab when clicking
            async with page.expect_popup() as popup_info:
                await product_link.click()

            detail_page = await popup_info.value
            await detail_page.wait_for_load_state()

            # Verify title on the new page
            await expect(detail_page.locator("#productTitle")).to_contain_text(
                "Atomic Habits", timeout=15000
            )

        finally:
            await browser.close()