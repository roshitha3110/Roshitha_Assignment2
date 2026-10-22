
import os
import pytest
from playwright.async_api import async_playwright, expect


@pytest.mark.asyncio
async def test_global_authentication():

    state_file = "auth_state.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome",
            slow_mo=500
        )

        try:
            # Step 1: Open SauceDemo and log in
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(
                "https://www.saucedemo.com/",
                wait_until="domcontentloaded"
            )

            await page.locator("#user-name").fill("standard_user")
            await page.locator("#password").fill("secret_sauce")
            await page.locator("#login-button").click()

            # Step 2: Verify successful login
            await expect(page.locator(".title")).to_have_text("Products")
            print("PASS: Login successful.")

            # Step 3: Save authenticated browser state
            await context.storage_state(path=state_file)
            print("PASS: Browser state saved.")

            # Step 4: Create a new context using saved state
            new_context = await browser.new_context(
                storage_state=state_file
            )
            new_page = await new_context.new_page()

            # Step 5: Open SauceDemo with the saved state
            await new_page.goto(
                "https://www.saucedemo.com/",
                wait_until="domcontentloaded"
            )

            # Step 6: Check whether authentication persists
            products = new_page.locator(".title")
            login_button = new_page.locator("#login-button")

            if await products.is_visible():
                print("PASS: Authenticated session restored.")
            elif await login_button.is_visible():
                print("Session expired. Re-authentication is needed.")
            else:
                print("Unable to determine authentication status.")

            await new_context.close()
            await context.close()

        finally:
            await browser.close()

    # Step 7: Remove the sensitive state file after testing
    if os.path.exists(state_file):
        os.remove(state_file)
        print("Temporary authentication state file deleted.")

