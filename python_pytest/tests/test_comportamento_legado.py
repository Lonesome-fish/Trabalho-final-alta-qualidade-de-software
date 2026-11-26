"""
Testes de caracterização (golden master).

Comparam o sistema refatorado com o comportamento do legado. Se algum falhar,
uma mudança alterou um comportamento existente.
"""
import pytest

from model_objects import Product, ProductUnit, SpecialOfferType
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog
from tests.legacy_oracle import legacy_discounts
from tests.receipt_printer import ReceiptPrinter


def _montar_catalogo():
    catalog = FakeCatalog()
    produtos = {
        "toothbrush": Product("toothbrush", ProductUnit.EACH),
        "apples": Product("apples", ProductUnit.KILO),
        "rice": Product("rice", ProductUnit.EACH),
        "toothpaste": Product("toothpaste", ProductUnit.EACH),
    }
    catalog.add_product(produtos["toothbrush"], 0.99)
    catalog.add_product(produtos["apples"], 1.99)
    catalog.add_product(produtos["rice"], 2.49)
    catalog.add_product(produtos["toothpaste"], 1.79)
    return catalog, produtos


# --- 1. Recibo impresso completo, caractere por caractere ---

RECIBO_ESPERADO = (
    "toothbrush                          3.96\n"
    "  0.99 * 4\n"
    "apples                              2.98\n"
    "  1.99 * 1.500\n"
    "rice                                7.47\n"
    "  2.49 * 3\n"
    "toothpaste                         10.74\n"
    "  1.79 * 6\n"
    "toothbrush                          0.99\n"
    "3 for 2 (toothbrush)               -0.99\n"
    "20.0% off (apples)                 -0.60\n"
    "2 for 4.0 (rice)                   -0.98\n"
    "5 for 7.49 (toothpaste)            -1.46\n"
    "\n"
    "Total:                             22.12\n"
)


def test_recibo_impresso_com_todas_as_ofertas_e_identico_ao_legado():
    catalog, p = _montar_catalogo()
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, p["toothbrush"], 0.0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, p["apples"], 20.0)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, p["rice"], 4.0)
    teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, p["toothpaste"], 7.49)

    cart = ShoppingCart()
    cart.add_item_quantity(p["toothbrush"], 4)
    cart.add_item_quantity(p["apples"], 1.5)
    cart.add_item_quantity(p["rice"], 3)
    cart.add_item_quantity(p["toothpaste"], 6)
    cart.add_item(p["toothbrush"])  # segunda adição do mesmo produto

    receipt = teller.checks_out_articles_from(cart)

    assert ReceiptPrinter().print_receipt(receipt) == RECIBO_ESPERADO


# --- 2. Comparação em massa com o oráculo do legado ---

OFERTAS = [
    (SpecialOfferType.THREE_FOR_TWO, 0.0),
    (SpecialOfferType.TEN_PERCENT_DISCOUNT, 10.0),
    (SpecialOfferType.TEN_PERCENT_DISCOUNT, 25.0),
    (SpecialOfferType.TWO_FOR_AMOUNT, 1.50),
    (SpecialOfferType.TWO_FOR_AMOUNT, 4.00),
    (SpecialOfferType.FIVE_FOR_AMOUNT, 3.00),
    (SpecialOfferType.FIVE_FOR_AMOUNT, 100.0),  # "oferta" mais cara que o preço normal
]

CASOS = (
    [("toothbrush", q) for q in [1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 15]]          # por unidade
    + [("apples", q) for q in [0.5, 1, 1.5, 2, 2.7, 3, 3.5, 4, 5, 6, 10.5]]    # por kg
)


@pytest.mark.parametrize("offer_type, argument", OFERTAS)
@pytest.mark.parametrize("nome_produto, quantidade", CASOS)
def test_descontos_identicos_ao_legado(nome_produto, quantidade, offer_type, argument):
    catalog, p = _montar_catalogo()
    produto = p[nome_produto]
    teller = Teller(catalog)
    teller.add_special_offer(offer_type, produto, argument)
    cart = ShoppingCart()
    cart.add_item_quantity(produto, quantidade)

    receipt = teller.checks_out_articles_from(cart)

    esperado = legacy_discounts(cart.product_quantities, teller.offers, catalog)
    obtido = [(d.product.name, d.description, d.discount_amount) for d in receipt.discounts]
    assert len(obtido) == len(esperado)
    for (nome_o, desc_o, valor_o), (nome_e, desc_e, valor_e) in zip(obtido, esperado):
        assert nome_o == nome_e
        assert desc_o == desc_e
        assert valor_o == pytest.approx(valor_e, abs=1e-9)


def test_carrinho_com_varios_produtos_e_ofertas_identico_ao_legado():
    catalog, p = _montar_catalogo()
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, p["toothbrush"], 0.0)
    teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, p["rice"], 4.0)
    cart = ShoppingCart()
    cart.add_item_quantity(p["toothbrush"], 7)
    cart.add_item_quantity(p["rice"], 5)
    cart.add_item_quantity(p["apples"], 2.0)  # sem oferta

    receipt = teller.checks_out_articles_from(cart)

    esperado = legacy_discounts(cart.product_quantities, teller.offers, catalog)
    obtido = [(d.product.name, d.description, d.discount_amount) for d in receipt.discounts]
    assert obtido == [(n, d, pytest.approx(v)) for n, d, v in esperado]


# --- 3. Casos-limite ---

def test_carrinho_vazio_gera_recibo_vazio():
    catalog, _ = _montar_catalogo()
    receipt = Teller(catalog).checks_out_articles_from(ShoppingCart())
    assert receipt.items == []
    assert receipt.discounts == []
    assert receipt.total_price() == 0


def test_produto_sem_oferta_nao_gera_desconto():
    catalog, p = _montar_catalogo()
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, p["toothbrush"], 0.0)
    cart = ShoppingCart()
    cart.add_item_quantity(p["rice"], 10)
    receipt = teller.checks_out_articles_from(cart)
    assert receipt.discounts == []
    assert receipt.total_price() == pytest.approx(24.90)


def test_segunda_oferta_no_mesmo_produto_substitui_a_primeira():
    catalog, p = _montar_catalogo()
    teller = Teller(catalog)
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, p["toothbrush"], 0.0)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, p["toothbrush"], 10.0)
    cart = ShoppingCart()
    cart.add_item_quantity(p["toothbrush"], 3)
    receipt = teller.checks_out_articles_from(cart)
    assert [d.description for d in receipt.discounts] == ["10.0% off"]


# --- 4. Mudança intencional: validação de quantidade (o legado aceitava estes valores) ---

@pytest.mark.parametrize("nome_produto, quantidade", [
    ("toothbrush", 0),
    ("toothbrush", -1),
    ("toothbrush", 1.5),   # produto por unidade com quantidade fracionada
    ("apples", 0),
    ("apples", -0.5),
])
def test_quantidade_invalida_e_rejeitada(nome_produto, quantidade):
    _, p = _montar_catalogo()
    with pytest.raises(ValueError):
        ShoppingCart().add_item_quantity(p[nome_produto], quantidade)
