from __future__ import annotations

from abc import ABC, abstractmethod
from model_objects import Discount, Product, ProductUnit, SpecialOfferType


class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        """Retorna (Discount | None, dict_de_unidades_consumidas)."""
        pass


class NoDiscountStrategy(DiscountStrategy):
    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        return None, {}


class PercentageDiscountStrategy(DiscountStrategy):
    def __init__(self, product: Product, percentage: float):
        self.product = product
        self.percentage = percentage

    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        quantity = remaining_quantities.get(self.product, 0)
        if quantity <= 0:
            return None, {}

        unit_price = catalog.unit_price(self.product)
        discount_amount = quantity * unit_price * self.percentage / 100.0
        discount = Discount(self.product, f"{self.percentage}% off", -discount_amount)
        return discount, {self.product: quantity}


class ThreeForTwoStrategy(DiscountStrategy):
    def __init__(self, product: Product):
        self.product = product

    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        quantity = remaining_quantities.get(self.product, 0)
        quantity_as_int = int(quantity)
        if quantity_as_int <= 2:
            return None, {}

        unit_price = catalog.unit_price(self.product)
        number_of_sets = quantity_as_int // 3
        discount_amount = quantity * unit_price - (
            (number_of_sets * 2 * unit_price) + (quantity_as_int % 3) * unit_price
        )
        discount = Discount(self.product, "3 for 2", -discount_amount)
        return discount, {self.product: number_of_sets * 3}


class XForAmountStrategy(DiscountStrategy):
    def __init__(self, product: Product, required_quantity: int, target_amount: float):
        self.product = product
        self.required_quantity = required_quantity
        self.target_amount = target_amount

    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        quantity = remaining_quantities.get(self.product, 0)
        quantity_as_int = int(quantity)
        if quantity_as_int < self.required_quantity:
            return None, {}

        unit_price = catalog.unit_price(self.product)
        number_of_sets = quantity_as_int // self.required_quantity
        total = (
            self.target_amount * number_of_sets
            + (quantity_as_int % self.required_quantity) * unit_price
        )
        discount_amount = unit_price * quantity - total
        discount = Discount(
            self.product,
            f"{self.required_quantity} for {self.target_amount}",
            -discount_amount,
        )
        return discount, {self.product: number_of_sets * self.required_quantity}


class ComboDiscountStrategy(DiscountStrategy):
    def __init__(self, products: list[Product], percentage: float = 10.0):
        if not products or len(products) < 2:
            raise ValueError("Um combo deve conter pelo menos 2 produtos distintos.")
        if len(set(products)) != len(products):
            raise ValueError("Um combo não pode conter produtos repetidos.")
        if percentage <= 0 or percentage > 100:
            raise ValueError("O percentual de desconto do combo deve estar entre 0 e 100.")

        self.products = list(products)
        self.percentage = percentage

    def calculate_discount(
        self, remaining_quantities: dict, catalog
    ) -> tuple[Discount | None, dict]:
        if any(remaining_quantities.get(p, 0) < 1 for p in self.products):
            return None, {}

        complete_combos = min(int(remaining_quantities[p]) for p in self.products)
        if complete_combos <= 0:
            return None, {}

        combo_unit_total = sum(catalog.unit_price(p) for p in self.products)
        discount_amount = complete_combos * combo_unit_total * (self.percentage / 100.0)

        consumed = {p: complete_combos for p in self.products}
        combo_name = " + ".join(p.name for p in self.products)
        combo_product = Product(combo_name, ProductUnit.EACH)
        discount = Discount(combo_product, f"Combo {self.percentage}% off", -discount_amount)
        return discount, consumed


class DiscountStrategyFactory:
    # Cada tipo de oferta aponta para a função que cria sua estratégia.
    # Um tipo novo de oferta entra como uma linha nova, sem cadeia de if.
    _creators = {
        SpecialOfferType.THREE_FOR_TWO: lambda product, argument: ThreeForTwoStrategy(product),
        SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda product, argument: PercentageDiscountStrategy(product, argument),
        SpecialOfferType.TWO_FOR_AMOUNT: lambda product, argument: XForAmountStrategy(product, 2, argument),
        SpecialOfferType.FIVE_FOR_AMOUNT: lambda product, argument: XForAmountStrategy(product, 5, argument),
    }

    @staticmethod
    def create_strategy(offer_type, product: Product, argument) -> DiscountStrategy:
        creator = DiscountStrategyFactory._creators.get(offer_type)
        if creator is None:
            return NoDiscountStrategy()
        return creator(product, argument)


class DiscountCalculator:
    """Calcula descontos sem reutilizar unidades e escolhe o melhor cenário."""

    @staticmethod
    def _consume_units(remaining_quantities: dict, consumed: dict) -> None:
        for product, used_qty in consumed.items():
            if product in remaining_quantities:
                remaining_quantities[product] = max(
                    0, remaining_quantities[product] - used_qty
                )

    def _calculate_individual_offers(
        self,
        remaining_quantities: dict,
        cart_order: list,
        offers: dict,
        catalog,
    ) -> list[Discount]:
        discounts = []
        for product in cart_order:
            if product in offers:
                offer = offers[product]
                strategy = DiscountStrategyFactory.create_strategy(
                    offer.offer_type, offer.product, offer.argument
                )
                discount, consumed = strategy.calculate_discount(
                    remaining_quantities, catalog
                )
                if discount:
                    discounts.append(discount)
                    self._consume_units(remaining_quantities, consumed)
        return discounts

    def _calculate_combo_offers(
        self,
        remaining_quantities: dict,
        combo_offers: dict | None,
        catalog,
    ) -> list[Discount]:
        discounts = []
        if not combo_offers:
            return discounts

        for combo_strategy in combo_offers.values():
            discount, consumed = combo_strategy.calculate_discount(
                remaining_quantities, catalog
            )
            if discount:
                discounts.append(discount)
                self._consume_units(remaining_quantities, consumed)
        return discounts

    def calculate_discounts(
        self,
        product_quantities: dict,
        offers: dict,
        catalog,
        combo_offers: dict | None = None,
    ) -> list[Discount]:
        cart_order = list(product_quantities.keys())

        # Cenário 1: ofertas individuais primeiro, combos nas unidades sobrantes
        rem_offers_first = dict(product_quantities)
        best_discounts = self._calculate_individual_offers(
            rem_offers_first, cart_order, offers, catalog
        ) + self._calculate_combo_offers(
            rem_offers_first, combo_offers, catalog
        )

        # Cenário 2: combos primeiro, ofertas individuais nas unidades sobrantes
        if combo_offers:
            rem_combos_first = dict(product_quantities)
            discounts_combos_first = self._calculate_combo_offers(
                rem_combos_first, combo_offers, catalog
            ) + self._calculate_individual_offers(
                rem_combos_first, cart_order, offers, catalog
            )

            # discount_amount é negativo; menor soma = maior desconto para o cliente
            if sum(d.discount_amount for d in discounts_combos_first) < sum(
                d.discount_amount for d in best_discounts
            ):
                best_discounts = discounts_combos_first

        return best_discounts
