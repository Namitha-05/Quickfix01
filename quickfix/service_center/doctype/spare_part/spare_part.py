import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

class SparePart(Document):

    def autoname(self):
        if self.part_code:
            self.name = self.part_code.upper() + "-" + make_autoname("PART-.YYYY.-.####")

    def validate(self):
        self.validate_pricing()

    def validate_pricing(self):
        if self.unit_cost is not None and self.selling_price is not None:
            if self.selling_price <= self.unit_cost:
                frappe.throw(
                    ("Selling Price ({0}) must be greater than Unit Cost ({1}).")
                    .format(self.selling_price, self.unit_cost),
                    title=("Invalid Pricing")
                )