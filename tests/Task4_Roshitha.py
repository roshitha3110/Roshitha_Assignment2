import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_product_details():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=500,
        )
        page = await browser.new_page()

        # Open Amazon and search
        await page.goto("https://www.amazon.in/")
        await page.locator("//input[@id='twotabsearchtextbox']").fill("books")
        await page.locator("//*[@id='nav-search-submit-button']").click()

        # First organic result's title link
        product = page.locator(
            'div[data-component-type="s-search-result"]:not(:has-text("Sponsored")) '
            'div[data-cy="title-recipe"] a'
        ).first
        await expect(product).to_be_visible(timeout=15000)

        # Remove target="_blank" so the link opens in the same tab
        await product.evaluate("el => el.removeAttribute('target')")
        await product.click()
        await page.wait_for_load_state("domcontentloaded")

        # Verify the product title on the detail page
        title = page.locator("#productTitle")
        await expect(title).to_be_visible(timeout=15000)
        print(await title.inner_text())

        await browser.close()