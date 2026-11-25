from __future__ import annotations

from abc import ABC, abstractmethod
import math

from model_objects import Discount, Product, ProductUnit, SpecialOfferType


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, remaining_quantities: dict, catalog):
        """Retorna o desconto e as unidades consumidas pela oferta."""
        pass


class NoDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, remaining_quantities: dict, catalog):
        return None, {}


class PercentageDiscountStrategy(DiscountStrategy):
    def __init__(self, product: Product, percentage: float):
        self.product, self.percentage = product, percentage

    def calculate_discount(self, remaining_quantities: dict, catalog):
        quantity = remaining_quantities.get(self.product, 0)
        if quantity <= 0:
            return None, {}
        amount = quantity * catalog.unit_price(self.product) * self.percentage / 100.0
        return Discount(self.product, f"{self.percentage}% off", -amount), {self.product: quantity}


class ThreeForTwoStrategy(DiscountStrategy):
    def __init__(self, product: Product):
        self.product = product

    def calculate_discount(self, remaining_quantities: dict, catalog):
        quantity = remaining_quantities.get(self.product, 0)
        quantity_as_int = int(quantity)
        if quantity_as_int < 3:
            return None, {}
        price = catalog.unit_price(self.product)
        groups = quantity_as_int // 3
        amount = quantity * price - (groups * 2 * price + quantity_as_int % 3 * price)
        return Discount(self.product, "3 for 2", -amount), {self.product: groups * 3}


class XForAmountStrategy(DiscountStrategy):
    def __init__(self, product: Product, required_quantity: int, target_amount: float):
        self.product, self.required_quantity, self.target_amount = product, required_quantity, target_amount

    def calculate_discount(self, remaining_quantities: dict, catalog):
        quantity = remaining_quantities.get(self.product, 0)
        quantity_as_int = int(quantity)
        if quantity_as_int < self.required_quantity:
            return None, {}
        price = catalog.unit_price(self.product)
        groups = quantity_as_int // self.required_quantity
        total = self.target_amount * groups + quantity_as_int % self.required_quantity * price
        amount = price * quantity - total
        return Discount(self.product, f"{self.required_quantity} for {self.target_amount}", -amount), {self.product: groups * self.required_quantity}


class ComboDiscountStrategy(DiscountStrategy):
    def __init__(self, products: list[Product], percentage: float = 10.0):
        if not products or len(products) < 2:
            raise ValueError("Um combo deve conter pelo menos 2 produtos distintos.")
        if len(set(products)) != len(products):
            raise ValueError("Um combo não pode conter produtos repetidos.")
        if percentage <= 0 or percentage > 100:
            raise ValueError("O percentual de desconto do combo deve estar entre 0 e 100.")
        self.products, self.percentage = list(products), percentage

    def calculate_discount(self, remaining_quantities: dict, catalog):
        if any(remaining_quantities.get(p, 0) < 1 for p in self.products):
            return None, {}
        combos = min(int(remaining_quantities[p]) for p in self.products)
        amount = combos * sum(catalog.unit_price(p) for p in self.products) * self.percentage / 100.0
        combo_product = Product(" + ".join(p.name for p in self.products), ProductUnit.EACH)
        return Discount(combo_product, f"Combo {self.percentage}% off", -amount), {p: combos for p in self.products}


class DiscountStrategyFactory:
    _creators = {
        SpecialOfferType.THREE_FOR_TWO: lambda product, argument: ThreeForTwoStrategy(product),
        SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda product, argument: PercentageDiscountStrategy(product, argument),
        SpecialOfferType.TWO_FOR_AMOUNT: lambda product, argument: XForAmountStrategy(product, 2, argument),
        SpecialOfferType.FIVE_FOR_AMOUNT: lambda product, argument: XForAmountStrategy(product, 5, argument),
    }

    @staticmethod
    def create_strategy(offer_type, product: Product, argument):
        creator = DiscountStrategyFactory._creators.get(offer_type)
        return NoDiscountStrategy() if creator is None else creator(product, argument)


class DiscountCalculator:
    @staticmethod
    def _consume_units(remaining_quantities: dict, consumed: dict) -> None:
        for product, quantity in consumed.items():
            if product in remaining_quantities:
                remaining_quantities[product] = max(0, remaining_quantities[product] - quantity)

    def _calculate_individual_offers(self, remaining_quantities, cart_order, offers, catalog):
        discounts = []
        for product in cart_order:
            if product not in offers:
                continue
            offer = offers[product]
            strategy = offer if isinstance(offer, DiscountStrategy) else DiscountStrategyFactory.create_strategy(offer.offer_type, offer.product, offer.argument)
            discount, consumed = strategy.calculate_discount(remaining_quantities, catalog)
            if discount:
                discounts.append(discount)
                self._consume_units(remaining_quantities, consumed)
        return discounts

    def _calculate_combo_offers(self, remaining_quantities, combo_offers, catalog):
        discounts = []
        for strategy in (combo_offers or {}).values():
            discount, consumed = strategy.calculate_discount(remaining_quantities, catalog)
            if discount:
                discounts.append(discount)
                self._consume_units(remaining_quantities, consumed)
        return discounts

    def calculate_discounts(self, product_quantities, offers, catalog, combo_offers=None):
        order = list(product_quantities.keys())
        remaining = dict(product_quantities)
        individual_first = self._calculate_individual_offers(remaining, order, offers, catalog)
        individual_first += self._calculate_combo_offers(remaining, combo_offers, catalog)

        if not combo_offers:
            return individual_first

        remaining = dict(product_quantities)
        combo_first = self._calculate_combo_offers(remaining, combo_offers, catalog)
        combo_first += self._calculate_individual_offers(remaining, order, offers, catalog)
        if sum(d.discount_amount for d in combo_first) < sum(d.discount_amount for d in individual_first):
            return combo_first
        return individual_first
