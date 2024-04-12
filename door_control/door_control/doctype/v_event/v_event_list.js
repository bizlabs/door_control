

frappe.listview_settings['v_event'] = {
    refresh: function(listview) {
        listview.page.add_inner_button("Get Recent", function() {
            frappe.call('door_control.door_control.doctype.v_event.v_event.get_recent', { 'qty': 6 })
                .then(r => {
                    debugger
                    frappe.msgprint("done downloading events")
                    frappe.set_route('List', 'v_event')
                })
        });;
    },
};

//frappe.call('frappe.core.doctype.user.user.get_all_rolesget_recent', { 'nummax': values.nummax })
