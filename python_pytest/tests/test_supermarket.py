import pytest

from model_objects import Product, SpecialOfferType, ProductUnit
from discount_strategies import PercentageDiscountStrategy
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


def test_ten_percent_discount():
    catalog = FakeCatalog()
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    catalog.add_product(toothbrush, 0.99)
    apples = Product("apples", ProductUnit.KILO)
    catalog.add_product(apples, 1.99)

    teller = Teller(catalog)
    
    teller.add_special_offer(PercentageDiscountStrategy(toothbrush, 10.0))

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 1)

    receipt = teller.checks_out_articles_from(cart)

    assert 0.891 == pytest.approx(receipt.total_price(), 0.01)
    assert [] != receipt.discounts
    assert 1 == len(receipt.items)
    receipt_item = receipt.items[0]
    assert toothbrush == receipt_item.product
    assert 0.99 == receipt_item.price
    assert 1 * 0.99 == pytest.approx(receipt_item.total_price, 0.01)
    assert 1 == receipt_item.quantity
