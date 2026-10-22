
import json
from pathlib import Path

import pytest
from playwright.async_api import async_playwright, expect


# SauceDemo website
SAUCE_URL = "https://www.saucedemo.com/"

# Demo login credentials
USERNAME = "standard_user"
PASSWORD = "secret_sauce"

# File to save browser session information
STATE_FILE = Path("auth_state.json")

# File for testing an empty session
EXPIRED_STATE_FILE = Path("expired_state.json")

# Chrome executable path on Ubuntu
CHROMIUM_PATH = "/usr/bin/google-chrome"


# TASK 1: Login and save browser state
@pytest.mark.asyncio
async def test_01_save_browser_state():

    # Start Playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path=CHROMIUM_PATH)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(SAUCE_URL)

        await page.locator("#user-name").fill(USERNAME)
        await page.locator("#password").fill(PASSWORD)
        await page.locator("#login-button").click()

        await expect(page).to_have_url( "https://www.saucedemo.com/inventory.html")

        # Verify that the Products page is visible
        await expect(page.locator(".title")).to_have_text("Products")

        # Save cookies and local storage to a JSON file
        await context.storage_state(path=str(STATE_FILE))
        print("PASS: Login successful and browser state saved.")
        await browser.close()

    # Confirm that the state file was created
    assert STATE_FILE.exists()

    # Confirm that the file contains data
    assert STATE_FILE.stat().st_size > 0


# TASK 2: Load saved state into a new browser context
@pytest.mark.asyncio
async def test_02_load_saved_state():

    # Check whether Task 1 created the state file
    assert STATE_FILE.exists(), "Run Task 1 first."
  
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path=CHROMIUM_PATH)

        # Create a new context using the saved state
        context = await browser.new_context(storage_state=str(STATE_FILE))
        page = await context.new_page()
        await page.goto("https://www.saucedemo.com/inventory.html")

        # Verify that the authenticated Products page opens
        # SauceDemo stores its login state in browser-side storage
        await expect(page.locator(".title")).to_have_text("Products")

        # Verify that the product list is displayed
        await expect(page.locator(".inventory_list")).to_be_visible()
        print("PASS: Saved browser state loaded successfully.")
        await browser.close()


# TASK 3: Reuse saved state in another browser run
@pytest.mark.asyncio
async def test_03_reuse_saved_state():

    # Confirm that the saved state file exists
    assert STATE_FILE.exists(), "Run Task 1 first."

   
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path=CHROMIUM_PATH)

        # Load the same saved state into a new context
        context = await browser.new_context(storage_state=str(STATE_FILE))
        page = await context.new_page()
        await page.goto("https://www.saucedemo.com/inventory.html")

        # Verify that the session still allows access to Products
        await expect(page.locator(".title")).to_have_text("Products")

        print("PASS: Saved state reused in another browser run.")

        # Close the browser
        await browser.close()


# TASK 4: Handle a missing state file
@pytest.mark.asyncio
async def test_04_missing_state_file():

    # Define a state file that does not exist
    missing_file = Path("missing_auth_state.json")

    # Delete it first if it already exists
    if missing_file.exists():
        missing_file.unlink()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, executable_path=CHROMIUM_PATH)
        
        # Verify that loading a missing state file raises an error
        with pytest.raises(FileNotFoundError):

            # Attempt to create a context with the missing file
            await browser.new_context(
                storage_state=str(missing_file)
            )

        print("PASS: Missing state file handled correctly.")

        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(SAUCE_URL)
        
        await expect(page.locator("#login-button")).to_be_visible()
        print("PASS: Fresh login page opened without saved state.")
        await browser.close()


# TASK 5: Test an empty session state file
@pytest.mark.asyncio
async def test_05_expired_state_file():

    # Create empty browser storage data
    # This represents missing session data, not a real expired session
    empty_data = {
        "cookies": [],
        "origins": []
    }

    # Save the empty data as a JSON file
    EXPIRED_STATE_FILE.write_text(
        json.dumps(empty_data),
        encoding="utf-8"
    )

    # Start Playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False,executable_path=CHROMIUM_PATH)

        # Create a context using the empty state file
        context = await browser.new_context(storage_state=str(EXPIRED_STATE_FILE))

        page = await context.new_page()
        await page.goto("https://www.saucedemo.com/inventory.html")
        await expect(page).to_have_url(SAUCE_URL)
        await expect( page.locator("#login-button")).to_be_visible()
        print("PASS: Empty session redirected to the login page.")

        await browser.close()

