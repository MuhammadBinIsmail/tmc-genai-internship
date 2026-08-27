# Day 16 - Web Scraping: scraper.py

import csv
import json
import time
import requests
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser

BASE_URL = "https://scrapeme.live/shop/"
USER_AGENT = "Mozilla/5.0 (compatible; TMC-Internship-Scraper/1.0)"
REQUEST_DELAY = 1.5  # seconds between requests, to scrape politely

def is_scraping_allowed(base_url):
    """Check robots.txt before scraping, to respect the site's rules."""
    rp = RobotFileParser()
    rp.set_url(base_url.rstrip("/") + "/robots.txt")
    rp.read()
    return rp.can_fetch(USER_AGENT, base_url)

def fetch_page(url):
    """Fetch a page and return parsed HTML, or None if the request fails."""
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch {url} (status {response.status_code})")
        return None

    return BeautifulSoup(response.text, "html.parser")

def parse_products(soup):
    """Extract product name, price, and URL from a listing page."""
    products = []
    items = soup.select("li.product")

    for item in items:
        name_tag = item.select_one("h2")
        price_tag = item.select_one("span.price")
        link_tag = item.select_one("a.woocommerce-LoopProduct-link")

        name = name_tag.get_text(strip=True) if name_tag else None
        price = price_tag.get_text(strip=True) if price_tag else None
        url = link_tag["href"] if link_tag else None

        products.append({"name": name, "price": price, "url": url})

    return products

def get_total_pages(soup):
    """Find the last page number from the pagination controls."""
    page_links = soup.select("a.page-numbers")
    page_numbers = [int(a.get_text()) for a in page_links if a.get_text().isdigit()]
    return max(page_numbers) if page_numbers else 1

def scrape_all_products(base_url):
    """Scrape every page of the listing, respecting rate limits."""
    first_page = fetch_page(base_url)
    if first_page is None:
        return []

    total_pages = get_total_pages(first_page)
    print(f"Found {total_pages} page(s) to scrape.")

    all_products = parse_products(first_page)

    for page_num in range(2, total_pages + 1):
        time.sleep(REQUEST_DELAY)
        page_url = f"{base_url}page/{page_num}/"
        soup = fetch_page(page_url)
        if soup:
            all_products.extend(parse_products(soup))
            print(f"Scraped page {page_num}/{total_pages}")

    return all_products

def save_to_csv(products, filename="products.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "url"])
        writer.writeheader()
        writer.writerows(products)
    print(f"Saved {len(products)} products to {filename}")

def save_to_json(products, filename="products.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2)
    print(f"Saved {len(products)} products to {filename}")

def main():
    if not is_scraping_allowed(BASE_URL):
        print("Scraping is disallowed by robots.txt for this URL. Exiting.")
        return

    products = scrape_all_products(BASE_URL)

    if products:
        save_to_csv(products)
        save_to_json(products)
    else:
        print("No products scraped.")

if __name__ == "__main__":
    main()