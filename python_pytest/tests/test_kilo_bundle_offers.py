import pytest

from model_objects import Product, ProductUnit, SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


@pytest.mark.parametrize(
    "quantity,expected_total",
    [
        (2.5, 25.0),  # Abaixo de 3 kg: sem desconto (2,5 * 10,00)
        (3.5, 25.0),  # 3 kg por 20,00 (1 kg grátis) + 0,5 kg cheio (5,00)
        (6.5, 45.0),  # 2 grupos de 3 kg por 40,00 + 0,5 kg cheio (5,00)
    ],
)
def test_three_for_two_kilo_charges_fractional_remainder_at_full_price(quantity, expected_total):
    catalog = FakeCatalog()
    meat = Product("carne", ProductUnit.KILO)
    catalog.add_product(meat, 10.0)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, meat, 0.0)

    cart = ShoppingCart()
    cart.add_item_quantity(meat, quantity)

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == pytest.approx(expected_total)


@pytest.mark.parametrize(
    "quantity,expected_total",
    [
        (1.8, 18.0),  # Abaixo de 2 kg: sem desconto
        (2.5, 20.0),  # 2 kg por 15,00 + 0,5 kg cheio (5,00)
        (3.5, 30.0),  # 2 kg por 15,00 + 1,5 kg cheio (15,00)
    ],
)
def test_two_for_amount_kilo_charges_fractional_remainder_at_full_price(quantity, expected_total):
    catalog = FakeCatalog()
    cheese = Product("queijo", ProductUnit.KILO)
    catalog.add_product(cheese, 10.0)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, cheese, 15.0)

    cart = ShoppingCart()
    cart.add_item_quantity(cheese, quantity)

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == pytest.approx(expected_total)


@pytest.mark.parametrize(
    "quantity,expected_total",
    [
        (4.9, 49.0),  # Abaixo de 5 kg: sem desconto
        (5.5, 45.0),  # 5 kg por 40,00 + 0,5 kg cheio (5,00)
        (10.5, 85.0),  # 2 grupos de 5 kg por 80,00 + 0,5 kg cheio (5,00)
    ],
)
def test_five_for_amount_kilo_charges_fractional_remainder_at_full_price(quantity, expected_total):
    catalog = FakeCatalog()
    potato = Product("batata", ProductUnit.KILO)
    catalog.add_product(potato, 10.0)

    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, potato, 40.0)

    cart = ShoppingCart()
    cart.add_item_quantity(potato, quantity)

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == pytest.approx(expected_total)