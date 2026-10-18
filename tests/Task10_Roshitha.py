import re
import pytest
from playwright.async_api import async_playwright, expect

PRODUCT = "Atomic Habits"


# Reusable helper function to search
async def search_product(page):
    await page.goto("https://www.amazon.in/")
    await page.locator("//input[@id='twotabsearchtextbox']").fill("Atomic Habits")
    await page.locator("//*[@id='nav-search-submit-button']").click()


# Helper to reliably target organic (non-sponsored) product cards
def get_organic_product_card(page):
    cards = page.locator("div[data-component-type='s-search-result']")
    return (
        cards
        .filter(has_text=PRODUCT)
        .filter(has_not=page.locator("[aria-label*='Sponsored']"))
        .filter(has_not_text="Sponsored")
        .first
    )


@pytest.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path="/usr/bin/google-chrome",slow_mo=500)

        page = await browser.new_page()
        yield page
        await browser.close()


# Test 1: Search for the product
@pytest.mark.asyncio
async def test_product_search(page):
    await search_product(page)

    results = page.locator(
        "div[data-component-type='s-search-result']"
    )
    await expect(results.first).to_be_visible(timeout=10000)


# Test 2: Find the correct product card
@pytest.mark.asyncio
async def test_correct_product_card(page):
    await search_product(page)

    product_card = get_organic_product_card(page)

    await expect(product_card).to_be_visible(timeout=10000)
    await expect(product_card.locator("h2")).to_contain_text(PRODUCT)


# Test 3: Check the product link
@pytest.mark.asyncio
async def test_product_link(page):
    await search_product(page)

    product_card = get_organic_product_card(page)
    product_link = product_card.locator("a[href*='/dp/']").first

    await expect(product_link).to_be_visible(timeout=10000)
    await expect(product_link).to_have_attribute("href", re.compile(r"/dp/"))


# Test 4: Open the product details
@pytest.mark.asyncio
async def test_product_details(page):
    await search_product(page)

    product_card = get_organic_product_card(page)
    product_link = product_card.locator("a[href*='/dp/']").first

    async with page.expect_popup() as popup_info:
        await product_link.click()

    detail_page = await popup_info.value

    try:
        await expect(detail_page.locator("#productTitle")).to_contain_text(
            PRODUCT, timeout=15000
        )
    finally:
        await detail_page.close()