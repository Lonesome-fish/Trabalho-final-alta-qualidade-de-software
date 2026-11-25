import math

from model_objects import ProductQuantity, SpecialOfferType, Discount
from discount_strategies import DiscountStrategyFactory


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt, offers, catalog, combo_offers=None):
        # 1. Segue a ordem dos produtos adicionados ao carrinho (preserva ordem do recibo)
        for p in self._product_quantities.keys():
            if p in offers:
                strategy = offers[p]
                # Compatibilidade caso testes de caracterização passem Offer legado diretamente
                if not hasattr(strategy, "calculate_discount"):
                    strategy = DiscountStrategyFactory.create_strategy(
                        strategy.offer_type, strategy.product, strategy.argument
                    )
                discount = strategy.calculate_discount(self._product_quantities, catalog)
                if discount:
                    receipt.add_discount(discount)

        # 2. Avalia combos completos sem interferir nas ofertas individuais
        if combo_offers:
            for combo_strategy in combo_offers.values():
                discount = combo_strategy.calculate_discount(self._product_quantities, catalog)
                if discount:
                    receipt.add_discount(discount)
