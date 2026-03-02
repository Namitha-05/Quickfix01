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

    def on_update(self):
            threshold = frappe.db.get_value(
                "QuickFix Settings", None, "low_stock_threshold"
            )
            if self.stock_qty < (threshold or 0):
                frappe.msgprint(f"Warning: Stock for {self.part_name} is below threshold ({threshold})")


# QuickFix Settings is a Single DocType (issingle = 1), so its values are
# stored in the tabSingles table.

# In controller methods like on_update, frappe.db.get_value should be used
# instead of frappe.get_doc because get_doc loads the entire document
# object including all fields and metadata, which is slower.

# frappe.db.get_value directly fetches only the required field from the
# database, making it more efficient for frequently executed controller
# methods.

# Passing None as the name parameter indicates that the value should be
# fetched from a Single DocType.