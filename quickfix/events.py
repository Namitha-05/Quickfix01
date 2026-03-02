import frappe


def job_card_validate(doc, method):

    if len(doc.customer_phone or "") != 10:
        frappe.throw("doc_events: phone must be 10 digits")