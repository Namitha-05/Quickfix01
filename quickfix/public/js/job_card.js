// // frappe.ui.form.on("Job Card", {
// //     refresh(frm) {
// //         console.log("Job Card form is loaded");
// //     }
// // });


// frappe.ui.form.on("Job Card", {

//     setup: function(frm) {
//         frm.set_query("assigned_technician", function() {
//             return {
//                 filters: {
//                     status: "Active",
//                     specialization: frm.doc.device_type
//                 }
//             };
//         });
//     },

//         onload: function(frm) {
//             frappe.realtime.on("job_ready", function(data) {
//                 frappe.show_alert({
//                     message: "Job is Ready for Delivery!",
//                     indicator: "green"
//                 });
//             });
//         },
//         refresh: function(frm) {
//         frm.dashboard.clear_indicators();

//         // DEBUG - remove after fixing
//         frappe.show_alert("Status: " + frm.doc.status + " | docstatus: " + frm.doc.docstatus);

//         if (frm.doc.status === "Pending Diagnosis") {
//             frm.dashboard.add_indicator("Pending Diagnosis", "orange");
//         } else if (frm.doc.status === "In Repair") {
//             frm.dashboard.add_indicator("In Repair", "blue");
//         } else if (frm.doc.status === "Ready for Delivery") {
//             frm.dashboard.add_indicator("Ready for Delivery", "green");
//         } else if (frm.doc.status === "Delivered") {
//             frm.dashboard.add_indicator("Delivered", "gray");
//         }

//         console.log("=== DEBUG ===");
//         console.log("status:", frm.doc.status);
//         console.log("docstatus:", frm.doc.docstatus);

//         if (frm.doc.status === "Ready for Delivery" && frm.doc.docstatus === 1) {
//             frm.add_custom_button("Mark as Delivered", function() {
//                 frm.set_value("status", "Delivered");
//                 frm.save();
//             });
//         }

//         if (frappe.boot.quickfix_shop_name) {
//             frm.page.set_title(frm.doc.name + " - " + frappe.boot.quickfix_shop_name);
//         }
//     },
//     assigned_technician: function(frm) {
//         if (frm.doc.assigned_technician) {
//             frappe.call({
//                 method: "frappe.client.get_value",
//                 args: {
//                     doctype: "Technician",
//                     filters: {
//                         name: frm.doc.assigned_technician
//                     },
//                     fieldname: "specialization"
//                 },
//                 callback: function(r) {
//                     if (r.message) {
//                         let tech_specialization = r.message.specialization;

//                         if (tech_specialization !== frm.doc.device_type) {
//                             frappe.msgprint({
//                                 title: "Warning",
//                                 message: "Technician specialization does not match Device Type!",
//                                 indicator: "orange"
//                             });
//                         }
//                     }
//                 }
//             });
//         }
//     },

//     validate: function(frm) {
//         if (!frm.doc.assigned_technician) {
//             frappe.throw("Please assign a technician before saving.");
//         }
//     }

// });


// frappe.ui.form.on("Part", {

//     quantity: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         let total = (row.quantity || 0) * (row.unit_price || 0);
//         frappe.model.set_value(cdt, cdn, "total_price", total);
//     },

//     unit_price: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         let total = (row.quantity || 0) * (row.unit_price || 0);
//         frappe.model.set_value(cdt, cdn, "total_price", total);
//     }

// });
