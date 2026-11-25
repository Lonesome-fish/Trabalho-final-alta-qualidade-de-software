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
        self.receipt_item_factory = ReceiptItem
    def total_price(self):
        total = 0
        for item in self.items:
            total += item.total_price
        for discount in self.discounts:
            total += discount.discount_amount
        return total

    def add_product(self, product, quantity, price, total_price):
        self._items.append(self.receipt_item_factory(product, quantity, price, total_price))

    def add_discount(self, discount):
        self._discounts.append(discount)
    #Properties são usados para copiar o _items e _discounts para evitar acessar as informações
    #diretamente e modificar os valores, garantindo que a lista original permaneça inalterada.
    @property
    def items(self):
        return self._items[:]

    @property
    def discounts(self):
        return self._discounts[:]
