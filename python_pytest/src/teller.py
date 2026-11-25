from discount_strategies import ComboDiscountStrategy, DiscountCalculator
from model_objects import Offer
from receipt import Receipt

#Teller funciona como uma espécie de caixa registradora: registra ofertas e combos e faz o checkout.
#Ele orquestra o processo, mas não calcula descontos: isso fica com o DiscountCalculator.
class Teller:

    def __init__(self, catalog, discount_calculator=None):
        self.catalog = catalog
        self.offers = {}
        self.combo_offers = {}
        # O calculador de descontos pode ser trocado (ex.: em testes); sem parâmetro, usa o padrão.
        self._discount_calculator = discount_calculator or DiscountCalculator()

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    def add_combo_offer(self, products: list, percentage: float = 10.0):
        strategy = ComboDiscountStrategy(products, percentage)
        self.combo_offers[frozenset(products)] = strategy

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        for product_quantity in the_cart.items:
            product = product_quantity.product
            quantity = product_quantity.quantity
            unit_price = self.catalog.unit_price(product)
            receipt.add_product(product, quantity, unit_price, quantity * unit_price)

        self._discount_calculator.apply_offers(
            receipt, the_cart.product_quantities, self.offers, self.catalog, self.combo_offers
        )

        return receipt

    def product_with_name(self, name):
        return self.catalog.products.get(name, None)