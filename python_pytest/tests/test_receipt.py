import pytest

from model_objects import Discount, SpecialOfferType
from receipt import Receipt
from shopping_cart import ShoppingCart
from teller import Teller


def test_empty_receipt_has_zero_total():
    receipt = Receipt()

    assert receipt.total_price() == 0
    assert receipt.items == []
    assert receipt.discounts == []


def test_receipt_total_sums_multiple_items(catalogo_preenchido):
    _, toothbrush, apples = catalogo_preenchido
    receipt = Receipt()
    receipt.add_product(toothbrush, 2, 0.99, 1.98)
    receipt.add_product(apples, 1.5, 1.99, 2.985)

    assert receipt.total_price() == pytest.approx(4.965)


def test_receipt_total_subtracts_discounts(catalogo_preenchido):
    _, toothbrush, apples = catalogo_preenchido
    receipt = Receipt()
    receipt.add_product(toothbrush, 3, 0.99, 2.97)
    receipt.add_discount(Discount(toothbrush, "3 for 2", -0.99))
    receipt.add_discount(Discount(apples, "10% off", -0.20))

    assert receipt.total_price() == pytest.approx(1.78)


def test_items_property_returns_a_copy(catalogo_preenchido):
    _, toothbrush, _ = catalogo_preenchido
    receipt = Receipt()
    receipt.add_product(toothbrush, 1, 0.99, 0.99)
    items = receipt.items

    items.clear()

    assert len(receipt.items) == 1


def test_discounts_property_returns_a_copy(catalogo_preenchido):
    _, toothbrush, _ = catalogo_preenchido
    receipt = Receipt()
    receipt.add_discount(Discount(toothbrush, "3 for 2", -0.99))
    discounts = receipt.discounts

    discounts.clear()

    assert len(receipt.discounts) == 1


def test_receipt_total_with_special_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(1.98, abs=0.0001)