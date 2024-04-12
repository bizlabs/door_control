// Copyright (c) 2024, bizlabs and contributors
// For license information, please see license.txt

frappe.ui.form.on("events", {
	refresh(frm) {
        frm.add_custom_button(__("download events"), function() {

            frappe.prompt({
                label: 'Maximum number of records to retrieve ',
                fieldname: 'nummax',
                fieldtype: 'Int'
            }, (values) => {
                console.log(values.nummax);

                frm.call('get_events', { 'nummax': values.nummax })
                .then(r => {
                    debugger
                    frappe.msgprint("done downloading events")
                    frappe.set_route('List', 'events')
                })
            })
            

        }).css({"color":"white", "background-color": "blue", "font-weight": "800"});
	},
});
