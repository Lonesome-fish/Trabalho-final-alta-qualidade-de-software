from model_objects import ProductUnit
from receipt import Receipt
from tests.receipt_printer import ReceiptPrinter
import pytest
@pytest.mark.parametrize(
    "quantidade_tooth, quantidade_apple, total_esperado_tooth, total_esperado_apple",
    [
        (1, 1, 0.99, 1.99),
        (2, 1, 1.98, 1.99),
        (3, 1, 2.97, 1.99),
        (4, 1, 3.96, 1.99),
        (6, 1, 5.94, 1.99),
    ],
)
def test_receipt_printer_prints_receipt(catalogo_preenchido, quantidade_tooth, quantidade_apple, total_esperado_tooth, total_esperado_apple):
    catalog, toothbrush, apple = catalogo_preenchido
    receipt = Receipt()
    receipt.add_product(toothbrush, quantidade_tooth, 0.99, total_esperado_tooth)
    receipt.add_product(apple, quantidade_apple, 1.99, total_esperado_apple)
        
    printer = ReceiptPrinter()
    printed_receipt = printer.print_receipt(receipt)

    print(f"Printed Receipt:\n{printed_receipt}")