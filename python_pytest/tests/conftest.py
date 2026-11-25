import pytest
from model_objects import Product, ProductUnit
from tests.fake_catalog import FakeCatalog   
@pytest.fixture
def catalogo_preenchido():
    catalog = FakeCatalog()
    toothbrush = Product("toothbrush", ProductUnit.EACH)
    catalog.add_product(toothbrush, 0.99)
    apples = Product("apples", ProductUnit.KILO)
    catalog.add_product(apples, 1.99)
    return catalog, toothbrush, apples
