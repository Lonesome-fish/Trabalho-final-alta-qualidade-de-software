from teller import Teller
from model_objects import SpecialOfferType
from discount_strategies import ComboDiscountStrategy, DiscountCalculator
def test_teller_adds_special_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    assert len(teller.offers) == 1
    assert teller.offers[toothbrush].product == toothbrush
    assert teller.offers[toothbrush].offer_type == SpecialOfferType.THREE_FOR_TWO