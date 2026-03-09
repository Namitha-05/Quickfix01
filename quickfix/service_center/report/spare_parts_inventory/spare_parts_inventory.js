frappe.query_reports["Spare Parts Inventory"] = {
    filters: [],
    formatter: function(value, row, column, data, default_formatter) {

        // Always apply default first
        // adds ₹ symbol, % sign etc
        value = default_formatter(value, row, column, data);

        // Red text for low stock rows
        if (data && data.is_low_stock) {
            value = `<span style="color: red; font-weight: bold;">
                        ${value}
                     </span>`;
        }

        // Bold for TOTAL row
        if (data && data.part_name === "TOTAL") {
            value = `<span style="font-weight: bold;">
                        ${value}
                     </span>`;
        }

        return value;
    }
};