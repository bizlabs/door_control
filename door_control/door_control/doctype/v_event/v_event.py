# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

@frappe.whitelist()
def get_recent(qty):
	event = frappe.new_doc('v_event')
	event.get_list({'page_length': qty})
	return True

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

	def db_insert(self, *args, **kwargs):
		pass

	def load_from_db(self):
		event_id = self.event_ndx
		ctrl = frappe.get_doc('controller',self.serial_number)
		card = ctrl.get_event(self.event_id)
		d = {
			'controller':	ctrl.serial_number, 
			'code':			card['card-number'],
			'start_date':	card['start-date'],
			'end_date':		card['end-date'],
			'doors':		str(card['doors']),
			'pin':			card['PIN'],

		}

		# d = get_info_user(self.name)
		super(Document, self).__init__(d)

	def db_update(self):
		pass

	
	def delete(self):
		frappe.msgprint("delete not implemented")

	@staticmethod
	def get_list(args):
		num_events = int(args['page_length'])
		eventset = []
		ctrls = frappe.get_all('controller')
		for ID in ctrls:
			ctrl = frappe.get_doc('controller',ID.name)
			events = ctrl.get_events()
			for i in range(events['last'], events['last']  - num_events, -1):
				event = ctrl.get_event(i)
				eventset.append({
					'event_ndx':	event['event-id'], 
					'dev_id':		event['device-id'], 
					'date':			event['timestamp'],
					'code':			event['card-number'],
					'event_type':	event['event-type-text'],
					'access_granted':	event['access-granted'],

					})
		return  eventset
		pass

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass

	# @frappe.whitelist()
	# def get_recent(self):
	# 	frappe.msgprint("getting recent...")
	# 	return self