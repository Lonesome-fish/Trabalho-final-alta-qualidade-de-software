import pytest

from model_objects import SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller


@pytest.mark.parametrize(
    "quantidade, valor_por_par, total_esperado",
    [
        (1, 1.50, 0.99),
        (2, 1.50, 1.50),
        (3, 1.50, 2.49),
        (4, 1.50, 3.00),
        (5, 1.50, 3.99),
    ],
)
def test_two_for_amount(
    catalogo_preenchido, quantidade, valor_por_par, total_esperado
):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.TWO_FOR_AMOUNT, toothbrush, valor_por_par
    )

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, quantidade)

    receipt = teller.checks_out_articles_from(cart)

    assert total_esperado == pytest.approx(receipt.total_price(), 0.0001)
