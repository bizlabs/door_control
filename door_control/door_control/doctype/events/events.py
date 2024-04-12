# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class events(Document):
	
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
						db_event = self.map_event(event)
						db_event.insert()
		# frappe.msgprint("downloaded " + str(numtot) + " events")
		return numtot
					
	def map_event(self, event):
		event_date = event['timestamp']
		db_event = frappe.get_doc ({
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
		})
		return db_event