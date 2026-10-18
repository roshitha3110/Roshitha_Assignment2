
#Home Page Validations (Soft Assertions)

from playwright.async_api import async_playwright


async def test_home_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, executable_path="/usr/bin/google-chrome",slow_mo=10000)

        page = await browser.new_page()
        await page.goto("https://www.amazon.in/")

        failures = []

        # 1. Page title
        try:
            assert "Amazon" in await page.title()
            print("PASS: Page title validated")
        except AssertionError:
            print("FAIL: Page title validation failed")
            failures.append("Page title")

        # 2. Amazon logo
        try:

            assert await page.locator("//*[@id='nav-logo-sprites']").is_visible()
            print("PASS: Amazon logo is visible")
        except AssertionError:
            print("FAIL: Amazon logo is not visible")
            failures.append("Amazon logo")

        # 3. Search textbox
        try:
            assert await page.locator("//input[@id='twotabsearchtextbox']").is_visible()
            print("PASS: Search textbox is visible")
        except AssertionError:
            print("FAIL: Search textbox is not visible")
            failures.append("Search textbox")

        # 4. Search button
        try:
            assert await page.locator("//*[@id='nav-search-submit-button']").is_visible()
            print("PASS: Search button is visible")
        except AssertionError:
            print("FAIL: Search button is not visible")
            failures.append("Search button")

        # 5. Navigation item
        try:
            assert await page.get_by_role("link", name="Today's Deals").is_visible()
            print("PASS: Navigation item is visible")
        except AssertionError:
            print("FAIL: Navigation item is not visible")
            failures.append("Navigation item")

        # Final result
        print("\\n========== FINAL RESULT ==========")

        if failures:
            print("FAILED: Some validations did not pass.")
            print("Failed validations:", ", ".join(failures))
            await page.screenshot(path="failure.png",full_page=True)
            print("Screenshot saved as failure.png")
        else:
            print("SUCCESS: All 5 validations passed!")

        print("==================================")

        await browser.close()

