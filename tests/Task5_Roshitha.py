# Timeout Handling and Custom Wait Conditions
import asyncio
from playwright.async_api import async_playwright, TimeoutError


async def test_timeout_handling():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path="/usr/bin/google-chrome")

        page = await browser.new_page()

        # Set the default action timeout to 5 seconds
        page.set_default_timeout(5000)

        await page.goto("https://www.saucedemo.com/")

        # Wait for a valid element using a custom timeout
        try:
            await page.locator("#login-button").wait_for(
                state="visible",
                timeout=3000
            )
            print("Login button is visible.")

        except TimeoutError:
            print("Timeout: Login button was not visible within 3 seconds.")

        # Wait for an element that does not exist
        try:
            await page.locator("#non-existent").wait_for(
                state="visible",
                timeout=2000
            )
            print("Element is visible.")

        except TimeoutError:
            print("Timeout occurred: Element not found within 2 seconds.")

        await browser.close()


asyncio.run(test_timeout_handling())