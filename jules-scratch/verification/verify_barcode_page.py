from playwright.sync_api import sync_playwright, Page, expect

def run_verification(page: Page):
    """
    This script verifies the "View Barcode" page.
    """

    # Set a higher timeout for navigation
    page.set_default_navigation_timeout(10000) # 10 seconds

    # 1. Add test data
    page.goto("http://localhost:8080/setup-test-data/")

    # 2. Go to the item list page
    page.goto("http://localhost:8080/")
    expect(page.locator("h1")).to_have_text("Item List")

    # 3. Click the "View Barcode" link for the first item
    page.locator("a:text('View Barcode')").first.click()
    expect(page.locator("h1")).to_have_text("Barcode for: Milk")

    # 4. Check for the svg element
    barcode_element = page.locator("#barcode")
    expect(barcode_element).to_be_visible()

    # 5. Take a screenshot
    page.screenshot(path="jules-scratch/verification/barcode_page.png")

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
