from discount_strategies import DiscountStrategy
from receipt import Receipt


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers: list[DiscountStrategy] = []

    def add_special_offer(self, strategy: DiscountStrategy) -> None:
        self.offers.append(strategy)

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        product_quantities = the_cart.items
        for pq in product_quantities:
            p = pq.product
            quantity = pq.quantity
            unit_price = self.catalog.unit_price(p)
            price = quantity * unit_price
            receipt.add_product(p, quantity, unit_price, price)
        the_cart.handle_offers(receipt, self.offers, self.catalog)
        return receipt

    def product_with_name(self, name):
        return self.catalog.products.get(name, None)
