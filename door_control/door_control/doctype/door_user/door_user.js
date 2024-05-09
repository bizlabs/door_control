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
       
        frm.add_custom_button(__("Inspect this card on controller"), function() {
            frm.call('get_card', { arg1: "value" })
            .then(r => {
                debugger
                cur_frm.doc.card_resp = r.message;
                frm.refresh_field('card_resp');
            })
            frm.call('get_cards', { arg1: "value" })
            .then(r => {
                debugger
                cur_frm.doc.all_cards = r.message;
                frm.refresh_field('all_cards');
            })
        }).css({"color":"white", "background-color": "blue", "font-weight": "800"});

        frm.add_custom_button(__("import cards"), function() {
            frm.call('import_cards', { arg1: "value" })
            .then(r => {
                debugger
                console.log (r.message)
                frappe.set_route(['List', 'door_user'])
            })
        }).css({"color":"black", "background-color": "pink", "font-weight": "800"});

        frm.add_custom_button(__("upload this user"), function() {
            frappe.confirm('Are you sure to upload this user to all applicable controllers?',
            () => {
                frm.call('upload_one', { arg1: "value" })
                .then(r => {
                    debugger
                    console.log (r.message)
                    if (r.message != false) {
                        frappe.msgprint("user '" + r.message + "' uploaded successfully");
                    }
                    else {
                        frappe.msgprint("error: " + r.message);
                    }

                });
            }, () => {
                console.log("user cancelled upload")
            })
        }).css({"color":"white", "background-color": "firebrick", "font-weight": "800"});
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
        debugger
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
        debugger

        frm.call('get_access_by_template', { arg1: "value" })
        .then(r => {
            debugger
            if (r.message === undefined) {
                get_missing_access(frm);
            }
            else{
                accesses = r.message
                for (a of accesses) {
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
            }
            for (a of cur_frm.doc.override) {
                a.door_name = ctrls[a.controller]['doorname_'+a.doornum];
            }
            frm.refresh_field('override');
        })
    });
}

function get_missing_access (frm) {
    // get any missing door accesses (override field)
    // fills missing controller/door accesses (override field) when there is no template
    frappe.db.get_list('controller', {
        filters: {
            'active': 1,
        },
    fields: ['name','doorname_1', 'doorname_2', 'doorname_3', 'doorname_4'],
    limit: 500,
    }).then(r => {
        var ctrls = {};
        for (const ctrl of r) {
            for (let dn=1; dn <= 4; dn++){
                found = false;
                for (oride of frm.doc.override) {
                    if (oride.doornum == dn && oride.controller == ctrl.name) {
                        found = true;
                        // oride.doorname = ctrl['doorname_'+dn]
                        break;
                    }
                }
                if (!found){
                    var a = frm.add_child('override');
                    a.controller = ctrl.name; a.doornum=dn; a.door_name = ctrl['doorname_'+dn]; a.access=false;
                }
            }
        }  
        frm.refresh_field('override');
    });
}