import pytest
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_product_discovery():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000,
        )
        page = await browser.new_page()

        await page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

        keyword = "Atomic Habits"
        await page.locator("#twotabsearchtextbox").fill(keyword)
        await page.locator("#nav-search-submit-button").click()

        # Each result title is a link wrapping an h2
        titles = page.locator('div[data-cy="title-recipe"] a:has(h2)')
        await titles.first.wait_for(timeout=30000)

        product_title = "Atomic Habits"
        found = False

        for i in range(await titles.count()):
            link = titles.nth(i)
            text = (await link.locator("h2").inner_text()).strip()
            print("Available Product:", text)

            if product_title.lower() in text.lower():
                print("Selected Product:", text)
                await link.click()
                found = True
                break

        assert found, f"'{product_title}' not found in search results"

        await browser.close()
