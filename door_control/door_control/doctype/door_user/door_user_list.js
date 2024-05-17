frappe.listview_settings['door_user'] = {
    refresh: function(listview) {
        listview.page.add_inner_button("UPload ALL", function() {
            debugger

            frappe.prompt({
                label: 'Type "confirm" to upload ALL named users.   (Does not include imported users that still have not been named)',
                fieldname: 'confirm',
                fieldtype: 'Data'
            }, (values) => {
                console.log(values.confirm);
                if (values.confirm == "confirm") {
                    frappe.call('door_control.door_control.doctype.door_user.door_user.upload_all', 
                        { 'arg': values.confirm  })
                        .then(r => {
                            // console.log(r.message)
                            num_uploaded = r.message
                            frappe.msgprint("Uploaded " + num_uploaded + " users");
                            cur_list.refresh()
                            debugger
                        })
                }
                else {
                    frappe.msgprint("You did not type 'confirm' so the operation was cancelled (case sensitive)")
                    console.log("upload cancelled")
                }
            })
        }).css({"color":"white", "background-color": "firebrick", "font-weight": "800"});


        listview.page.add_inner_button("read card", function() {
            frappe.msgprint("scan card now...")
            frappe.call('door_control.door_control.doctype.door_user.door_user.read_card', 
            { 'arg': ""  })
            .then(r => {
                console.log(r.message)
                debugger
                if (!r.message) {
                    frappe.msgprint ("no card scanned");
                }
                else {
                    debugger
                    event = r.message;
                    frappe.call({
                        method: "frappe.client.get",
                        args: {
                            doctype: "controller",
                            name: r.message['device-id']
                        },
                        callback: function(r) {
                            debugger
                            var ctrl = r.message;
                            dname = ctrl["doorname_"+event['door-id']];
                            devname = ctrl.location;
                            msg = "card: "+event['card-number'] + ", ";
                            msg += "at door "+dname + ", ";
                            msg += "on controller: "+devname;
                            frappe.msgprint(msg);
                            frappe.msgprint("is this the right scan?")
                            frappe.confirm('Is this the right scan?',
                            () => {
                                var user = frappe.model.get_new_doc("door_user");
                                user.code = event['card-number'];
                                frappe.set_route("Form", 'door_user', user.name);
                            }, () => {
                                frappe.msgprint("Press the 'read card' button to try again")
                            })
                        }
                    });
                    
                    

                }
            });
        }).css({"color":"white", "background-color": "blue", "font-weight": "800"});


        listview.page.add_inner_button("TEST read card", function() {
            event = {'card-number':"5551212"} 
            debugger

            var user = frappe.model.get_new_doc("door_user");
            user.code = "555";
        
            // Open the form for the new document
            frappe.set_route("Form", 'door_user', user.name);
        }).css({"color":"white", "background-color": "red", "font-weight": "800"});

    },
};
