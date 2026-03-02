import frappe

def after_install():
    device_types = ["Mobile", "Laptop", "Tablet"]
    for d in device_types:
        if not frappe.db.exists("Device Type", d):

            frappe.get_doc({
                "doctype": "Device Type",
                "device_type_name": d
            }).insert(ignore_permissions=True)

    if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
        frappe.get_doc({
            "doctype": "QuickFix Settings",
            "shop_name": "QuickFix Shop",
            "manager_email": "admin@test.com"
        }).insert(ignore_permissions=True)

    frappe.msgprint("QuickFix installed successfully")


def before_uninstall():
    exists = frappe.db.exists(
        "Job Card",
        {"docstatus": 1}
    )

    if exists:
        raise frappe.ValidationError(
            "Cannot uninstall. Submitted Job Cards exist."
        )