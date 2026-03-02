frappe.ready(function () {

    if (frappe.boot.quickfix_shop_name) {

        // console.log("Shop:", frappe.boot.quickfix_shop_name);

        $(".navbar .navbar-brand").text(
            frappe.boot.quickfix_shop_name
        );

    }

});