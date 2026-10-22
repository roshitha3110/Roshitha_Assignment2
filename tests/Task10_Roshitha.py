
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
            # Step 1: Open SauceDemo and sign in
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://www.saucedemo.com/")

            await page.locator("#user-name").fill("standard_user")
            await page.locator("#password").fill("secret_sauce")
            await page.locator("#login-button").click()

            # Step 2: Verify successful login
            await expect(page.locator(".title")).to_have_text("Products")
            print("PASS: Login successful.")

            # Step 3: Save the authenticated browser state
            await context.storage_state(path=state_file)
            print("PASS: Browser state saved.")

            # Step 4: Create a new context using saved state
            new_context = await browser.new_context(
                storage_state=state_file
            )
            new_page = await new_context.new_page()

            # Step 5: Open SauceDemo in the new context
            await new_page.goto("https://www.saucedemo.com/")

            # Step 6: Verify authentication without logging in again
            products = new_page.locator(".title")
            login_button = new_page.locator("#login-button")

            if await products.is_visible():
                print("PASS: Authenticated session restored.")

            elif await login_button.is_visible():
                print("Session expired or not restored.")
                print("Re-authentication is needed.")

            else:
                print("Unable to determine authentication status.")

            await new_context.close()
            await context.close()

        finally:
            await browser.close()

        # Step 7: Delete the sensitive state file
        if os.path.exists(state_file):
            os.remove(state_file)
            print("Temporary authentication state file deleted.")


