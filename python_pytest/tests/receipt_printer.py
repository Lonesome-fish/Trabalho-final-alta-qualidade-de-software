class ReceiptPrinter:
    def __init__(self, columns: int = 40, tax_rate: float = 0.0):
        self.columns = columns
        self.tax_rate = tax_rate

    def print_receipt(self, receipt):
        result = ""
        for item in receipt.items:
            result += self.present_receipt_item(item)
        for discount in receipt.discounts:
            result += self.present_discount(discount)
        result += "\n"
        result += self.present_total(receipt)
        if self.tax_rate > 0:
            result += self.present_tax_and_dedication(receipt)
        return str(result)

    def present_receipt_item(self, item):
        total_price_printed = self.print_price(item.total_price)
        name = item.product.name
        line = self.format_line_with_whitespace(name, total_price_printed)
        if item.quantity != 1:
            line += f"  {self.print_price(item.price)} * {self.present_quantity(item)}\n"
        return line

    def present_discount(self, discount):
        name = f"{discount.description} ({discount.product.name})"
        value = self.print_price(discount.discount_amount)
        return self.format_line_with_whitespace(name, value)

    def present_total(self, receipt):
        name = "Total: "
        value = self.print_price(receipt.total_price())
        return self.format_line_with_whitespace(name, value)

    def present_tax_and_dedication(self, receipt):
        tax_percent = f"{self.tax_rate * 100:.0f}%"
        tax_line = self.format_line_with_whitespace(
            f"Impostos ({tax_percent}): ",
            self.print_price(receipt.calculate_tax(self.tax_rate)),
        )
        final_total_line = self.format_line_with_whitespace(
            "Total com impostos: ",
            self.print_price(receipt.total_price_with_tax(self.tax_rate)),
        )
        dedication = f"Dedicatória: {tax_percent} de impostos incluídos.\n"
        return tax_line + final_total_line + dedication

    def format_line_with_whitespace(self, name, value):
        whitespace_size = self.columns - len(name) - len(value)
        return name + (" " * max(1, whitespace_size)) + value + "\n"

    def print_price(self, price):
        return f"{price:.2f}"

    def present_quantity(self, item):
        return f"{item.quantity}" if item.product.unit.name == "EACH" else f"{item.quantity:.3f}"