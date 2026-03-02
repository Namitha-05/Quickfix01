# Copyright (c) 2026, Namitha and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document


class JobCard(Document):

    def before_insert(self):
        default_labor = frappe.db.get_single_value(
            "QuickFix Settings",
            "default_labour_charge"
        )
        if not self.labour_charge:
            self.labour_charge = default_labor


    def validate(self):
        if not self.customer_phone:
            frappe.throw("Controller: phone required")

        if not re.fullmatch(r"\d{10}", self.customer_phone or ""):
            frappe.throw(
                "Customer Phone must contain exactly 10 numeric digits (0-9).",
                title="Invalid Phone Number"
            )

        if self.status in ["In Repair", "Ready for Delivery", "Completed"]:
            if not self.assigned_technician:
                frappe.throw(
                    f"Assigned Technician is required when status is '{self.status}'.",
                    title="Technician Missing"
                )

        parts_total = 0

        for row in self.parts_used:
            qty = row.quantity or 0
            rate = row.unit_price or 0
            row.total_price = qty * rate
            parts_total += row.total_price

        self.parts_total = parts_total

        if self.labour_charge is None:
            self.labour_charge = frappe.db.get_single_value(
                "QuickFix Settings",
                "default_labour_charge"
            ) or 0

        self.final_amount = self.parts_total + (self.labour_charge or 0)


    def before_submit(self):
        if self.status != "Ready for Delivery":
            frappe.throw(
                "Job Card can only be submitted when status is 'Ready for Delivery'."
            )
        if not self.parts_used:
            return

        for row in self.parts_used:

            available_stock = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            ) or 0

            required_qty = row.quantity or 0

            if required_qty <= 0:
                frappe.throw(f"Quantity must be > 0 for {row.part}")

            if available_stock < required_qty:
                frappe.throw(
                    f"Insufficient stock for {row.part}. "
                    f"Available {available_stock}, Required {required_qty}"
                )

    def on_submit(self):
        for row in self.parts_used:
            available_stock = frappe.db.get_value(
                "Spare Part",
                row.part,
                "stock_qty"
            ) or 0

            new_stock = available_stock - (row.quantity or 0)
            frappe.db.set_value(
                "Spare Part",
                row.part,
                "stock_qty",
                new_stock
            )
        invoice = frappe.get_doc({
            "doctype": "Service Invoice",
            "customer": self.customer_name,
            "job_card": self.name,
            "amount": self.final_amount
        })
        invoice.insert(ignore_permissions=True)

        frappe.publish_realtime(
            "job_ready",
            {"job_card": self.name},
            user=self.owner
        )

        frappe.enqueue(
            "quickfix.quickfix.doctype.job_card.job_card.send_job_ready_email",
            job_card=self.name
        )

    def on_cancel(self):
        self.db_set("status", "Cancelled")
        if self.parts_used:
            for row in self.parts_used:

                current_stock = frappe.db.get_value(
                    "Spare Part",
                    row.part,
                    "stock_qty"
                ) or 0

                restored_stock = current_stock + (row.quantity or 0)

                frappe.db.set_value(
                    "Spare Part",
                    row.part,
                    "stock_qty",
                    restored_stock
                )

        invoice_name = frappe.db.get_value(
            "Service Invoice",
            {"job_card": self.name},
            "name"
        )
        if invoice_name:
            invoice = frappe.get_doc(
                "Service Invoice",
                invoice_name
            )
            if invoice.docstatus == 1:
                invoice.cancel()

    def on_trash(self):
        if self.status not in ["Draft", "Cancelled"]:
            frappe.throw(
                "Only Draft or Cancelled Job Cards can be deleted."
            )

    def on_update(self):
        if self.status == "Completed" and not self.completed_on:
            self.db_set("completed_on", frappe.utils.now())