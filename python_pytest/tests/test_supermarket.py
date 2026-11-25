import pytest

from discount_strategies import PercentageDiscountStrategy
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
    """Oferta na escova, cliente leva só maçã: nenhum desconto é aplicado."""
    catalog, toothbrush, apples = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

    cart = ShoppingCart()
    cart.add_item_quantity(apples, quantidade)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(total_esperado, abs=0.001)
    assert receipt.discounts == []
    assert len(receipt.items) == 1
    receipt_item = receipt.items[0]
    assert receipt_item.product == apples
    assert receipt_item.price == 1.99
    assert receipt_item.total_price == pytest.approx(quantidade * 1.99, abs=0.001)
    assert receipt_item.quantity == quantidade


def test_ten_percent_discount_on_offered_product(catalogo_preenchido):
    """A estratégia também pode ser registrada diretamente no Teller."""
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(PercentageDiscountStrategy(toothbrush, 10.0))

    cart = ShoppingCart()
    cart.add_item_quantity(toothbrush, 1)

    receipt = teller.checks_out_articles_from(cart)

    assert receipt.total_price() == pytest.approx(0.891, abs=0.001)
    assert len(receipt.discounts) == 1
