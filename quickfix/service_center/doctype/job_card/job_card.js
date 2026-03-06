frappe.ui.form.on("Job Card", {
    setup: function(frm) {
        frm.set_query("assigned_technician", function() {
            return {
                filters: {
                    status: "Active",
                    specialization: frm.doc.device_type
                }
            };
        });

    },

    onload: function(frm) {
        frappe.realtime.on("job_ready", function(data) {
            frappe.show_alert({
                message: `Job ${data.job_card} is Ready for Delivery!`,
                indicator: "green"
            });
        });
    },
    
    refresh: function(frm) {

        if (frm.doc.status === "Awaiting Customer Approval") {
            frm.dashboard.add_indicator("Awaiting Customer Approval", "orange");
        }
        else if (frm.doc.status === "In Repair") {
            frm.dashboard.add_indicator("In Repair", "blue");
        }
        else if (frm.doc.status === "Ready for Delivery") {
            frm.dashboard.add_indicator("Ready", "green");
        }
        else if (frm.doc.status === "Cancelled") {
            frm.dashboard.add_indicator("Cancelled", "red");
        }
        else if (frm.doc.status === "Delivered") {
            frm.dashboard.add_indicator("Delivered", "gray");
        }

        if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1) {

            frm.add_custom_button("Mark as Delivered", function() {

                frappe.call({
                    method: "quickfix.api.mark_delivered",
                    args: {
                        job_card: frm.doc.name
                    },
                    callback: function(r) {
                        if (!r.exc) {
                            frm.reload_doc();
                        }
                    }
                });

            });
        }

        if (frappe.boot.quickfix_shop_name) {
            frm.page.set_indicator(
                frappe.boot.quickfix_shop_name,
                "blue"
            );
        }

        if (frm.doc.docstatus === 0 && frm.doc.status !== "Cancelled") {
            frm.add_custom_button("Reject Job", function() {

                let dialog = new frappe.ui.Dialog({
                    title: "Reject Job",
                    fields: [
                        {
                            label: "Rejection Reason",
                            fieldname: "rejection_reason",
                            fieldtype: "Small Text",
                            reqd: 1          
                        }
                    ],
                    primary_action_label: "Submit",

                    primary_action(values) {
                        frappe.call({
                            method: "quickfix.api.reject_job",
                            args: {
                                job_card: frm.doc.name,
                                reason: values.rejection_reason
                            },
                            callback: function(r) {
                                if (!r.exc) {
                                    dialog.hide();   
                                    frm.reload_doc(); 
                                }
                            }
                        });
                    }
                });

                // Step 4 - Actually show the dialog
                dialog.show();

            }, "Actions");  
        }



        // // Transfer Technician
        //  if (!frappe.user.has_role("QF Manager")) {
        //     frm.set_df_property("customer_phone", "hidden", 1);
        // }


        if (frm.doc.docstatus === 0) {
            frm.add_custom_button("Transfer Technician", function() {
                frappe.prompt(
                    [
                        {
                            label: "New Technician",
                            fieldname: "new_technician",
                            fieldtype: "Link",
                            options: "Technician",  
                            reqd: 1
                        }
                    ],

                    function(values) {
                        frappe.confirm(
                            "Are you sure you want to transfer this technician?",
                            function() {
                                frappe.call({
                                    method: "quickfix.api.transfer_technician",
                                    args: {
                                        job_card: frm.doc.name,
                                        new_technician: values.new_technician
                                    },
                                    callback: function(r) {
                                        if (!r.exc) {
                                            frm.set_value(
                                                "assigned_technician",
                                                values.new_technician
                                            );
                                            frm.trigger("assigned_technician");
                                            frm.reload_doc();
                                        }
                                    }
                                });
                            }
                        );
                    },
                    "Transfer Technician",  // popup title
                    "Transfer"              // submit button label
                );

            }, "Actions");
        }
    },
    
    refresh: function(frm) {
    // SAME customization as Client Script above
    // but this time shipped as part of the app file
    if (!frappe.user.has_role("QF Manager")) {
        frm.set_df_property("customer_phone", "hidden", 1);
    }

},
    assigned_technician: function(frm) {
        if (!frm.doc.assigned_technician) return;
        frappe.call({
            method: "frappe.client.get_value",
            args: {
                doctype: "Technician",
                filters: { name: frm.doc.assigned_technician },
                fieldname: "specialization"
            },
            callback: function(r) {
                if (r.message) {
                    let tech_spec = r.message.specialization;
                    if (tech_spec !== frm.doc.device_type) {
                        frappe.msgprint(
                            " Technician specialization does not match device type."
                        );
                    }

                }
            }
        });

    },

});
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

