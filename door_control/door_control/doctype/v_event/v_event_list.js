

frappe.listview_settings['v_event'] = {
    refresh: function(listview) {
        listview.page.add_inner_button("Get Recent", function() {
            // debugger
            end = new Date();
            start = new Date (end.getTime() - 2*24*3600*1000);
            max = 30

            frappe.prompt([
                {
                    label: 'Start Date',
                    fieldname: 'start',
                    fieldtype: 'Date',
                    default:    start
                },
                {
                    label: 'End Date',
                    fieldname: 'end',
                    fieldtype: 'Date',
                    default:    end
                },
                {
                    label: 'Maximum # of Events to Retrieve per controller',
                    fieldname: 'max',
                    fieldtype: 'Int',
                    default:    max
                },
            ], (values) => {
                console.log(values.start, values.end, values.max);
                listview.page_length = values.max;
                debugger 
                frappe.route_options = {
                    "timestamp": ["between", [new Date(values.start), new Date(values.end)]]
                };
                cur_list.refresh();
                
        

                // pydate.timestamp()*1000
                // Date.parse(jsdate)
                //     //calc and set date limits and page_length
                //     "session_type": ["=", "Individual"]
                // };
    
                // frappe.call('door_control.door_control.doctype.v_event.v_event.get_recent', 
                //     { 'start':start, 'end':end, 'max': max  })
                //     .then(r => {
                //         // debugger
                //     })
            })
            



        });;
    },
};

//frappe.call('frappe.core.doctype.user.user.get_all_rolesget_recent', { 'nummax': values.nummax })
