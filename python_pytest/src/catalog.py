
class SupermarketCatalog:
    '''
    Interface do catálogo de produtos. A implementação real acessa o banco de dados;
    nos testes é usado o FakeCatalog.
    '''
    def add_product(self, product, price):
        raise NotImplementedError("Subclasses devem implementar add_product")

    def unit_price(self, product):
        raise NotImplementedError("Subclasses devem implementar unit_price")

    def product_with_name(self, name):
        raise NotImplementedError("Subclasses devem implementar product_with_name")
