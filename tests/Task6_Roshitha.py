import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_manage_state_across_pages():
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000
        )

        try:
            # Create a browser context to track multiple pages/tabs
            context = await browser.new_context()
            page = await context.new_page()

            # Step 1: Open Amazon
            await page.goto(
                "https://www.amazon.in/",
                wait_until="domcontentloaded"
            )

            # Step 2: Search for a product
            search_box = page.locator("#twotabsearchtextbox")
            await search_box.fill("headphones")
            await page.locator("#nav-search-submit-button").click()

            # Step 3: Wait for search results
            product_cards = page.locator(
                '[data-component-type="s-search-result"]'
            )

            await product_cards.first.wait_for(
                state="visible",
                timeout=20000
            )

            # Step 4: Select the first product with a title
            product = page.locator('//a[@class="a-link-normal s-line-clamp-3 s-link-style a-text-normal"]').first

            await expect(product).to_be_visible(timeout=15000)

            # Capture product title before navigation
            selected_title = " ".join(
                (await product.inner_text()).split()
            )

            print("Selected Product:", selected_title)

            # Step 5: Open product detail page (handling new tab)
            async with context.expect_event("page") as new_page_info:
                await product.click()

            detail_page = await new_page_info.value
            await detail_page.wait_for_load_state("domcontentloaded")

            # Target the visible span tag specifically to avoid strict mode violation
            product_title = detail_page.locator("span#productTitle")
            await expect(product_title).to_be_visible(timeout=20000)

            detail_title = " ".join(
                (await product_title.inner_text()).split()
            )

            # Validate product state after navigation
            assert selected_title.casefold() in detail_title.casefold() or (
                    detail_title.casefold() in selected_title.casefold()
            ), (
                f"Product title changed unexpectedly.\n"
                f"Search title: {selected_title}\n"
                f"Detail title: {detail_title}"
            )

            print("PASS: Product title retained on detail page")

            # Step 6: Add product to cart
            add_to_cart = detail_page.locator("#add-to-cart-button")

            if await add_to_cart.count() == 0 or not await add_to_cart.is_visible():
                pytest.skip(
                    "Add to Cart is unavailable for this product."
                )

            await add_to_cart.click()

            # Step 7: Open cart
            await detail_page.locator("#nav-cart").click()

            # Step 8: Verify the same product is in the cart
            cart_items = detail_page.locator(".sc-list-item")

            await cart_items.first.wait_for(
                state="visible",
                timeout=20000
            )

            matching_item = cart_items.filter(
                has_text=detail_title
            ).first

            assert await matching_item.count() > 0, (
                f"Selected product was not found in cart.\n"
                f"Product: {detail_title}"
            )

            print("PASS: Same product found in cart")

            # Step 9: Return to search results
            await page.bring_to_front()
            await expect(search_box).to_be_visible(timeout=15000)

            # Step 10: Verify the search context is retained
            retained_search = await search_box.input_value()

            assert retained_search.strip().casefold() == "headphones", (
                f"Search context was lost.\n"
                f"Expected: headphones\n"
                f"Actual: {retained_search}"
            )

            print("PASS: Search context retained:", retained_search)

        finally:
            await browser.close()
