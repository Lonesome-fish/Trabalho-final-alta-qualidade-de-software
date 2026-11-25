"""
Oráculo do comportamento legado (usado somente nos testes).

Cópia do algoritmo original de ShoppingCart.handle_offers (commit 297b164), escrita como
função pura. Serve para comparar o sistema refatorado com o legado, caso a caso.

Diferenças em relação ao original, todas mudanças intencionais e documentadas:
  1. "2 por X": divisão inteira (//) em vez de (/). O legado cobrava a mais com quantidade ímpar.
  2. Produtos por KILO em ofertas de pacote (3 por 2, 2 por X, 5 por X): a fração que não fecha
     um pacote é cobrada a preço cheio. O legado dava essa fração de graça.
"""
import math

from model_objects import SpecialOfferType


def legacy_discounts(product_quantities, offers, catalog):
    """Retorna [(nome_do_produto, descricao, valor)] como o legado produziria."""
    result = []
    for p in product_quantities.keys():
        quantity = product_quantities[p]
        if p in offers.keys():
            offer = offers[p]
            unit_price = catalog.unit_price(p)
            quantity_as_int = int(quantity)
            discount = None
            x = 1
            if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
                x = 3
            elif offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
                x = 2
                if quantity_as_int >= 2:
                    total = offer.argument * (quantity_as_int // x) + quantity_as_int % 2 * unit_price
                    discount_n = unit_price * quantity_as_int - total
                    discount = (p.name, "2 for " + str(offer.argument), -discount_n)
            if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
                x = 5
            number_of_x = math.floor(quantity_as_int / x)
            if offer.offer_type == SpecialOfferType.THREE_FOR_TWO and quantity_as_int > 2:
                discount_amount = quantity_as_int * unit_price - (
                    (number_of_x * 2 * unit_price) + quantity_as_int % 3 * unit_price)
                discount = (p.name, "3 for 2", -discount_amount)
            if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
                discount = (p.name, str(offer.argument) + "% off",
                            -quantity * unit_price * offer.argument / 100.0)
            if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT and quantity_as_int >= 5:
                discount_total = unit_price * quantity_as_int - (
                    offer.argument * number_of_x + quantity_as_int % 5 * unit_price)
                discount = (p.name, str(x) + " for " + str(offer.argument), -discount_total)
            if discount:
                result.append(discount)
    return result
