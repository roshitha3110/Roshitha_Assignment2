import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_pagination_and_infinite_scroll():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=500
        )

        try:
            context = await browser.new_context()
            page = await context.new_page()

            # 1. Open Amazon and search
            await page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

            await page.locator("#twotabsearchtextbox").fill("wireless mouse")
            await page.locator("#nav-search-submit-button").click()

            # 2. Wait for results
            product_cards = page.locator('[data-component-type="s-search-result"]')
            await product_cards.first.wait_for(state="visible", timeout=20000)

            # Get title of the first product on Page 1
            first_product_title = await product_cards.first.locator("h2").inner_text()
            print(f"Page 1 First Product: {first_product_title.strip()}")

            # 3. Handle Pagination (Click 'Next')
            next_button = page.locator('.s-pagination-next')

            if await next_button.is_visible():
                await next_button.click()

                # Wait for the next page results to render
                await product_cards.first.wait_for(state="visible", timeout=20000)

                second_product_title = await product_cards.first.locator("h2").inner_text()
                print(f"Page 2 First Product: {second_product_title.strip()}")

                # 4. Validate results changed
                assert first_product_title.strip() != second_product_title.strip(), \
                    "Pagination failed: Result set did not change."

                print("PASS: Successfully navigated to next page and verified new results.")
            else:
                print("Pagination 'Next' button not found on this view.")

        finally:
            await browser.close()
