import frappe

def rename_technician(old_name, new_name):
    frappe.rename_doc(
        "Technician",
        old_name,
        new_name,
        merge=False
    )


# merge=True will merge two existing Technician records into one.
# This can be dangerous because:
# - Data from one record may overwrite the other
# - Linked documents may get reassigned unexpectedly
# - Audit history may become confusing
# - It cannot be easily undone





def send_urgent_alert(job_card, manager):

    subject = f"Urgent Job Card {job_card} Needs Technician"

    message = f"""
    <h3>Urgent Job Card Alert</h3>

    <p>Job Card <b>{job_card}</b> is marked as <b>Urgent</b>
    but no technician has been assigned.</p>

    <p>Please assign a technician immediately.</p>
    """

    frappe.sendmail(
        recipients=[manager],
        subject=subject,
        message=message
    )
    

