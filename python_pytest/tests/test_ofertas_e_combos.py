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

    def test_teller_offers_preserves_dict_interface(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        assert isinstance(teller.offers, dict)
        assert toothbrush in teller.offers
        assert list(teller.offers.keys()) == [toothbrush]

    def test_second_offer_on_same_product_overwrites_first(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 3)

        receipt = teller.checks_out_articles_from(cart)

        # Apenas a última oferta (10%) deve valer: 30.00 - 3.00 = 27.00
        assert pytest.approx(receipt.total_price(), 0.01) == 27.00
        assert len(receipt.discounts) == 1

    def test_discounts_follow_cart_insertion_order(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 1.00)
        catalog.add_product(toothpaste, 2.00)

        teller = Teller(catalog)
        # Cadastra toothpaste primeiro, toothbrush depois
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothpaste, 10.0)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        cart = ShoppingCart()
        # Adiciona toothbrush primeiro no carrinho, toothpaste depois
        cart.add_item_quantity(toothbrush, 1)
        cart.add_item_quantity(toothpaste, 1)

        receipt = teller.checks_out_articles_from(cart)

        assert [d.product for d in receipt.discounts] == [toothbrush, toothpaste]           

    def test_teller_offers_stores_native_offer_objects(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)

        offer = teller.offers[toothbrush]
        assert offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT
        assert offer.product == toothbrush
        assert offer.argument == 10.0

    def test_combo_and_individual_percentage_offer_do_not_double_discount(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)
        catalog.add_product(toothpaste, 15.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, toothbrush, 10.0)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 1)
        cart.add_item_quantity(toothpaste, 1)

        receipt = teller.checks_out_articles_from(cart)

        # 1 escova + 1 creme fecham o combo (-2.50); não sobra escova para o 10% individual
        assert pytest.approx(receipt.total_price(), 0.01) == 22.50
        assert len(receipt.discounts) == 1

    def test_combo_and_three_for_two_do_not_reuse_same_unit(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)
        catalog.add_product(toothpaste, 15.00)

        teller = Teller(catalog)
        teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, toothbrush, None)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 4)  # 1 vai para o combo, 3 restantes fecham o 3 por 2
        cart.add_item_quantity(toothpaste, 1)

        receipt = teller.checks_out_articles_from(cart)

        # Bruto: 4*10 + 15 = 55.00 | Combo: -2.50 | 3 por 2 nas 3 restantes: -10.00 -> 42.50
        assert pytest.approx(receipt.total_price(), 0.01) == 42.50
        assert len(receipt.discounts) == 2

    def test_two_overlapping_combos_do_not_reuse_same_product_unit(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        toothpaste = Product("toothpaste", ProductUnit.EACH)
        floss = Product("floss", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)
        catalog.add_product(toothpaste, 15.00)
        catalog.add_product(floss, 5.00)

        teller = Teller(catalog)
        teller.add_combo_offer([toothbrush, toothpaste], percentage=10.0)
        teller.add_combo_offer([toothbrush, floss], percentage=10.0)

        cart = ShoppingCart()
        cart.add_item_quantity(toothbrush, 1)
        cart.add_item_quantity(toothpaste, 1)
        cart.add_item_quantity(floss, 1)

        receipt = teller.checks_out_articles_from(cart)

        # Apenas o primeiro combo usa a única escova (-2.50); o segundo não aplica
        assert pytest.approx(receipt.total_price(), 0.01) == 27.50
        assert len(receipt.discounts) == 1

    def test_invalid_combo_offers_raise_value_error(self):
        catalog = FakeCatalog()
        toothbrush = Product("toothbrush", ProductUnit.EACH)
        catalog.add_product(toothbrush, 10.00)

        teller = Teller(catalog)

        with pytest.raises(ValueError):
            teller.add_combo_offer([toothbrush])

        with pytest.raises(ValueError):
            teller.add_combo_offer([toothbrush, toothbrush])

    def test_combo_never_increases_price_over_existing_offers(self):
        scenarios = [
            (SpecialOfferType.THREE_FOR_TWO, None, 3, 1, 35.00),
            (SpecialOfferType.THREE_FOR_TWO, None, 6, 2, 70.00),
            (SpecialOfferType.TEN_PERCENT_DISCOUNT, 50.0, 1, 1, 20.00),
            (SpecialOfferType.TWO_FOR_AMOUNT, 12.0, 2, 1, 27.00),
            (SpecialOfferType.TEN_PERCENT_DISCOUNT, 10.0, 1, 1, 22.50),
        ]

        for offer_type, argument, brush_qty, paste_qty, expected_total in scenarios:
            catalog = FakeCatalog()
            toothbrush = Product("toothbrush", ProductUnit.EACH)
            toothpaste = Product("toothpaste", ProductUnit.EACH)
            catalog.add_product(toothbrush, 10.00)
            catalog.add_product(toothpaste, 15.00)

            teller_without_combo = Teller(catalog)
            teller_without_combo.add_special_offer(offer_type, toothbrush, argument)

            teller_with_combo = Teller(catalog)
            teller_with_combo.add_special_offer(offer_type, toothbrush, argument)
            teller_with_combo.add_combo_offer([toothbrush, toothpaste], percentage=10.0)

            cart_a = ShoppingCart()
            cart_a.add_item_quantity(toothbrush, brush_qty)
            cart_a.add_item_quantity(toothpaste, paste_qty)

            cart_b = ShoppingCart()
            cart_b.add_item_quantity(toothbrush, brush_qty)
            cart_b.add_item_quantity(toothpaste, paste_qty)

            total_without = teller_without_combo.checks_out_articles_from(cart_a).total_price()
            total_with = teller_with_combo.checks_out_articles_from(cart_b).total_price()

            assert total_with <= total_without
            assert pytest.approx(total_with, 0.01) == expected_total        