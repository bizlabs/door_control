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
			'code':				str(event['card-number']),
			'timestamp':		datetime.strptime(event_date, "%Y-%m-%d %H:%M:%S %Z"),
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
		num_events = int(args['page_length'])
		eventset = []
		ctrls = frappe.get_all('controller')
		miss = 0
		for ID in ctrls: 
			ctrl = frappe.get_doc('controller',ID.name)
			events = ctrl.get_events()
			if not events:
				continue
			#find index range given date range (events, dates)
			#estimate from date range of first to last and assume slope
			start_ndx, end_ndx = get_range(ctrl, events, args)
			start_ndx = max(start_ndx,end_ndx-num_events)
			for i in range(end_ndx, start_ndx, -1):
				event = ctrl.get_event(i)
				if not event:
					miss += 1
					continue
				eventset.append({
					'name': 		str(event['device-id']) + ":" + str(event['event-id']),
					'event_ndx':	event['event-id'], 
					'dev_id':		event['device-id'], 
					'timestamp':	datetime.strptime(event['timestamp'], "%Y-%m-%d %H:%M:%S %Z"),
					# 'timestamp':	event['timestamp'],
					'code':			str(event['card-number']),
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

	
def get_range(ctrl,events,args):
	'''return the index of the end of the range based on end_date'''
	
	if args.filters:
		filter = args.filters[0] #xxx filter[0] gives error if there are no filters!
		if filter[1] == 'timestamp' and filter[2] == 'Between' and filter[3]:
			start_date_str = filter[3][0]
			end_date_str = filter[3][1]
		else:
			return 1, events['last'] #no filter
	else:
		return 1, events['last'] #no filter
	
	date1 = get_date(ctrl,events['first'])
	date2 = get_date(ctrl,events['last'])
	totdays = (date2-date1).days
	numevents = events['last']-events['first']
	slope = float(numevents / totdays)
	end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
	end_date = date_in_range(end_date, date1, date2)
	# end_date = end_date if end_date < date2 else date2
	end_ndx = interpolate(ctrl, end_date, date1, slope)
	start_date = datetime.strptime(start_date_str,'%Y-%m-%d')
	start_date = date_in_range(start_date, date1, date2)
	# start_date = start_date if start_date > date1 else date1
	start_ndx = interpolate(ctrl, start_date, date1, slope)
	return start_ndx, end_ndx

def interpolate(ctrl, test_date, date1, slope):
	xdays = (test_date - date1).days
	eventnum = int(round(xdays * slope))

	xdate = get_date(ctrl,eventnum)
	while xdate < test_date:
		eventnum += 1
		xdate = get_date(ctrl,eventnum)
	while xdate > test_date:
		eventnum -= 1
		xdate = get_date(ctrl,eventnum)

	return eventnum

def get_date(ctrl,ndx):
	event = ctrl.get_event(ndx)
	if not event:
		frappe.throw("error retreiving ndx = " + str(ndx))
	datestr = event['timestamp']
	date = datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S %Z")
	return date

def date_in_range(x, d1, d2):
	if x < d1:
		return d1
	elif x > d2:
		return d2
	else:
		return x