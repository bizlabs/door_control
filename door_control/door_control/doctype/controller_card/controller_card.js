// Copyright (c) 2024, bizlabs and contributors
// For license information, please see license.txt

frappe.ui.form.on("controller_card", {
	refresh(frm) {

        frm.add_custom_button(__("Get All Cards"), function() {
            frm.call('get_all_cards', { arg1: "value" })
            .then(r => {
                debugger
                frappe.set_route(['List', 'controller_card'])
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
            ], (values) => {
                console.log(values.cardnum, values.doors);

                frm.call('add_card', { 'cardnum': values.cardnum, 'doors': values.doors, 'pin': '0'  })
                .then(r => {
                    debugger
                })

            })

        }).css({"color":"black", "background-color": "pink", "font-weight": "800"});

	},
    
   




    
});
