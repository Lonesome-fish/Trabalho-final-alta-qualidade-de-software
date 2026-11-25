import pytest

from model_objects import SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller

@pytest.mark.parametrize("quantidadedeitens, valorporpacote, valoresperado", [
    (5, 100.0, 100.0),
    (10, 10.0, 20.0),
    (15, 100.0, 300.0),
    (25, 100.0, 500.0),
    (20, 5.0, 20.0)
])
def test_five_for_amount(catalogo_preenchido, quantidadedeitens, valorporpacote, valoresperado):

    catalog,toothbrush, apples = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, valorporpacote)

    cart = ShoppingCart()

    cart.add_item_quantity(toothbrush, quantidadedeitens)

    receipt = teller.checks_out_articles_from(cart)

    assert valoresperado == pytest.approx(receipt.total_price(), 0.0001)


@pytest.mark.parametrize(
    "quantity, expected_total, expected_discount",
    [
        (4, 3.96, 0),
        (5, 3.00, -1.95),
        (6, 3.99, -1.95),
        (9, 6.96, -1.95),
        (10, 6.00, -3.90),
        (11, 6.99, -3.90),
    ],
)
def test_five_for_amount_boundaries(
    catalogo_preenchido, quantity, expected_total, expected_discount
):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, 3.0
    )
    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, quantity)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(expected_total, abs=0.0001)
    actual_discount = sum(
        discount.discount_amount for discount in receipt.discounts
    )
    assert actual_discount == pytest.approx(expected_discount, abs=0.0001)


def test_five_for_amount_applies_only_to_the_offered_product(catalogo_preenchido):
    catalog, toothbrush, apples = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, 3.0
    )
    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 5)
    cart.add_item_quantity(apples, 1)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(4.99, abs=0.0001)
    assert len(receipt.discounts) == 1
    assert receipt.discounts[0].product == toothbrush
