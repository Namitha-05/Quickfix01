import frappe


def job_card_validate(doc, method):

        if not doc.customer_phone:
            frappe.msgprint("Doc: device modelrequired")