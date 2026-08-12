"""
Unit tests for scripts/transform.py.

scrapeme.live doesn't currently have any products on sale, so the
sale-price parsing branch in parse_price() can't be exercised by a
real scrape. These tests feed it synthetic input instead, to confirm
the logic is correct independent of what the live site happens to show.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from transform import parse_price, parse_stock, clean_text


def test_parse_price_single_price():
    current, original = parse_price("£63.00")
    assert current == 63.00
    assert original is None


def test_parse_price_with_sale():
    # WooCommerce glues original + sale price together like this
    # when a product is discounted, e.g. "£100.00£75.00"
    current, original = parse_price("£100.00£75.00")
    assert current == 75.00
    assert original == 100.00


def test_parse_price_missing():
    current, original = parse_price(None)
    assert current is None
    assert original is None


def test_parse_price_no_numbers():
    current, original = parse_price("Price on request")
    assert current is None
    assert original is None


def test_parse_stock_in_stock():
    quantity, in_stock = parse_stock("45 in stock")
    assert quantity == 45
    assert in_stock is True


def test_parse_stock_out_of_stock():
    quantity, in_stock = parse_stock("Out of stock")
    assert quantity == 0
    assert in_stock is False


def test_parse_stock_missing():
    quantity, in_stock = parse_stock(None)
    assert quantity is None
    assert in_stock is None


def test_clean_text_strips_whitespace():
    assert clean_text("  Bulbasaur   \n") == "Bulbasaur"


def test_clean_text_none():
    assert clean_text(None) is None


def test_clean_text_empty_string():
    assert clean_text("   ") is None


if __name__ == "__main__":
    tests = [
        test_parse_price_single_price,
        test_parse_price_with_sale,
        test_parse_price_missing,
        test_parse_price_no_numbers,
        test_parse_stock_in_stock,
        test_parse_stock_out_of_stock,
        test_parse_stock_missing,
        test_clean_text_strips_whitespace,
        test_clean_text_none,
        test_clean_text_empty_string,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__} - {e}")
    print(f"\n{passed}/{len(tests)} tests passed")