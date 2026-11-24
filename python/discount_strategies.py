from abc import ABC, abstractmethod
import math
from model_objects import Discount, Product, ProductUnit, SpecialOfferType


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, product_quantities: dict, catalog) -> Discount | None:
        pass


class PercentageDiscountStrategy(DiscountStrategy):
    """Serve para 10%, 20%, 50%, etc."""
    def __init__(self, product, percentage: float):
        self.product = product
        self.percentage = percentage

    def calculate_discount(self, product_quantities: dict, catalog) -> Discount | None:
        if self.product not in product_quantities:
            return None
        quantity = product_quantities[self.product]
        unit_price = catalog.unit_price(self.product)
        discount_amount = quantity * unit_price * self.percentage / 100.0
        return Discount(self.product, f"{self.percentage}% off", -discount_amount)


class XForAmountStrategy(DiscountStrategy):
    """Serve para 2 por X, 5 por X, 10 por X, etc."""
    def __init__(self, product, pack_size: int, amount: float):
        self.product = product
        self.pack_size = pack_size
        self.amount = amount

    def calculate_discount(self, product_quantities: dict, catalog) -> Discount | None:
        if self.product not in product_quantities:
            return None
        quantity = product_quantities[self.product]
        quantity_as_int = int(quantity)
        if quantity_as_int < self.pack_size:
            return None

        unit_price = catalog.unit_price(self.product)
        number_of_packs = math.floor(quantity_as_int / self.pack_size)
        remainder = quantity_as_int % self.pack_size
        total = (self.amount * number_of_packs) + (remainder * unit_price)
        discount_amount = (unit_price * quantity) - total
        return Discount(self.product, f"{self.pack_size} for {self.amount}", -discount_amount)


class BuyXPayYStrategy(DiscountStrategy):
    """Serve para Leve 3 Pague 2, Leve 4 Pague 3, etc."""
    def __init__(self, product, buy_qty: int, pay_qty: int):
        self.product = product
        self.buy_qty = buy_qty
        self.pay_qty = pay_qty

    def calculate_discount(self, product_quantities: dict, catalog) -> Discount | None:
        if self.product not in product_quantities:
            return None
        quantity = product_quantities[self.product]
        quantity_as_int = int(quantity)
        if quantity_as_int < self.buy_qty:
            return None

        unit_price = catalog.unit_price(self.product)
        number_of_groups = math.floor(quantity_as_int / self.buy_qty)
        remainder = quantity_as_int % self.buy_qty
        total = (number_of_groups * self.pay_qty * unit_price) + (remainder * unit_price)
        discount_amount = (quantity * unit_price) - total
        return Discount(self.product, f"{self.buy_qty} for {self.pay_qty}", -discount_amount)


class DiscountStrategyFactory:
    @staticmethod
    def create_strategy(offer_type: SpecialOfferType, product, argument: float) -> DiscountStrategy:
        strategies = {
            SpecialOfferType.THREE_FOR_TWO: lambda: BuyXPayYStrategy(product, buy_qty=3, pay_qty=2),
            SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda: PercentageDiscountStrategy(product, percentage=argument),
            SpecialOfferType.TWO_FOR_AMOUNT: lambda: XForAmountStrategy(product, pack_size=2, amount=argument),
            SpecialOfferType.FIVE_FOR_AMOUNT: lambda: XForAmountStrategy(product, pack_size=5, amount=argument),
        }
        creator = strategies.get(offer_type)
        if not creator:
            raise ValueError(f"Tipo de oferta desconhecido: {offer_type}")
        return creator()


class ComboDiscountStrategy(DiscountStrategy):
    """Aplica desconto percentual apenas para conjuntos completos de produtos."""
    def __init__(self, products: list, percentage: float = 10.0):
        self.products = products
        self.percentage = percentage

    def calculate_discount(self, product_quantities: dict, catalog) -> Discount | None:
        # 1. Verifica se TODOS os produtos do combo estão no carrinho
        if not self.products or any(p not in product_quantities for p in self.products):
            return None

        # 2. Quantidade de combos completos = menor quantidade inteira entre os itens
        complete_combos = min(int(product_quantities[p]) for p in self.products)
        if complete_combos <= 0:
            return None

        # 3. Soma o preço unitário de cada item do combo e aplica o percentual
        combo_unit_total = sum(catalog.unit_price(p) for p in self.products)
        discount_amount = complete_combos * combo_unit_total * (self.percentage / 100.0)

        combo_name = " + ".join(p.name for p in self.products)
        combo_product = Product(combo_name, ProductUnit.EACH)
        return Discount(combo_product, f"Combo {self.percentage}% off", -discount_amount)    