#Classe de item do recibo com produto, quantidade, preço e preço total
class ReceiptItem:
    def __init__(self, product, quantity, price, total_price):
        self.product = product
        self.quantity = quantity
        self.price = price
        self.total_price = total_price

#Classe de recibo com itens e descontos
class Receipt:
    def __init__(self):
        self._items = []
        self._discounts = []

    def total_price(self):
        total = 0
        for item in self._items:
            total += item.total_price
        for discount in self._discounts:
            total += discount.discount_amount
        return total

    def calculate_tax(self, tax_rate: float = 0.02) -> float:
        if tax_rate < 0:
            raise ValueError("A taxa de imposto não pode ser negativa.")
        return self.total_price() * tax_rate

    def total_price_with_tax(self, tax_rate: float = 0.02) -> float:
        return self.total_price() + self.calculate_tax(tax_rate)

    def add_product(self, product, quantity, price, total_price):
        self._items.append(ReceiptItem(product, quantity, price, total_price))

    def add_discount(self, discount):
        self._discounts.append(discount)

    @property
    def items(self):
        return self._items[:]

    @property
    def discounts(self):
        return self._discounts[:]
