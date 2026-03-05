import frappe

# get_context() is automatically called by Frappe
# when someone opens /track-job
# context = dictionary used to send data to HTML

def get_context(context):

    # Get job_id from URL
    # Example:
    # /track-job?job_id=JC-0001
    job_id = frappe.form_dict.get("job_id")

    # Always send shop name manually to HTML
    # (Even though we can use Jinja method,
    #  this shows how context works)
    context.shop = frappe.db.get_single_value(
        "Quickfix Settings",
        "shop_name"
    )

    # If user entered a job_id
    if job_id:
        try:
            job = frappe.get_doc("Job Card", job_id)
            context.job = job

        except frappe.DoesNotExistError:
            context.error = "Invalid Job ID"