import frappe
from frappe.client import get_count
from frappe.utils import now_datetime
from frappe.utils import today, now
from frappe import _
import uuid

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


    
# @frappe.whitelist()
# def get_status_chart_data():
    
#     result = frappe.db.sql("""
#         SELECT
#             status,
#             COUNT(name) as count
#         FROM `tabJob Card`
#         WHERE
#             status IS NOT NULL
#             AND status != ''
#         GROUP BY status
#         ORDER BY count DESC
#     """, as_dict=True)

#     labels = [r.status for r in result]
#     values = [r.count  for r in result]

#     return {
#         "labels": labels,
#         "datasets": [
#             {
#                 "name"  : "Job Count",
#                 "values": values
#             }
#         ]
#     }


@frappe.whitelist()
def get_status_chart_data():

    # Step 1: Define cache key
    # This is the name/label for our cached data
    cache_key = "quickfix:status_chart_data"

    # Step 2: Check if data already in cache
    cached_data = frappe.cache.get_value(cache_key)

    if cached_data:
        # Data found in cache
        # Return immediately without hitting database
        print("Returning from CACHE")
        return cached_data

    # Step 3: Cache miss - data not in cache
    # Must run SQL query
    print("Cache MISS - running SQL query")

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
     
        chart_data = {
        "labels": labels,
        "datasets": [
            {
                "name"  : "Job Count",
                "values": values
            }
        ]
    }

    # Step 4: Save result in cache for 300 seconds
    frappe.cache.set_value(
        cache_key,        # name of cache item
        chart_data,       # data to store
        expires_in_sec=300  # auto delete after 300s
    )
    print("Data saved to cache for 300 seconds")

    return chart_data




@frappe.whitelist()
def send_ready_email(job_card):
    frappe.enqueue(
        "quickfix.tasks.send_job_ready_email",
        job_card=job_card,
        queue="short"
    )

    return "Email job queued"




def generate_monthly_revenue_report():
    frappe.log_error(
        "Monthly revenue report job executed",
        "Scheduler Test"
    )

def failing_job():
    raise Exception("Intentional failure")




def check_low_stock():
    start = today() + " 00:00:00"
    end = today() + " 23:59:59"
    last_run = frappe.db.get_value(
        "Audit Log",
        {
            "action": "low_stock_check",
            "timestamp": ["between", [start, end]]
        },
        "name"
    )
    if last_run:
        print("Already ran today")
        return

    print("Checking low stock items...")

    frappe.get_doc({
        "doctype": "Audit Log",
        "action": "low_stock_check",
        "doctype_name": "System",
        "document_name": "Daily Low Stock Check",
        "user": "Administrator",
        "timestamp": now()
    }).insert(ignore_permissions=True)

    frappe.db.commit()
    print("Job completed")




@frappe.whitelist(allow_guest=True)
def get_job_summary():
    job_card_name = frappe.form_dict.get("job_card_name")

    if not frappe.db.exists("Job Card", job_card_name):
        frappe.response["http_status_code"] = 404
        return {"error": "Not found"}

    doc = frappe.get_doc("Job Card", job_card_name)

    return {
        "job_card": doc.name,
        "customer": doc.customer,
        "status": doc.status,
        "posting_date": doc.posting_date
    }

def cancel_old_draft_job_cards():
    frappe.db.sql("""
        UPDATE `tabJob Card`
        SET status = 'Cancelled'
        WHERE docstatus = 0
        LIMIT 1000
    """)
    frappe.db.commit()
    print("1000 draft job cards cancelled")





def insert_logs_slow():

    for i in range(500):

        doc = frappe.get_doc({
            "doctype": "Audit Log",
            "doctype_name": "Job Card",
            "document_name": f"DOC-{i}",
            "action": "Slow Insert",
            "user": "Administrator",
            "timestamp": now()
        })

        doc.insert()

    frappe.db.commit()

@frappe.whitelist()
def bulk_insert_audit_logs():
    import time
    
    start = time.time()
    records = []
    for i in range(50):
        records.append([
            f"BULK-TESTS-{frappe.generate_hash(length=6)}",
            "Job Card",
            f"TEST-{i}",
            "bulk_TEST",
            "Administrator"
        ])
    frappe.db.bulk_insert(
        "Audit Log",
        fields=["name", "doctype_name", "document_name", "action", "user"],
        values=records
    )
    frappe.db.commit()
    bulk_time = time.time() - start
    frappe.log_error(f"Bulk insert time: {bulk_time}", "Benchmark")
    return f"Done in {bulk_time} seconds"