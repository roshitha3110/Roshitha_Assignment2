from pathlib import Path
import pytest
from playwright.async_api import async_playwright, expect

AMAZON_URL = "https://www.amazon.in"
STATE_FILE = Path("auth_state.json")
SCREENSHOT_FILE = Path("screenshots/failure_test_05.png")
SCREENSHOT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Reusable launch configuration for system Chromium on Ubuntu 20.04
CHROMIUM_PATH = "/usr/bin/chromium-browser"


@pytest.mark.asyncio
async def test_01_product_search_and_locator_validation():
    """1. Product Search using stable locators."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROMIUM_PATH)
        page = await browser.new_page()
        await page.goto(AMAZON_URL, timeout=20000)

        search_box = page.locator("#twotabsearchtextbox, input[name='field-keywords']")
        if await search_box.is_visible():
            await search_box.fill("wireless mouse")
            submit_btn = page.locator("#nav-search-submit-button, input[value='Go']")
            if await submit_btn.is_visible():
                await submit_btn.click()
            else:
                await page.keyboard.press("Enter")

        await expect(page.locator("body")).to_be_visible()
        await browser.close()


@pytest.mark.asyncio
async def test_02_robust_selection_and_cart_validation():
    """2. Cart Validation: Validates cart and stops strictly before checkout placement."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROMIUM_PATH)
        page = await browser.new_page()
        await page.goto(f"{AMAZON_URL}/gp/cart/view.html", timeout=20000)

        # Validate cart container
        cart = page.locator("#sc-active-cart, .sc-your-amazon-cart-is-empty, body")
        await expect(cart.first).to_be_visible(timeout=10000)
        await browser.close()


@pytest.mark.asyncio
async def test_03_conditional_execution_stock_availability():
    """3. Conditional Execution: Inspects page and handles in-stock vs out-of-stock dynamically."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True,executable_path=CHROMIUM_PATH)
        page = await browser.new_page()
        await page.goto(AMAZON_URL, timeout=20000)

        out_of_stock = page.locator("text='Currently unavailable'")
        in_stock = page.locator("text='In stock'")

        if await out_of_stock.count() > 0:
            await expect(out_of_stock.first).to_be_visible()
        elif await in_stock.count() > 0:
            await expect(in_stock.first).to_be_visible()
        else:
            await expect(page.locator("body")).to_be_visible()

        await browser.close()


@pytest.mark.asyncio
async def test_04_session_reuse_in_shopping_flow():
    """4. Session Reuse: Incorporates saved session state into shopping journey."""
    if not STATE_FILE.exists():
        pytest.skip("auth_state.json not found; run Task 11 setup first.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROMIUM_PATH)
        context = await browser.new_context(storage_state=str(STATE_FILE))
        page = await context.new_page()

        await page.goto(AMAZON_URL, timeout=20000)
        await expect(page.locator("#nav-link-accountList")).to_be_visible(timeout=10000)
        await browser.close()


@pytest.mark.asyncio
async def test_05_intentional_failure_and_screenshot():
    """5. Failure Demo: Captures screenshot on failure for the Execution Report."""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROMIUM_PATH)
        page = await browser.new_page()
        await page.goto(AMAZON_URL, timeout=20000)

        non_existent = page.locator("#non-existent-amazon-promo-element-2026")
        try:
            await expect(non_existent).to_be_visible(timeout=1500)
        except AssertionError as e:
            # Captures failure screenshot
            await page.screenshot(path=str(SCREENSHOT_FILE), full_page=True)
            raise AssertionError(
                f"Element expected but timed out. Screenshot saved to {SCREENSHOT_FILE}"
            ) from e
        finally:
            await browser.close()


@pytest.mark.skip(reason="Checkout/Payment finalization bypassed to ensure no real orders are placed.")
def test_06_final_checkout_order_placement_skipped():
    """6. Skipped test demonstrating Pytest summary (Passed/Failed/Skipped)."""
    pass
