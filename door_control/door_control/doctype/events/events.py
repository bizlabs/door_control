# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime

@frappe.whitelist()
def get_events(max):
	event = frappe.new_doc('events')
	return event.get_events(int(max))

class events(Document):
	
	@property
	def controller(self):
		try:
			ctrl = frappe.get_doc('controller',str(self.dev_id))
		except:
			return # no controller found
		return ctrl.location

	@property
	def user(self):
		try:
			user = frappe.get_all('door_user',filters={'code':self.code},fields=['full_name'])[0]
			# user = frappe.get_doc('door_user',usernames[0])
		except:
			return # no user found
		return user.full_name
	
	@property
	def door_name(self):
		try:
			ctrl = frappe.get_doc('controller',str(self.dev_id))
		except:
			return # no controller found
		return self.door + "- " + getattr(ctrl,'doorname_' + str(self.door))
	
	@frappe.whitelist()
	def get_events(self,max):
		numtot = numctl = miss = 0
		ctrls = frappe.get_all('controller')
		for id in ctrls:
			numctl += 1
			db_events = frappe.get_all('events',filters={'dev_id':int(id.name)}, pluck='event_ndx')
			ctrl = frappe.get_doc('controller',id)
			events = ctrl.get_events()
			# frappe.publish_progress(50.0, title='processing...', description='desciption')
			if events != None:   #xxx
				for ndx in range(events['first'],events['last']):
					qty = events['last'] - events['first']
					if numtot+1 > max:
						break
					if ndx not in db_events:
						numtot += 1
						event = ctrl.get_event(ndx)
						if not event:
							miss += 1
							continue
						db_event = self.map_event(event)
						db_event.insert()
		# frappe.msgprint("downloaded " + str(numtot) + " events")
		msg = str(miss) + " of " + str(numtot) + " requested events skipped because controller time-out"
		frappe.msgprint(msg)
		return numtot
					
	def map_event(self, event):
		event_date = event['timestamp']
		db_event = frappe.get_doc ({
			'doctype':		'events',
			'event_ndx':		event['event-id'],
			'dev_id':			event['device-id'],
			'access_granted':	event['access-granted'],
			'door':				str(event['door-id']),
			'code':				str(event['card-number']),
			'timestamp':		datetime.strptime(event_date, "%Y-%m-%d %H:%M:%S %Z"),
			'reason':			event['event-reason-text'],
			'event_type':		event['event-type-text'],
			'direction':		event['direction-text'],
		})
		return db_event