from catalog import SupermarketCatalog
from model_objects import Product, ProductUnit, SpecialOfferType
from teller import Teller


class CustomCatalogWithoutDict(SupermarketCatalog):
    """Simula um catálogo real (ex.: banco de dados) sem atributo .products."""

    def __init__(self, items):
        self._items = list(items)

    def add_product(self, product, price):
        self._items.append((product, price))

    def unit_price(self, product):
        for item, price in self._items:
            if item == product:
                return price
        raise KeyError(product.name)

    def product_with_name(self, name):
        for item, _ in self._items:
            if item.name == name:
                return item
        return None


def test_teller_adds_special_offer(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, 0.0)

    assert len(teller.offers) == 1
    assert toothbrush in teller.offers


def test_teller_finds_product_by_name(catalogo_preenchido):
    catalog, toothbrush, _ = catalogo_preenchido
    teller = Teller(catalog)

    assert teller.product_with_name("toothbrush") == toothbrush
    assert teller.product_with_name("produto_inexistente") is None


def test_teller_works_with_any_catalog_implementation():
    apple = Product("maçã", ProductUnit.KILO)
    custom_catalog = CustomCatalogWithoutDict([(apple, 4.50)])
    teller = Teller(custom_catalog)

    assert teller.product_with_name("maçã") == apple
    assert teller.product_with_name("banana") is None