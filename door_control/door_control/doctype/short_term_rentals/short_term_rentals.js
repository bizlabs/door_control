// Copyright (c) 2024, bizlabs and contributors
// For license information, please see license.txt

frappe.ui.form.on("short_term_rentals", {
	'uhppote_controller': async function (frm) { 
        // doors = ["door1", "door2", "door3", "door4"];
        debugger

        var controllerName = frm.doc.uhppote_controller;
        if (controllerName) {
            frappe.db.get_doc('controller', controllerName)
                .then(ctrl => {
                    debugger
                    doors = [];
                    for (i=1; i<=4; i++){
                        doors[i-1] = ctrl['doorname_'+i];
                    }
                    cur_frm.set_df_property('door_name', 'options', doors);
                    console.log(doc);
                })
                .catch(err => {
                    // Handle any errors
                    console.error(err);
                });
        }

	},

    refresh(frm) {
        frm.add_custom_button(__("Load Users"), function() {
            debugger
            frm.call('load_vera_access', { arg1: "value" })
            .then(r => {
                // window.location.reload();
                debugger
                // frappe.msgprint(r.message)
                // console.log (r.message)
            })
        }).css({"color":"black", "background-color": "pink", "font-weight": "800"});
    },

    onload(frm) {
        frm.call('load_vera_access', { arg1: "value" })
        .then(r => {
            // frappe.msgprint(r.message)
            // console.log (r.message)
        })
    },

});

// frappe.ui.form.on('vera_access', {
//     vera_access_add: function(frm, cdt, cdn) {
//     item = locals[cdt][cdn];
//     frm.call('add_user', { arg1: "value" })
//     .then(r => {
//         debugger
//         frappe.msgprint(r.message)
//         console.log (r.message)
//     })
//     frm.refresh_field('vera_access');
//    },
// })