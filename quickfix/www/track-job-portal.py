import frappe

def get_context(context):

    # Get job id from URL
    job_id = frappe.form_dict.get("job_id")

    # Send empty values initially
    context.job = None
    context.error = None

    # If user entered job id
    if job_id:
        try:
            job = frappe.get_doc("Job Card", job_id)

            # Send job data to HTML
            context.job = job

        except frappe.DoesNotExistError:

            # If job id is wrong
            context.error = "Invalid Job ID"

    context.title = "Track Job Status"
    context.description = "Check the repair status of your device online"
    context.og_title = "QuickFix Job Tracking"