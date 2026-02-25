import frappe

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