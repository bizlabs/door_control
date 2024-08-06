// Copyright (c) 2024, Doug Mattingly and contributors
// For license information, please see license.txt

frappe.ui.form.on("controller", {
	refresh(frm) {
        frm.add_custom_button(__("send swipe"), function() {
            frm.call('send_swipe', { arg1: "value" })
            .then(r => {
                debugger
                console.log (r.message)
            })
        }).css({"color":"black", "background-color": "pink", "font-weight": "800"});

        frm.add_custom_button(__("Search controllers"), function() {
            frm.call('search_new_controllers', { arg1: "value" })
            .then(r => {
                debugger
                frappe.msgprint("found " + r.message + " NEW controllers")
                // frappe.set_route('List', 'controller')
                frappe.set_route('List', 'controller', { 'location': ['is','not set'] })
            })
        }).css({"color":"white", "background-color": "blue", "font-weight": "800"});


        frm.add_custom_button(__("Add Card"), function() {
            debugger
            frappe.prompt([
                {
                    label: 'card number',
                    fieldname: 'cardnum',
                    fieldtype: 'Data'
                },
                {
                    label: '4 doors permissions (eg, 1011)',
                    fieldname: 'doors',
                    fieldtype: 'Data'
                },
                {
                    label: 'pin',
                    fieldname: 'pin',
                    fieldtype: 'Data'
                },
            ], (values) => {
                console.log(values.cardnum, values.doors);

                frm.call('add_card_for_testing', { 'cardnum': values.cardnum, 'dstr': values.doors, 'pin': values.pin  })
                .then(r => {
                    debugger
                })

            })

        }).css({"color":"black", "background-color": "pink", "font-weight": "800"});
	},
});
