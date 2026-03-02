import frappe
from frappe.utils import now_datetime


def log_change(doc, method):
    """
    Logs every change for any DocType
    """

    # ✅ stop during migrate / install / patch
    if frappe.flags.in_migrate or frappe.flags.in_install:
        return

    # ✅ prevent recursion
    if doc.doctype == "Audit Log":
        return


    try:
        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": doc.doctype,
            "document_name": doc.name,
            "action": method.replace("on_", "").capitalize(),
            "user": frappe.session.user,
            "timestamp": now_datetime()
        }).insert(ignore_permissions=True)

    except Exception:
        pass


def log_event(doctype_name, document_name, action):

    if frappe.flags.in_migrate or frappe.flags.in_install:
        return

    if not frappe.db.table_exists("tabAudit Log"):
        return

    try:
        frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": doctype_name,
            "document_name": document_name,
            "action": action,
            "user": frappe.session.user,
            "timestamp": now_datetime()
        }).insert(ignore_permissions=True)

    except Exception:
        pass