import frappe

def execute(filters=None):

    columns = [
        {"label": "Technician", "fieldname": "technician", "fieldtype": "Data", "width": 200},
        {"label": "Jobs Completed", "fieldname": "jobs", "fieldtype": "Int", "width": 150},
        {"label": "Total Estimated Cost", "fieldname": "total_cost", "fieldtype": "Currency", "width": 150}
    ]

    conditions = ""

    if filters.get("technician"):
        conditions += " AND assigned_technician = %(technician)s"

    data = frappe.db.sql("""
        SELECT
            assigned_technician as technician,
            COUNT(name) as jobs,
            SUM(estimated_cost) as total_cost
        FROM
            `tabJob Card`
        WHERE
            creation BETWEEN %(from_date)s AND %(to_date)s
            AND status = 'Completed'
            {conditions}
        GROUP BY assigned_technician
    """.format(conditions=conditions), filters, as_dict=1)

    return columns, data