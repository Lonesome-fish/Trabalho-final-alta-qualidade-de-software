from teller import Teller
from model_objects import SpecialOfferType
def test_teller_adds_special_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    assert len(teller.special_offers) == 1
    assert teller.special_offers[0].product == toothbrush
    assert teller.special_offers[0].offer_type == SpecialOfferType.THREE_FOR_TWO