import frappe

def after_install():
    #  Create Device Types
    device_types = ["Mobile", "Laptop", "Tablet"]

    for d in device_types:
        if not frappe.db.exists("Device Type", {"device_type": d}):
            frappe.get_doc({
                "doctype": "Device Type",
                "device_type": d
            }).insert(ignore_permissions=True)

    #  Create QuickFix Settings (ONLY once, outside loop)
    if not frappe.db.exists("QuickFix Settings", "QuickFix Settings"):
        frappe.get_doc({
            "doctype": "QuickFix Settings",
            "shop_name": "QuickFix Shop",
            "manager_email": "admin@test.com"
        }).insert(ignore_permissions=True)

    # Add Property Setter → Make remarks bold in Job Card
    frappe.make_property_setter({
            "doctype":"Job Card",
            "fieldname":"remarks",
            "property":"bold",
            "value":"1",
            "property_type":"Check"
        })

    frappe.db.commit()

def before_uninstall():
    exists = frappe.db.exists(
        "Job Card",
        {"docstatus": 1}
    )

    if exists:
        raise frappe.ValidationError(
            "Cannot uninstall. Submitted Job Cards exist."
        )

    else:
        print("No job card is available")
    