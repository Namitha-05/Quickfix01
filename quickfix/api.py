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