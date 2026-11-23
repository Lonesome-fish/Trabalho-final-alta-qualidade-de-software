import pytest

from model_objects import SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller


@pytest.mark.parametrize(
    "quantidade, total_esperado",
    [
        (0.5, 0.995),
        (1.0, 1.99),
        (2.5, 4.975),
        (3.0, 5.97),
        (5.0, 9.95),
    ],
)
def test_ten_percent_discount(catalogo_preenchido, quantidade, total_esperado):
    catalog, toothbrush, apples = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(
        SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0
    )

    cart = ShoppingCart()
    cart.add_item_quantity(apples, quantidade)

    receipt = teller.checks_out_articles_from(cart)

    assert total_esperado == pytest.approx(receipt.total_price(), 0.0001)
    assert [] == receipt.discounts
    assert 1 == len(receipt.items)
    receipt_item = receipt.items[0]
    assert apples == receipt_item.product
    assert 1.99 == receipt_item.price
    assert quantidade * 1.99 == pytest.approx(receipt_item.total_price, 0.0001)
    assert quantidade == receipt_item.quantity
