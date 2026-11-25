from discount_strategies import ComboDiscountStrategy, DiscountCalculator
from model_objects import Offer
from receipt import Receipt


class Teller:

    def __init__(self, catalog, discount_calculator=None):
        self.catalog = catalog
        self.discount_calculator = discount_calculator or DiscountCalculator()
        self.offers = {}
        self.combo_offers = {}

    def add_special_offer(self, offer_or_type, product=None, argument=None) -> None:
        """Registra uma oferta legada ou uma DiscountStrategy diretamente."""
        if product is None and hasattr(offer_or_type, "product"):
            self.offers[offer_or_type.product] = offer_or_type
            return
        self.offers[product] = Offer(offer_or_type, product, argument)

    def add_combo_offer(self, products: list, percentage: float = 10.0) -> None:
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

        discounts = self.discount_calculator.calculate_discounts(
            the_cart.product_quantities,
            self.offers,
            self.catalog,
            self.combo_offers,
        )
        for discount in discounts:
            receipt.add_discount(discount)

        return receipt

    def product_with_name(self, name):
        return self.catalog.product_with_name(name)
