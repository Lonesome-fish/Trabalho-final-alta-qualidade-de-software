from enum import Enum

#Classe de produto com nome e unidade de medida do produto 
class Product:
    def __init__(self, name, unit):
        self.name = name
        self.unit = unit

#Classe de quantidade de produto com produto e quantidade
class ProductQuantity:
    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity

#Classe de unidade de medida do produto com duas opções: EACH e KILO
class ProductUnit(Enum):
    EACH = 1
    KILO = 2

#Classe com enumeração de ofertas com 3 ou 5 por um preço fixo ou 3 por 2 ou 10% de desconto
class SpecialOfferType(Enum):
    THREE_FOR_TWO = 1
    TEN_PERCENT_DISCOUNT = 2
    TWO_FOR_AMOUNT = 3
    FIVE_FOR_AMOUNT = 4
#Classe de oferta com tipo de oferta, produto e argumento, usando para definir o desconto
#Ex: 10 para desconto de 10% ou 100 para 5 produtos por 100 reais, para ten_percent_discount e five_for_amount respectivamente
class Offer:
    def __init__(self, offer_type, product, argument):
        self.offer_type = offer_type
        self.product = product
        self.argument = argument

#Classe de desconto com produto, descrição e valor do desconto
class Discount:
    def __init__(self, product, description, discount_amount):
        self.product = product
        self.description = description
        self.discount_amount = discount_amount
