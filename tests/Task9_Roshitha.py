
import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_product_availability():

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=500
        )

        page = await browser.new_page()

        try:
            # Open Amazon India
            await page.goto("https://www.amazon.in/")

            # Search for a product
            search_box = page.locator("#twotabsearchtextbox")
            await search_box.fill("headphones")
            await search_box.press("Enter")

            # Wait for search results
            products = page.locator(
                'div[data-component-type="s-search-result"]'
            )
            await expect(products.first).to_be_visible()

            # Select the first product
            await products.first.click()
            await page.wait_for_load_state("domcontentloaded")

            # Check Add to Cart button
            add_to_cart = page.locator("#add-to-cart-button")

            if await add_to_cart.count() > 0 and await add_to_cart.is_visible() and await add_to_cart.is_enabled():

                print("Product appears available")

                await add_to_cart.click()
                print("PASS: Add to Cart clicked")

                # Validate cart
                await page.goto("https://www.amazon.in/gp/cart/view.html")

                await expect(page.locator("#sc-active-cart")).to_be_visible()
                print("PASS: Cart page opened")

            else:
                print("Product unavailable: Add to Cart button missing or disabled")
                print("SKIPPED: Cart validation")

        finally:
            await browser.close()
