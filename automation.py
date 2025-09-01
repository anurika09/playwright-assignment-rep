import json
import os
from playwright.sync_api import sync_playwright

SESSION_FILE = "session.json"
BASE_URL = "https://hiring.idenhq.com/"
EMAIL = "anurikamoudgalya@gmail.com"
PASSWORD = "UqWJ9cXJ"
OUTPUT_FILE = "products.json"


def save_session(context):
    storage = context.storage_state()
    with open(SESSION_FILE, "w") as f:
        json.dump(storage, f)


def load_session(p):
    if os.path.exists(SESSION_FILE):
        return p.chromium.launch(headless=False).new_context(storage_state=SESSION_FILE)
    else:
        return p.chromium.launch(headless=False).new_context()


def main():
    with sync_playwright() as p:
        context = load_session(p)
        page = context.new_page()

        print(" Opening site")
        page.goto(BASE_URL)

        if page.is_visible('input[type="email"]'):
            print(" Logging in")
            page.fill('input[type="email"]', EMAIL)
            page.fill('input[type="password"]', PASSWORD)
            page.click('button:has-text("Sign in")')
            page.wait_for_load_state("networkidle")
            save_session(context)

        if page.is_visible('button:has-text("Launch Challenge")'):
            print("Launching challenge")
            page.click('button:has-text("Launch Challenge")')
            page.wait_for_load_state("networkidle")

        print(" Expanding accordions")
        page.click('text=Dashboard Tools')
        page.click('text=Open Data Visualization')
        page.click('text=Data Visualization')
        page.click('text=Open Inventory Management')
        page.click('text=Inventory Management')

        print(" Opening product inventory")
        view_btn = page.locator('text=View Product Inventory')
        view_btn.click()
        view_btn.dblclick()

        print(" Waiting for product cards")
        page.wait_for_selector("div:has-text('Updated')", timeout=60000)

        # Scrape product cards
        products = []
        cards = page.query_selector_all("div:has-text('Updated')")
        for card in cards:
            text = card.inner_text().strip().split("\n")

            product = {
                "id": text[0] if len(text) > 0 else "",
                "name": text[1] if len(text) > 1 else "",
                "category": text[2] if len(text) > 2 else "",
                "details": text[3] if len(text) > 3 else "",
                "shade": text[4] if len(text) > 4 else "",
                "composition": text[5] if len(text) > 5 else "",
                "updated": [t for t in text if "Updated" in t][-1] if any("Updated" in t for t in text) else "",
            }
            products.append(product)

        # Save pretty JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(products, f, indent=4, ensure_ascii=False)

        print(f"\n Extracted {len(products)} products → {OUTPUT_FILE}")

        print("\n Preview:")
        for prod in products[:5]:
            print(prod)

        context.close()


if __name__ == "__main__":
    main()
