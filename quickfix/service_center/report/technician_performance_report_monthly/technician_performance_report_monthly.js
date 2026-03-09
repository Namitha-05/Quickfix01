// Copyright (c) 2026, Namitha and contributors
// For license information, please see license.txt

// frappe.query_reports["Technician Performance Report Monthly"] = {
// 	filters: [
// 		// {
// 		// 	"fieldname": "my_filter",
// 		// 	"label": __("My Filter"),
// 		// 	"fieldtype": "Data",
// 		// 	"reqd": 1,
// 		// },
// 	],
// };


frappe.query_reports["Technician Performance Report Monthly"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": "From Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": "To Date",
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1
        },
        {
            "fieldname": "technician",
            "label": "Technician",
            "fieldtype": "Link",
            "options": "Technician"
        }
    ]
};