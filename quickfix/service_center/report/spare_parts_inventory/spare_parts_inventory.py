import frappe

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    summary = get_summary(data)
    return columns, data, None, None, summary



def get_columns():
    return [
        {
            "label"    : "Part Name",
            "fieldname": "part_name",
            "fieldtype": "Data",
            "width"    : 180
        },
        {
            "label"    : "Part Code",
            "fieldname": "part_code",
            "fieldtype": "Link",
            "options"  : "Spare Part",
            "width"    : 130
        },
        {
            "label"    : "Device Type",
            "fieldname": "compatible_device_type",
            "fieldtype": "Link",
            "options"  : "Device Type",
            "width"    : 130
        },
        {
            "label"    : "Stock Qty",
            "fieldname": "stock_qty",
            "fieldtype": "Float",
            "width"    : 100
        },
        {
            "label"    : "Reorder Level",
            "fieldname": "reorder_level",
            "fieldtype": "Float",
            "width"    : 120
        },
        {
            "label"    : "Unit Cost",
            "fieldname": "unit_cost",
            "fieldtype": "Currency",
            "width"    : 120
        },
        {
            "label"    : "Selling Price",
            "fieldname": "selling_price",
            "fieldtype": "Currency",
            "width"    : 120
        },
        {
            "label"    : "Margin %",
            "fieldname": "margin_percent",
            "fieldtype": "Percent",
            "width"    : 100
        }
    ]


def get_data(filters):
    parts = frappe.get_all(
        "Spare Part",
        fields=[
            "name",
            "part_name",
            "compatible_device_type",
            "stock_qty",
            "reorder_level",
            "unit_cost",
            "selling_price"
        ],
        order_by="part_name asc"
    )

    data            = []
    total_stock_qty = 0
    total_value     = 0

    for part in parts:
        # Margin % = ((selling - cost) / cost) * 100
        if part.unit_cost and part.unit_cost > 0:
            margin = (
                (part.selling_price - part.unit_cost)
                / part.unit_cost * 100
            )
        else:
            margin = 0

        # True if stock is at or below reorder level
        # This flag is used by JS formatter to color row red
        is_low_stock = (
            (part.stock_qty or 0) <= (part.reorder_level or 0)
        )

        row = {
            "part_name"             : part.part_name,
            "part_code"             : part.name,
            "compatible_device_type": part.compatible_device_type,
            "stock_qty"             : part.stock_qty    or 0,
            "reorder_level"         : part.reorder_level or 0,
            "unit_cost"             : part.unit_cost    or 0,
            "selling_price"         : part.selling_price or 0,
            "margin_percent"        : round(margin, 2),
            "is_low_stock"          : is_low_stock
        }

        # Running totals for total row
        total_stock_qty += part.stock_qty or 0
        total_value     += (part.stock_qty or 0) * (part.unit_cost or 0)

        data.append(row)

    # Add TOTAL row at the bottom
    data.append({
        "part_name"             : "TOTAL",
        "part_code"             : "",
        "compatible_device_type": "",
        "stock_qty"             : total_stock_qty,
        "reorder_level"         : "",
        "unit_cost"             : "",
        "selling_price"         : total_value,
        "margin_percent"        : "",
        "is_low_stock"          : False,
        "bold"                  : 1
    })

    return data


def get_summary(data):

    # Remove TOTAL row before calculating
    parts = [r for r in data if r.get("part_name") != "TOTAL"]

    total_parts   = len(parts)

    below_reorder = len([
        r for r in parts
        if r.get("is_low_stock")
    ])

    total_value = sum(
        (r.get("stock_qty") or 0) * (r.get("unit_cost") or 0)
        for r in parts
    )

    return [
        {
            "value"    : total_parts,
            "label"    : "Total Parts",
            "datatype" : "Int",
            "indicator": "blue"
        },
        {
            "value"    : below_reorder,
            "label"    : "Below Reorder Level",
            "datatype" : "Int",
            "indicator": "red"
        },
        {
            "value"    : total_value,
            "label"    : "Total Inventory Value",
            "datatype" : "Currency",
            "indicator": "green"
        }
    ]