# End-to-End Product Search and Cart Validation

import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_product_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000
        )

        page = await browser.new_page()
        page.set_default_timeout(15000)

        try:
            # 1. Open Amazon
            await page.goto("https://www.amazon.in/")

            # 2. Search for books
            await page.locator(
                "//input[@id='twotabsearchtextbox']"
            ).fill("books")

            await page.locator(
                "//*[@id='nav-search-submit-button']"
            ).click()

            # 3. Get all product titles
            titles = page.locator(
                '//div[@data-cy="title-recipe"]//h2/span'
            )

            await page.wait_for_load_state("domcontentloaded")
            await titles.first.wait_for(
                state="visible", timeout=15000
            )

            print("Product search results displayed.")

            # 4. Select the first product title
            product_title = (await titles.first.inner_text()).strip()
            print("Selected product:", product_title)

            # Find the link for the selected product
            title_link = page.locator(
                '//div[@data-cy="title-recipe"]//h2'
            ).first.locator("xpath=ancestor::a")

            # 5. Open the product page
            async with page.context.expect_page(timeout=5000) as new_page:
                try:
                    await title_link.click()
                except Exception:
                    pass

            try:
                product_page = await new_page.value
            except Exception:
                product_page = page

            await product_page.wait_for_load_state("domcontentloaded")

            # 6. Validate product title
            detail_title = product_page.locator("#productTitle")
            await expect(detail_title).to_be_visible(timeout=15000)

            print(
                "Product details:",
                (await detail_title.inner_text()).strip()
            )

            # 7. Check Add to Cart availability
            add_to_cart = product_page.locator("#add-to-cart-button")

            if (
                await add_to_cart.is_visible()
                and await add_to_cart.is_enabled()
            ):
                # Get cart count before adding
                cart_count = product_page.locator("#nav-cart-count")
                before_text = await cart_count.inner_text()
                before_count = int(before_text.strip() or "0")

                # 8. Add product to cart
                await add_to_cart.click()
                print("Add to Cart clicked.")

                # 9. Verify cart count increased
                await expect(cart_count).not_to_have_text(
                    str(before_count), timeout=15000
                )

                after_count = await cart_count.inner_text()
                print("Cart count before:", before_count)
                print("Cart count after:", after_count)
                print("Cart verification completed.")

            else:
                print(
                    "Add to Cart is unavailable. "
                    "Skipping cart validation."
                )

            # Do not proceed to checkout or payment.

        finally:
            await browser.close()

