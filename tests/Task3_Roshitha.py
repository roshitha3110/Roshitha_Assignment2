#Built-in Waits and Page Load States
import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_product_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, executable_path="/usr/bin/google-chrome",slow_mo=10000)

        page = await browser.new_page()

        # Open Amazon and wait for the page to load
        await page.goto("https://www.amazon.in/")

        # Search for books
        await page.locator("//input[@id='twotabsearchtextbox']").fill("books")
        await page.locator("//*[@id='nav-search-submit-button']").click()

        # Wait for the results area
        results = page.locator(
            "div[data-component-type='s-search-result']"
        )
        await expect(results.first).to_be_visible(timeout=15000)

        # Wait for the first product title
        titles = page.locator(
            '//div[@data-cy="title-recipe"]//h2/span'
        )
        await expect(titles.first).to_be_visible(timeout=15000)

        # Validate that at least one result is displayed
        count = await titles.count()
        assert count > 0, "No product results found"

        print("Total product titles:", count)
        print("First product:", await titles.first.inner_text())

        await browser.close()
