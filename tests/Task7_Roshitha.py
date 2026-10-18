

from playwright.async_api import async_playwright, TimeoutError


async def test_dynamic_dropdown():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome"
        )

        page = await browser.new_page()
        await page.goto("https://www.amazon.in/")

        # Enter a partial product name

        search = page.locator("//input[@id='twotabsearchtextbox']")
        await search.fill("headphone")

        try:
            # Wait for autocomplete suggestions
            suggestions = page.locator(
                '//*[@id="sac-suggestion-row-1-cell-1"]/div[1]'
            )

            await suggestions.first.wait_for(
                state="visible",
                timeout=3000
            )

            print("Autocomplete suggestions appeared.")

            # Select the first visible suggestion
            suggestion_text = (
                await suggestions.first.inner_text()
            ).strip()

            print("Selected suggestion:", suggestion_text)
            await suggestions.first.click()

            # Validate navigation to the selected suggestion's results
            await page.wait_for_load_state("domcontentloaded")
            print("Page URL:", page.url)

        except TimeoutError:
            print("No autocomplete suggestions appeared.")
            print("Using normal search as a fallback.")

            await search.fill("headphone")
            await search.press("Enter")

            # Wait for normal search results
            await page.locator(
                "[data-component-type='s-search-result']"
            ).first.wait_for(
                state="visible",
                timeout=10000
            )

            print("Normal search results are displayed.")
            print("Page URL:", page.url)

        await browser.close()


