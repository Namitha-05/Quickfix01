import frappe
from frappe.utils import date_diff

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data)
    summary = get_summary(data)
    return columns, data, None, chart, summary


def get_columns(filters):
    # Base columns
    cols = [
        {
            "label": "Technician",
            "fieldname": "technician",
            "fieldtype": "Link",
            "options": "Technician",
            "width": 180
        },
        {
            "label": "Total Jobs",
            "fieldname": "total_jobs",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Completed",
            "fieldname": "completed",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "label": "Avg Turnaround Days",
            "fieldname": "avg_turnaround",
            "fieldtype": "Float",
            "width": 160
        },
        {
            "label": "Revenue",
            "fieldname": "revenue",
            "fieldtype": "Currency",
            "width": 130
        },
        {
            "label": "Completion Rate %",
            "fieldname": "completion_rate",
            "fieldtype": "Percent",
            "width": 140
        }
    ]

    # Dynamic columns - one per Device Type fetched at runtime
    device_types = frappe.get_all("Device Type", fields=["name"])
    for dt in device_types:
        cols.append({
            "label": dt.name,
            "fieldname": dt.name.lower().replace(" ", "_"),
            "fieldtype": "Int",
            "width": 100
        })

    return cols


def get_data(filters):
    conditions = ""
    values = {}

    # Date filters - no table alias prefix
    if filters.get("from_date"):
        conditions += " AND creation >= %(from_date)s"
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND creation <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    # Optional technician filter
    technician_filter = {}
    if filters.get("technician"):
        technician_filter["name"] = filters.get("technician")

    # frappe.get_list respects permissions
    # QF Technician sees only their own row
    # frappe.get_all would show all technicians to everyone
    technicians = frappe.get_list(
        "Technician",
        filters=technician_filter,
        fields=["name", "technician_name"]
    )

    # Device types for dynamic columns
    device_types = frappe.get_all("Device Type", fields=["name"])

    data = []

    for tech in technicians:

        # Get all job cards for this technician
        job_cards = frappe.db.sql("""
            SELECT
                name,
                status,
                creation,
                delivery_date,
                final_amount,
                device_type
            FROM `tabJob Card`
            WHERE
                assigned_technician = %(technician)s
                {conditions}
        """.format(conditions=conditions),
        dict(values, technician=tech.name),
        as_dict=True)

        total_jobs = len(job_cards)

        # Skip technicians with no jobs
        if total_jobs == 0:
            continue

        # Count delivered jobs as completed
        completed = len([
            j for j in job_cards
            if j.status == "Delivered"
        ])

        # Average turnaround days
        turnaround_list = []
        for j in job_cards:
            if j.delivery_date and j.creation:
                days = date_diff(j.delivery_date, j.creation)
                turnaround_list.append(days)

        avg_turnaround = (
            sum(turnaround_list) / len(turnaround_list)
            if turnaround_list else 0
        )

        # Revenue from delivered jobs only
        revenue = sum(
            j.final_amount or 0
            for j in job_cards
            if j.status == "Delivered"
        )

        # Completion rate percentage
        completion_rate = (
            completed / total_jobs * 100
            if total_jobs else 0
        )

        row = {
            "technician": tech.name,
            "total_jobs": total_jobs,
            "completed": completed,
            "avg_turnaround": round(avg_turnaround, 1),
            "revenue": revenue,
            "completion_rate": round(completion_rate, 2)
        }

        # Dynamic device type counts per technician
        for dt in device_types:
            fieldname = dt.name.lower().replace(" ", "_")
            count = len([
                j for j in job_cards
                if j.device_type == dt.name
            ])
            row[fieldname] = count

        data.append(row)

    return data


def get_chart(data):
    if not data:
        return None

    labels = [row.get("technician") for row in data]
    total_jobs = [row.get("total_jobs", 0) for row in data]
    completed = [row.get("completed", 0) for row in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Total Jobs",
                    "values": total_jobs
                },
                {
                    "name": "Completed",
                    "values": completed
                }
            ]
        },
        "type": "bar",
        "colors": ["blue", "green"]
    }


def get_summary(data):
    if not data:
        return []

    total_jobs = sum(row.get("total_jobs", 0) for row in data)
    total_revenue = sum(row.get("revenue", 0) for row in data)

    # Best technician has highest completion rate
    best = max(data, key=lambda x: x.get("completion_rate", 0))

    return [
        {
            "value": total_jobs,
            "label": "Total Jobs",
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": total_revenue,
            "label": "Total Revenue",
            "datatype": "Currency",
            "indicator": "green"
        },
        {
            "value": best.get("technician"),
            "label": "Best Technician",
            "datatype": "Data",
            "indicator": "green"
        }
    ]