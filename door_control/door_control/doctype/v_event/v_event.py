# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class v_event(Document):
	
	@frappe.whitelist()
	def get_events(self,nummax):
		numtot = numctl = 0
		ctrls = frappe.get_all('controller')
		for id in ctrls:
			numctl += 1
			db_events = frappe.get_all('events',filters={'dev_id':int(id.name)}, pluck='event_ndx')
			ctrl = frappe.get_doc('controller',id)
			events = ctrl.get_events()
			if events != None:   #xxx
				for ndx in range(events['first'],events['last']):
					if numtot+1 > nummax:
						return numtot
					if ndx not in db_events:
						numtot += 1
						event = ctrl.get_event(ndx)
						event_dict = self.map_event(event)
						db_event = frappe.get_doc (event_dict)
						db_event.insert()
		# frappe.msgprint("downloaded " + str(numtot) + " events")
		return numtot
					
	def map_event(self, event):
		event_date = event['timestamp']
		event_dict = {
			'doctype':		'events',
			'event_ndx':		event['event-id'],
			'dev_id':			event['device-id'],
			'access_granted':	event['access-granted'],
			'door':				str(event['door-id']),
			'code':				event['card-number'],
			'timestamp':		event_date,
			'reason':			event['event-reason-text'],
			'event_type':		event['event-type-text'],
			'direction':		event['direction-text'],
		}
		return event_dict

	def db_insert(self, *args, **kwargs):
		pass

	def load_from_db(self):
		parsed = self.name.split(':')
		ID = parsed[0]; eid = parsed[1]
		ctrl = frappe.get_doc('controller',ID)
		event = ctrl.get_event(eid)
		d = self.map_event(event)
		d.pop('doctype', None)
		d['controller'] = ctrl.location
		x = frappe.get_all('door_user', filters={'code': str(['code'])}, pluck='full_name')
		d['user'] = None if x==[] else x[0]
		d['door'] = getattr(ctrl, 'doorname_' + d['door'])

		super(Document, self).__init__(d)
		pass

	def db_update(self):
		pass

	
	def delete(self):
		frappe.msgprint("delete not implemented")

	@staticmethod
	def get_list(args):
		pass
		# xxx loop thru args.filters
		# eg args.filters[0][1] = field [2] = compare operator, [3] = condition to compare
		# eg ['v_event','timestamp', '>', some_date]
		# or ['v_event','timestamp', 'Between', [date1,date2]]
		# ignore other filters for now

		num_events = int(args['page_length'])
		eventset = []
		ctrls = frappe.get_all('controller')
		miss = 0
		for ID in ctrls: 
			ctrl = frappe.get_doc('controller',ID.name)
			events = ctrl.get_events()
			for i in range(events['last'], events['last']  - num_events, -1):
				event = ctrl.get_event(i)
				if not event:
					miss += 1
					continue
				eventset.append({
					'name': 		str(event['device-id']) + ":" + str(event['event-id']),
					'event_ndx':	event['event-id'], 
					'dev_id':		event['device-id'], 
					'timestamp':	event['timestamp'],
					'code':			event['card-number'],
					'event_type':	event['event-type-text'],
					'access_granted':	event['access-granted'],
					'door':			str(event['door-id']),
					})
		if miss > 0:
			frappe.msgprint(str(miss) + " events were skipped because controller timed out")
		return  eventset

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass