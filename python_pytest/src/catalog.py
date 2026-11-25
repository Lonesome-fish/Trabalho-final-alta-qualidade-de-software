
class SupermarketCatalog:
    '''
    Esse código define com catalogo com dois métodos mas sem implementação.
    '''
    def add_product(self, product, price):
        raise Exception("cannot be called from a unit test - it accesses the database")

    def unit_price(self, product):
        raise Exception("cannot be called from a unit test - it accesses the database")

class SupermarketCatalog:

    def add_product(self, product, price):
        raise NotImplementedError("Subclasses devem implementar add_product")

    def unit_price(self, product):
        raise NotImplementedError("Subclasses devem implementar unit_price")

    def product_with_name(self, name):
        raise NotImplementedError("Subclasses devem implementar product_with_name")    

