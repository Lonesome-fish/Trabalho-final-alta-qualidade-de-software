import math

from model_objects import ProductQuantity, ProductUnit


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}
        self.product_quantity_factory = ProductQuantity

    @property
    def items(self):
        return list(self._items)

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return dict(self._product_quantities)

    def add_item_quantity(self, product, quantity):
        self._validate_item_and_quantity(product, quantity)
        self._items.append(self.product_quantity_factory(product, quantity))
        if product in self._product_quantities:
            self._product_quantities[product] += quantity
        else:
            self._product_quantities[product] = quantity

    @staticmethod
    def _validate_item_and_quantity(product, quantity):
        if product is None:
            raise ValueError("O produto não pode ser nulo.")
        if isinstance(quantity, bool) or not isinstance(quantity, (int, float)):
            raise ValueError("A quantidade deve ser um valor numérico válido.")
        if math.isnan(quantity) or math.isinf(quantity) or quantity <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        if getattr(product, "unit", None) == ProductUnit.EACH and not float(quantity).is_integer():
            raise ValueError("Produtos vendidos por unidade (EACH) aceitam apenas quantidades inteiras.")