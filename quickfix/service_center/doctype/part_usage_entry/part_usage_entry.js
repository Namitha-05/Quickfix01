frappe.ui.form.on("Part Usage Entry", {
    quantity: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if (row.quantity && row.unit_price) {
            let total = row.quantity * row.unit_price;
            frappe.model.set_value(
                cdt,
                cdn,
                "total_price",
                total
            );
        }
    }
});