# Copyright (c) 2026, Namitha and contributors
# For license information, please see license.txt

# import frappe
# from frappe.model.document import Document


import frappe
from frappe.model.document import Document

class JobCard(Document):

    def before_insert(self):
        default_labor = frappe.db.get_single_value( "QuickFix Settings", "default_labour_charge")
        if not self.labour_charge:
            self.labour_charge = default_labor