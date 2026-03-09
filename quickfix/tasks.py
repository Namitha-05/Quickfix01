import frappe
from frappe.utils import now, today

def check_low_stock():

    last_run = frappe.db.sql("""
        SELECT name
        FROM `tabAudit Log`
        WHERE action='low_stock_check'
        AND DATE(timestamp)=%s
        LIMIT 1
    """, (today(),))

    if last_run:
        print("Already ran today")
        return

    print("Checking low stock items...")

    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "doctype_name": "System",
        "document_name": "Daily Low Stock Check",
        "user": "Administrator",
        "timestamp": now()
    }).insert(ignore_permissions=True)

    frappe.db.commit()

    print("Job completed")