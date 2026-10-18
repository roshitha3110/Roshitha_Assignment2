
import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page:
            import os
            os.makedirs("screenshots", exist_ok=True)

            page.screenshot(
                path=f"screenshots/{item.name}.png",
                full_page=True
            )
