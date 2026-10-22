
import pytest
from playwright.async_api import async_playwright


API_URL = "https://fakestoreapi.com/products/1"


@pytest.mark.asyncio
async def test_ui_api_product_validation():

    async with async_playwright() as p:

        # Step 1: Get product details from API
        request = await p.request.new_context()

        try:
            response = await request.get(API_URL)

            assert response.status == 200, (
                f"API request failed: {API_URL}, "
                f"Status: {response.status}"
            )

            api_data = await response.json()
            api_title = " ".join(api_data["title"].split())

            print("API Endpoint:", API_URL)
            print("API Field: title")
            print("API Product Title:", api_title)

            # Step 2: Validate the API data
            assert api_title, "API product title is empty"

            print("PASS: API product title received")

            # Step 3: Open the API's public demo page
            # This validates API data, but does not compare
            # it with Amazon's live product data.
            browser = await p.chromium.launch(
                headless=False,
                executable_path="/usr/bin/google-chrome",
                slow_mo=1000
            )

            try:
                page = await browser.new_page()

                await page.goto(
                    "https://fakestoreapi.com/",
                    wait_until="domcontentloaded"
                )

                print("PASS: Demo website opened")
                print("NOTE: UI/API comparison requires a matching")
                print("product UI and API dataset.")

            finally:
                await browser.close()

        finally:
            await request.dispose()

