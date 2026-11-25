import pytest

from model_objects import Discount, Product, ProductUnit
from receipt import Receipt
from receipt_printer import ReceiptPrinter


def test_receipt_calculates_two_percent_tax():
    receipt = Receipt()
    apple = Product("maçã", ProductUnit.KILO)
    receipt.add_product(apple, 2.0, 50.0, 100.0)

    assert receipt.total_price() == pytest.approx(100.0)
    assert receipt.calculate_tax(0.02) == pytest.approx(2.0)
    assert receipt.total_price_with_tax(0.02) == pytest.approx(102.0)


def test_receipt_tax_applies_after_discounts():
    receipt = Receipt()
    toothbrush = Product("escova", ProductUnit.EACH)
    receipt.add_product(toothbrush, 2, 50.0, 100.0)
    receipt.add_discount(Discount(toothbrush, "10% off", -10.0))

    assert receipt.total_price() == pytest.approx(90.0)
    assert receipt.calculate_tax(0.02) == pytest.approx(1.8)
    assert receipt.total_price_with_tax(0.02) == pytest.approx(91.8)


def test_receipt_printer_prints_tax_and_dedication():
    receipt = Receipt()
    rice = Product("arroz", ProductUnit.EACH)
    receipt.add_product(rice, 1, 100.0, 100.0)

    printer = ReceiptPrinter(tax_rate=0.02)
    output = printer.print_receipt(receipt)

    assert "Impostos (2%):" in output
    assert "2.00" in output
    assert "Total com impostos:" in output
    assert "102.00" in output
    assert "Dedicatória: 2% de impostos incluídos." in output