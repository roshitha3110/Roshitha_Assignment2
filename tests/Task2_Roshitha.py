#Multiple Locators: First, Last, and Indexed Selection

from playwright.async_api import async_playwright


async def test_product_search():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, executable_path="/usr/bin/google-chrome", slow_mo=10000)

        page = await browser.new_page()
        await page.goto("https://www.amazon.in/")

        # Search for books
        await page.locator("//input[@id='twotabsearchtextbox']").fill("books")
        await page.locator("//*[@id='nav-search-submit-button']").click()

        # Get all product titles
        titles = page.locator('//div[@data-cy="title-recipe"]//h2/span')

        # Wait for search results
        await page.wait_for_load_state("domcontentloaded")
        await titles.first.wait_for(state="attached", timeout=15000)

        # Get all titles
        all_titles = await titles.all_inner_texts()
        print("All Product Titles:", all_titles)

        # Count products
        count = await titles.count()
        print("Total Products:", count)

        # First product
        print("First Product:", await titles.first.inner_text())

        # Last product
        print("Last Product:", await titles.last.inner_text())

        # Third product
        if count >= 3:
            print("Third Product:", await titles.nth(2).inner_text())

        # Open the first product
        await titles.first.click()