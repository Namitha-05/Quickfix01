frappe.query_reports["Technician Performance Report"] = {

    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
            default: frappe.datetime.month_start()
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
            default: frappe.datetime.month_end()
        },
        {
            fieldname: "technician",
            label: "Technician",
            fieldtype: "Link",
            options: "Technician"
        }
    ],

    // Formatter - color code completion rate column
    // red if below 70%, green if 90% or above
    formatter: function(value, row, column, data, default_formatter) {

        // always call default formatter first
        value = default_formatter(value, row, column, data);

        if (column.fieldname === "completion_rate" && data) {

            if (data.completion_rate < 70) {
                // red - poor performance
                value = `<span style="color:red; font-weight:bold;">
                            ${value}
                         </span>`;

            } else if (data.completion_rate >= 90) {
                // green - excellent performance
                value = `<span style="color:green; font-weight:bold;">
                            ${value}
                         </span>`;
            }
        }

        return value;
    }

};