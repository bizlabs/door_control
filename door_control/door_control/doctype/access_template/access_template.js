// Copyright (c) 2024, bizlabs and contributors
// For license information, please see license.txt

frappe.ui.form.on("access_template", {
	refresh(frm) {
	},

    onload: function(frm){
        //get door accesses for each door on each controller
        frappe.db.get_list('controller', {
            filters: {
                'active': 1,
            },
        fields: ['name','doorname_1', 'doorname_2', 'doorname_3', 'doorname_4'],
        limit: 500,
        }).then(r => {
            console.log(r);
            for (const ctrl of r) {

                if (frm.is_new()) {
                    var a = frm.add_child('access');
                    a.controller = ctrl.name; a.doornum=1; a.door_name = ctrl.doorname_1;
                    var a = frm.add_child('access');
                    a.controller = ctrl.name; a.doornum=2; a.door_name = ctrl.doorname_2;
                    var a = frm.add_child('access');
                    a.controller = ctrl.name; a.doornum=3; a.door_name = ctrl.doorname_3;
                    var a = frm.add_child('access');
                    a.controller = ctrl.name; a.doornum=4; a.door_name = ctrl.doorname_4;
                    frm.refresh_field('access');
                }
            }  
        });
    },
 });
