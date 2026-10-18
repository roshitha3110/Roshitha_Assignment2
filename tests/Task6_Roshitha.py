#Static Dropdowns and Selected-Option Validation


from playwright.async_api import async_playwright, expect


async def test_static_dropdown():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="/usr/bin/google-chrome"
        )

        page = await browser.new_page()

        await page.goto(
            "https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_select"
        )

        # The dropdown is inside the example iframe
        frame = page.frame_locator("#iframeResult")
        dropdown = frame.locator("select")

        # Select an option by its visible label
        await dropdown.select_option(label="Opel")

        # Validate the selected option
        selected_value = await dropdown.locator(
            "option:checked"
        ).text_content()

        assert selected_value == "Opel"

        print("Selected option:", selected_value)
        print("Dropdown selection validated successfully.")

        await browser.close()


