from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    This script verifies the new Bootstrap UI on all main pages.
    """

    # Set a higher timeout for navigation
    page.set_default_navigation_timeout(10000) # 10 seconds

    # 1. Add test data
    page.goto("http://localhost:8080/setup-test-data/")

    # 2. Go to the item list page
    page.goto("http://localhost:8080/")
    expect(page.locator("h1")).to_have_text("Item List")
    page.screenshot(path="jules-scratch/verification/item_list_bootstrap.png")

    # 3. Go to the Add Item page
    page.goto("http://localhost:8080/add/")
    expect(page.locator("h1")).to_have_text("Add New Item")
    page.screenshot(path="jules-scratch/verification/add_item_bootstrap.png")

    # 4. Go to the Expiring Soon page
    page.goto("http://localhost:8080/expiring-soon/")
    expect(page.locator("h1")).to_have_text("Items Expiring Soon")
    page.screenshot(path="jules-scratch/verification/expiring_soon_bootstrap.png")

    # 5. Go to the Search page
    page.goto("http://localhost:8080/search/")
    expect(page.locator("h1")).to_have_text("Search by UPC")
    page.screenshot(path="jules-scratch/verification/search_bootstrap.png")

    # 6. Go to the Subscribe page
    page.goto("http://localhost:8080/subscribe/")
    expect(page.locator("h1")).to_have_text("Subscribe to Reminders")
    page.screenshot(path="jules-scratch/verification/subscribe_bootstrap.png")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        run_verification(page)
    except Exception as e:
        print(f"Verification failed: {e}")
        page.screenshot(path="jules-scratch/verification/error.png")
    finally:
        browser.close()
