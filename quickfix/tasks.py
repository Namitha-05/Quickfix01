# import frappe
# from frappe.utils import today, now

# def check_low_stock():
#     start = today() + " 00:00:00"
#     end = today() + " 23:59:59"
#     last_run = frappe.db.get_value(
#         "Audit Log",
#         {
#             "action": "low_stock_check",
#             "timestamp": ["between", [start, end]]
#         },
#         "name"
#     )
#     if last_run:
#         print("Already ran today")
#         return

#     print("Checking low stock items...")

#     frappe.get_doc({
#         "doctype": "Audit Log",
#         "action": "low_stock_check",
#         "doctype_name": "System",
#         "document_name": "Daily Low Stock Check",
#         "user": "Administrator",
#         "timestamp": now()
#     }).insert(ignore_permissions=True)

#     frappe.db.commit()
#     print("Job completed")