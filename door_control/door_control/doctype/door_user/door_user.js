// Copyright (c) 2024, Doug Mattingly and contributors
// For license information, please see license.txt

frappe.ui.form.on('user_access', {
    access: function(frm,cdt,cdn) {
        // toggle override if access toggled
        item = locals[cdt][cdn];
        item.override ? item.override = false : item.override = true;
        frm.refresh_field('override')
    },
    override: function(frm,cdt,cdn) {
        //xxx if override is turned off, copy the access from template, else just turn it back off
        item = locals[cdt][cdn];
        if (item.override) {
            item.override = false;  //override is set automatically if access is changed
        }
        else {
            copy_template(frm);
        }
    },
});

frappe.ui.form.on("door_user", {
	refresh(frm) {

    frm.add_custom_button(__("get card"), function() {
        frm.call('get_card', { arg1: "value" })
        .then(r => {
            debugger
            cur_frm.doc.card_resp = r.message[0]
        })
        frm.call('get_cards', { arg1: "value" })
        .then(r => {
            debugger
            cur_frm.doc.all_cards = r.message
        })
    }).css({"color":"white", "background-color": "blue", "font-weight": "800"});
	},

    'group': function(frm) {
        if (!cur_frm.doc.template){
            frappe.model.get_value('group', cur_frm.doc.group , 'template', function(r) {
                // console.log(r);
                
                cur_frm.doc.template = r.template;
                copy_template(frm);
                frm.refresh_field('template');
            });
        }
    },

    'template': function(frm) {
        copy_template(frm);
    },
    
    before_load: function(frm){
        copy_template(frm);
    },

});


function copy_template (frm) {
    frappe.db.get_list('controller', {
    filters: {'active': 1,},
    fields: ['name','doorname_1', 'doorname_2', 'doorname_3', 'doorname_4'],
    limit: 500,
    }).then(ctrl_list => {
            var ctrls = {}
            for (const ctrl of ctrl_list) {
                ctrls[ctrl.name] = ctrl;
            }
        frappe.db.get_list('access', {
        filters: {'parent': cur_frm.doc.template,},
        fields: ['name', 'access','name','name','name','controller','name','doornum'],
        limit: 500,
        }).then(r => {
            debugger // xxx why getting every other field?
            for (a of r) {
                var exist = cur_frm.doc.override.find(e => (e.doornum === a.doornum && e.controller === a.controller));
                if (!exist) {
                    var b = frm.add_child('override');
                    b.controller = a.controller; b.doornum=a.doornum; b.access = a.access; 
                }
                else {
                    // found the item.  copy access if not overriden
                    if (!exist.override) {
                        exist.access = a.access;
                    }
                }
            }
            // for (a of cur_frm.doc.override)
            // for (i=0; i<=cur_frm.doc.override.length-1; i++) {
            //     debugger
            //     a = cur_frm.doc.override[i];
            //     cur_frm.doc.override[i].door_name = ctrls[a.controller]['doorname_'+a.doornum];
            // }
            for (a of cur_frm.doc.override) {
                a.door_name = ctrls[a.controller]['doorname_'+a.doornum];
            }
            frm.refresh_field('override');
        });
    });
}