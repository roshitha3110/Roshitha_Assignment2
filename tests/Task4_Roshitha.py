import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_checkout_journey():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=1000
        )

        page = await browser.new_page()

        # Step 1: Open Amazon
        await page.goto(
            "https://www.amazon.in/",
            wait_until="domcontentloaded"
        )

        # Step 2: Search for books
        await page.locator("#twotabsearchtextbox").fill("books")
        await page.locator("#nav-search-submit-button").click()

        # Step 3: Wait for products
        products = page.locator(".s-result-item.s-asin")
        await products.first.wait_for(state="visible", timeout=20000)

        # Step 4: Find the first product link
        product = page.locator('//a[@class="a-link-normal s-line-clamp-3 s-link-style a-text-normal"]').first

        await expect(product).to_be_visible(timeout=15000)

        # Get the product URL
        product_url = await product.get_attribute("href")

        assert product_url, "FAIL: Product URL not found"

        # Convert relative URL into a full URL
        if product_url.startswith("/"):
            product_url = "https://www.amazon.in" + product_url

        # Open the product
        await page.goto(
            product_url,
            wait_until="domcontentloaded"
        )

        # Step 5: Validate product title
        title = page.locator("#productTitle")
        await expect(title).to_be_visible(timeout=20000)

        product_name = (await title.inner_text()).strip()
        print("PASS: Product title:", product_name)

        # Step 6: Check Add to Cart
        add_to_cart = page.locator("#add-to-cart-button")

        if await add_to_cart.count() > 0 and await add_to_cart.is_visible():

            print("PASS: Add to Cart is available")

            # Step 7: Add the book to cart
            await add_to_cart.click()

            # Step 8: Open the cart
            await page.locator("#nav-cart").click()

            # Step 9: Validate cart items
            cart_items = page.locator(".sc-list-item")
            await cart_items.first.wait_for(state="visible", timeout=20000)

            matching_book = cart_items.filter(has_text=product_name).first
            await expect(matching_book).to_be_visible()

            print("PASS: Book found in cart")

            # Step 10: Check quantity using both locator types
            quantity = matching_book.locator("select")

            if await quantity.count() > 0:
                print("Cart quantity:", await quantity.first.input_value())

            else:
                quantity = matching_book.locator("span.a-dropdown-prompt")

                if await quantity.count() > 0:
                    print(
                        "Cart quantity:",
                        (await quantity.first.inner_text()).strip()
                    )
                else:
                    print("INFO: Quantity control not found")

            # Step 11: Proceed to checkout, but do not place the order
            checkout = page.locator(
                'input[name="proceedToRetailCheckout"]'
            )

            if await checkout.count() > 0 and await checkout.first.is_visible():
                await checkout.first.click()

                print("PASS: Proceeded to checkout")
                print("STOP: Do not place the order or submit payment.")

            else:
                print("INFO: Checkout button is unavailable")

        else:
            print("INFO: Add to Cart is unavailable for this book")

        # Step 12: Close browser
        await browser.close()
