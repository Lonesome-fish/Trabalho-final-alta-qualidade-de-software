from model_objects import SpecialOfferType
from teller import Teller


def test_teller_adds_special_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    assert len(teller.offers) == 1
    assert toothbrush in teller.offers