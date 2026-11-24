import unittest
import pytest

from model_objects import Product, SpecialOfferType, ProductUnit
from shopping_cart import ShoppingCart
from teller import Teller
from tests.fake_catalog import FakeCatalog


class SupermarketTest(unittest.TestCase):
    def test_ten_percent_discount(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 0.99)

        apples = Product("apples", ProductUnit.KILO)
        catalog.add_product(apples, 1.99)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(apples, 2.5)

        receipt = teller.checks_out_articles_from(cart)

        self.assertAlmostEqual(receipt.total_price(), 4.975, places=2)
        self.assertEqual([], receipt.discounts)
        self.assertEqual(1, len(receipt.items))
        receipt_item = receipt.items[0]
        self.assertEqual(apples, receipt_item.product)
        self.assertEqual(1.99, receipt_item.price)
        self.assertAlmostEqual(receipt_item.total_price, 2.5 * 1.99, places=2)
        self.assertEqual(2.5, receipt_item.quantity)
    
    def test_combo_discount_with_extra_items(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)
        catalog.add_product(toothpaste, 2.00)

        teller = Teller(catalog)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 2)  # 1 no combo + 1 excedente
        cart.add_item_quantity(toothpaste, 1)  # 1 no combo

        receipt = teller.checks_out_articles_from(cart)

        # Sem desconto: 2*1.00 + 1*2.00 = 4.00
        # Desconto de 10% sobre 1 combo (1.00 + 2.00 = 3.00): -0.30
        # Total esperado: 3.70
        assert pytest.approx(receipt.total_price(), 0.01) == 3.70
        assert len(receipt.discounts) == 1
    def test_three_for_two_discount(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 3)

        receipt = teller.checks_out_articles_from(cart)

        assert pytest.approx(receipt.total_price(), 0.01) == 2.00
        assert len(receipt.discounts) == 1

    def test_two_for_amount_discount(self):
        catalog = FakeCatalog()
        tomatoes = Product("cherry tomatoes", ProductUnit.EACH)
        catalog.add_product(tomatoes, 0.69)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TWO_FOR_AMOUNT, tomatoes, 0.99)

        cart = ShoppingCart()
        cart.add_item_quantity(tomatoes, 2)

        receipt = teller.checks_out_articles_from(cart)

        assert pytest.approx(receipt.total_price(), 0.01) == 0.99
        assert len(receipt.discounts) == 1

    def test_five_for_amount_discount(self):
        catalog = FakeCatalog()
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothpaste, 1.79)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.FIVE_FOR_AMOUNT, toothpaste, 7.49)

        cart = ShoppingCart()
        cart.add_item_quantity(toothpaste, 5)

        receipt = teller.checks_out_articles_from(cart)

        assert pytest.approx(receipt.total_price(), 0.01) == 7.49
        assert len(receipt.discounts) == 1

    def test_combo_incomplete_no_discount(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)
        catalog.add_product(toothpaste, 2.00)

        teller = Teller(catalog)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 2)  # falta a pasta para fechar o combo

        receipt = teller.checks_out_articles_from(cart)

        assert pytest.approx(receipt.total_price(), 0.01) == 2.00
        assert len(receipt.discounts) == 0

    def test_multiple_complete_combos(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)
        catalog.add_product(toothpaste, 2.00)

        teller = Teller(catalog)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 2)
        cart.add_item_quantity(toothpaste, 3)  # 2 combos completos + 1 pasta excedente

        receipt = teller.checks_out_articles_from(cart)

        # Sem desconto: 2*1.00 + 3*2.00 = 8.00
        # 10% sobre 2 combos (2 * 3.00 = 6.00): -0.60 -> Total: 7.40
        assert pytest.approx(receipt.total_price(), 0.01) == 7.40
        assert len(receipt.discounts) == 1        
