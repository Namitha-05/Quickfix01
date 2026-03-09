import frappe
from frappe.client import get_count
from frappe.utils import now_datetime

@frappe.whitelist()
def share_job_card(job_card_name, user_email):

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.throw("Job Card does not exist")

    frappe.share.add(
        doctype="Job Card",
        name=job_card_name,
        user=user_email,
        read=1,
        write=0,
        submit=0,
        share=0
    )
    return "Job Card shared successfully"



@frappe.whitelist()
def manager_only_action():
    frappe.only_for("QF Manager")
    return "This is only if manager role is there.It is present"


@frappe.whitelist()
def get_job_cards_unsafe():
    return frappe.get_all("Job Card")


@frappe.whitelist()
def get_job_cards_safe():
    user = frappe.session.user
    roles = frappe.get_roles(user)

    job_cards = frappe.get_list(
        "Job Card",
        fields=["name", "customer_name", "customer_phone", "customer_email", "status"]
    )

    if "QF Manager" not in roles:
        for jc in job_cards:
            jc.pop("customer_phone", None)
            jc.pop("customer_email", None)

    return job_cards



@frappe.whitelist()
def custom_get_count(doctype, filters=None, debug=False, cache=False):
    frappe.get_doc({
        "doctype": "Audit Log",
        "doctype_name": doctype,
        "action": "count_queried",
        "user": frappe.session.user,
        "timestamp":now_datetime(),
    }).insert(ignore_permissions=True)

    frappe.db.commit() 
    # frappe.msgprint("Custom override running")


    return get_count(doctype, filters, debug, cache)  


@frappe.whitelist()
def mark_delivered(job_card):
    doc = frappe.get_doc("Job Card", job_card)
    doc.status = "Delivered"
    doc.save()
    frappe.db.commit()
    return "Delivered"

@frappe.whitelist()
def reject_job(job_card, reason):
    doc = frappe.get_doc("Job Card", job_card)
    doc.status = "Cancelled"
    doc.rejection_reason = reason
    doc.save()
    frappe.db.commit()
    return "Cancelled"
    
@frappe.whitelist()
def transfer_technician(job_card, new_technician):
    doc = frappe.get_doc("Job Card", job_card)
    doc.assigned_technician = new_technician
    doc.save()
    frappe.db.commit()
    return "Transferred"

@frappe.whitelist()
def mark_ready_for_delivery(job_card):
    doc = frappe.get_doc("Job Card", job_card)
    doc.status = "Ready for Delivery"
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return "success"


    
@frappe.whitelist()
def get_status_chart_data():
    
    result = frappe.db.sql("""
        SELECT
            status,
            COUNT(name) as count
        FROM `tabJob Card`
        WHERE
            status IS NOT NULL
            AND status != ''
        GROUP BY status
        ORDER BY count DESC
    """, as_dict=True)

    labels = [r.status for r in result]
    values = [r.count  for r in result]

    return {
        "labels": labels,
        "datasets": [
            {
                "name"  : "Job Count",
                "values": values
            }
        ]
    }



@frappe.whitelist()
def send_ready_email(job_card):
    frappe.enqueue(
        "quickfix.tasks.send_job_ready_email",
        job_card=job_card,
        queue="short"
    )

    return "Email job queued"