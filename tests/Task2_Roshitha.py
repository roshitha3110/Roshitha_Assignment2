import pytest
import asyncio
from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_dynamic_product_selection():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000
        )

        page = await browser.new_page()

        # Open Amazon India
        await page.goto("https://www.amazon.in/", wait_until="domcontentloaded")

        # Search for a product
        search_box = page.locator("#twotabsearchtextbox")
        await search_box.fill("headphones")
        await search_box.press("Enter")

        # Wait for product cards to appear
        product_cards = page.locator(
            'div[data-component-type="s-search-result"]'
        )
        await product_cards.first.wait_for(state="visible", timeout=15000)

        # Find a product by its name or keyword
        required_keyword = "headphones"
        matching_card = None

        for i in range(await product_cards.count()):

            card = product_cards.nth(i)

            # Get the title only from this card
            title = card.locator("h2 span").first

            if await title.count() > 0:
                product_name = (await title.inner_text()).strip()

                if required_keyword.lower() in product_name.lower():
                    matching_card = card
                    print("PASS: Matching product found:", product_name)
                    break

        # Fail clearly if no matching product is found
        assert matching_card is not None, (
            f"FAIL: No product found with keyword '{required_keyword}'"
        )

        # Validate the title inside the matched card
        matched_title = matching_card.locator("h2 span").first
        assert await matched_title.is_visible(), (
            "FAIL: Matching product title is not visible"
        )

        print("PASS: Product title is visible")

        # Interact only within the matched product card
        add_to_cart = matching_card.get_by_role(
            "button", name="Add to cart"
        )

        if await add_to_cart.count() > 0 and await add_to_cart.first.is_visible():
            await add_to_cart.first.click()
            print("PASS: Add to Cart clicked for the matching product")
        else:
            # Amazon may not show Add to Cart in search results.
            # Open the matched product instead.
            product_link = matching_card.locator("h2 a").first

            assert await product_link.count() > 0, (
                "FAIL: No Add to Cart button or product link in matched card"
            )

            await product_link.click()
            print("PASS: Opened the matching product")

        await page.wait_for_timeout(2000)

        await browser.close()
