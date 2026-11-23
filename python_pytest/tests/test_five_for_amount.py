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
