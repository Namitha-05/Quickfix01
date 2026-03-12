import frappe

@frappe.whitelist()
def get(chart_name=None, chart=None, no_cache=None, filters=None,
        from_date=None, to_date=None, timespan=None,
        time_interval=None, heatmap_year=None):

    statuses = [
        "Draft",
        "Pending Diagnosis",
        "Awaiting Customer Approval",
        "In Repair",
        "Ready for Delivery",
        "Delivered",
        "Cancelled"
    ]

    labels = []
    values = []

    for status in statuses:
        count = frappe.db.count("Job Card", filters={"status": status})
        labels.append(status)
        values.append(count)

    return {
        "labels": labels,
        "datasets": [{"name": "Job Cards", "values": values}],
        "type": "bar"
    }