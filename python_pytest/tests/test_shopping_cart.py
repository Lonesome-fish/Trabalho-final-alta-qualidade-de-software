
import pytest

from model_objects import SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller


@pytest.mark.parametrize(
    "quantidadedeitens, valorporpacote, valoresperado",
    [
        (5, 100.0, 100.0),
        (10, 10.0, 20.0),
        (15, 100.0, 300.0),
        (25, 100.0, 500.0),
        (20, 5.0, 20.0),
    ],
)
def test_shopping_cart_total(
    catalogo_preenchido, quantidadedeitens, valorporpacote, valoresperado
):
    catalog, toothbrush, apples = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, valorporpacote
    )

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, quantidadedeitens)

    assert cart.product_quantities[toothbrush] == quantidadedeitens
    assert apples not in cart.product_quantities

    receipt = teller.checks_out_articles_from(cart)
    assert receipt.total_price() == pytest.approx(valoresperado, abs=0.0001)


def test_new_shopping_cart_is_empty():
    cart = ShoppingCart()

    assert cart.items == []
    assert cart.product_quantities == {}


def test_add_item_adds_one_unit(catalogo_preenchido):
    _, toothbrush, _ = catalogo_preenchido
    cart = ShoppingCart()

    cart.add_item(toothbrush)

    assert cart.product_quantities[toothbrush] == 1.0
    assert len(cart.items) == 1
    assert cart.items[0].product == toothbrush
    assert cart.items[0].quantity == 1.0


def test_repeated_additions_accumulate_quantity(catalogo_preenchido):
    _, toothbrush, _ = catalogo_preenchido
    cart = ShoppingCart()

    cart.add_item(toothbrush)
    cart.add_item_quantity(toothbrush, 2)

    assert cart.product_quantities[toothbrush] == 3.0
    assert [item.quantity for item in cart.items] == [1.0, 2]


def test_different_products_have_independent_quantities(catalogo_preenchido):
    _, toothbrush, apples = catalogo_preenchido
    cart = ShoppingCart()

    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(apples, 1.5)

    assert cart.product_quantities == {toothbrush: 2, apples: 1.5}
    assert [(item.product, item.quantity) for item in cart.items] == [
        (toothbrush, 2),
        (apples, 1.5),
    ]


def test_fractional_quantities_accumulate(catalogo_preenchido):
    _, _, apples = catalogo_preenchido
    cart = ShoppingCart()

    cart.add_item_quantity(apples, 0.5)
    cart.add_item_quantity(apples, 1.25)

    assert cart.product_quantities[apples] == pytest.approx(1.75)


def test_checkout_without_offers_totals_multiple_products(catalogo_preenchido):
    catalog, toothbrush, apples = catalogo_preenchido
    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(apples, 1.5)

    receipt = Teller(catalog).checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(4.965)
    assert [(item.product, item.quantity) for item in receipt.items] == [
        (toothbrush, 2),
        (apples, 1.5),
    ]
    assert receipt.discounts == []


def test_checkout_accumulates_separate_additions_for_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.FIVE_FOR_AMOUNT, toothbrush, 3.0
    )
    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 2)
    cart.add_item_quantity(toothbrush, 3)

    receipt = teller.checks_out_articles_from(cart)

    assert cart.product_quantities[toothbrush] == 5
    assert receipt.total_price() == pytest.approx(3.0)
    assert len(receipt.discounts) == 1