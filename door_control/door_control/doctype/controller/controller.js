// Copyright (c) 2024, Doug Mattingly and contributors
// For license information, please see license.txt

frappe.ui.form.on("controller", {
	refresh(frm) {

        frm.add_custom_button(__("Search controllers"), function() {
            frm.call('get_all_controllers', { arg1: "value" })
            .then(r => {
                debugger
                frappe.msgprint("found " + r.message + " NEW controllers")
                // frappe.set_route('List', 'controller')
                frappe.set_route('List', 'controller', { 'location': ['is','not set'] })
            })
        }).css({"color":"white", "background-color": "blue", "font-weight": "800"});
	},
});
