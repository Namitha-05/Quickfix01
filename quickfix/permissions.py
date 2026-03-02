import frappe

def jobcard_permission_query_conditions(user):
    roles = frappe.get_roles(user)

    if "QF Manager" in roles or "System Manager" in roles or "Administrator":
        return ""

    if "QF Technician":
        return f"""
            `tabJob Card`.assigned_technician IN (
                SELECT name FROM `tabTechnician`
                WHERE user = {frappe.db.escape(user)}
            )
    """

def service_invoice_has_permission(doc, user):
    if "QF Manager" in frappe.get_roles(user):
        return True

    payment_status = frappe.db.get_value(
        "Job Card",
        doc.job_card,
        "payment_status"
    )
    if payment_status != "Paid":
        return False
    return True


# def before_submit(self):

#     if self.status != "Ready for Delivery":
#         frappe.throw(
#             "Job Card can only be submitted when status is 'Ready for Delivery'.",
#             title="Invalid Status for Submission"
#         )

#     if not self.parts_used:
#         return

#     for row in self.parts_used:
#         available_stock = frappe.db.get_value(
#             "Spare Part",
#             row.part,
#             "stock_qty"
#         ) or 0

#         required_qty = row.quantity or 0

#         if required_qty <= 0:
#             frappe.throw(
#                 f"Quantity for Part '{row.part}' must be greater than zero.",
#                 title="Invalid Quantity"
#             )

#         if available_stock < required_qty:
#             frappe.throw(
#                 f"Insufficient stock for Part '{row.part}'. "
#                 f"Available: {available_stock}, Required: {required_qty}.",
#                 title="Stock Not Available"
#             )
        

# def on_submit(self):
#     for row in self.parts_used:
#         available_stock = frappe.db.get_value(
#             "Spare Part",
#             row.part,
#             "stock_qty"
#         ) or 0

#         new_stock = available_stock - (row.quantity or 0)
#         frappe.db.set_value(
#             "Spare Part",
#             row.part,
#             "stock_qty",
#             new_stock,
#             update_modified=False,
#             ignore_permissions=True
#         )
#         # ignore_permissions=True is acceptable here because
#         # this stock deduction is a system-initiated action triggered
#         # during Job Card submission, not a manual user edit.


#     invoice = frappe.get_doc({
#         "doctype": "Service Invoice",
#         "customer": self.customer_name,
#         "job_card": self.name,
#         "amount": self.final_amount
#     })
#     invoice.insert(ignore_permissions=True)


#     frappe.publish_realtime(
#         "job_ready",
#         {
#             "job_card": self.name,
#             "message": "Your job is ready for delivery."
#         },
#         user=self.owner
#     )

#     frappe.enqueue(
#         "quickfix.quickfix.doctype.job_card.send_job_ready_email",
#         job_card=self.name
#     )

#     def on_cancel(self):

#         self.status = "Cancelled"

#     # Restore stock
#     for row in self.parts_used:
#         current_stock = frappe.db.get_value("Spare Part", row.part, "stock_qty") or 0

#         frappe.db.set_value(
#             "Spare Part",
#             row.part,
#             "stock_qty",
#             current_stock + row.quantity,
#             update_modified=False
#         )

#     # Cancel Service Invoice
#     invoice_name = frappe.db.get_value(
#         "Service Invoice",
#         {"job_card": self.name},
#         "name"
#     )

#     if invoice_name:
#         invoice = frappe.get_doc("Service Invoice", invoice_name)
#         invoice.cancel()



# def on_trash(self):

#     if self.status not in ["Draft", "Cancelled"]:
#         frappe.throw(
#             "Only Draft or Cancelled Job Cards can be deleted."
#         )

# def on_update(self):

#     if self.status == "Completed" and not self.completed_on:
#         self.db_set("completed_on", frappe.utils.now())