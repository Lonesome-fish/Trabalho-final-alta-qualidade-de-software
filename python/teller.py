from discount_strategies import ComboDiscountStrategy
from model_objects import Offer
from receipt import Receipt


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.combo_offers = {}

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    def add_combo_offer(self, products: list, percentage: float = 10.0):
        strategy = ComboDiscountStrategy(products, percentage)
        self.combo_offers[frozenset(products)] = strategy

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        product_quantities = the_cart.items
        for pq in product_quantities:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)

        the_cart.handle_offers(receipt, self.offers, self.catalog, self.combo_offers)

        return receipt