// Copyright (c) 2024, bizlabs and contributors
// For license information, please see license.txt

frappe.ui.form.on('access', {
    refresh:function(frm, cdt, cdn) {
    }
}); 

frappe.ui.form.on("door_template", {
	refresh(frm) {
        cur_frm.fields_dict['access'].grid.wrapper.find('.btn-open-row').hide();
        cur_frm.fields_dict['access'].grid.grid_buttons.addClass('hidden');
        
	},


    before_load: function(frm){
        //get door accesses for each door on each controller

        frappe.db.get_list('controller', {
            filters: {
                'active': 1,
            },
        fields: ['name','doorname_1', 'doorname_2', 'doorname_3', 'doorname_4'],
        limit: 500,
        }).then(r => {
            var ctrls = {}
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
                else {
                    ctrls[ctrl.name] = ctrl;
                }
            }  
            
            for (a of cur_frm.doc.access) {
                a.door_name = ctrls[a.controller]['doorname_'+a.doornum]
            }
        });
    },

});
