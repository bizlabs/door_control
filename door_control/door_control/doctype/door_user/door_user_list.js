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
    },
};