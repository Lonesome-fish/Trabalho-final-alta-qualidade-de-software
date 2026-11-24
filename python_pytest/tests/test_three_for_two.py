import pytest

from model_objects import SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller


@pytest.mark.parametrize(
    "quantidade, total_esperado",
    [
        (1, 0.99),
        (2, 1.98),
        (3, 1.98),
        (4, 2.97),
        (6, 3.96),
    ],
)
def test_three_for_two(catalogo_preenchido, quantidade, total_esperado):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, quantidade)

    receipt = teller.checks_out_articles_from(cart)

    assert total_esperado == pytest.approx(receipt.total_price(), 0.0001)
