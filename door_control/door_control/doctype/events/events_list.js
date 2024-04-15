frappe.listview_settings['events'] = {
    refresh: function(listview) {
        listview.page.add_inner_button("Download Events", function() {
            debugger

            frappe.prompt({
                label: 'Maximum number of records to retrieve ',
                fieldname: 'max',
                fieldtype: 'Int'
            }, (values) => {
                console.log(values.max);
                
		        frappe.msgprint("This will likely take a while.  I'll let you know when it's complete")
                frappe.call('door_control.door_control.doctype.events.events.get_events', 
                    { 'max': values.max  })
                    .then(r => {
                        // frappe.msgprint("done downloading events");
                        cur_list.refresh()
                        debugger
                    })
            })
        });;
    },
};