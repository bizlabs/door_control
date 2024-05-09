# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests, re

def remove_special_characters(s):
    """Remove all characters except letters, numbers, and spaces from a string."""
    return re.sub(r'[^a-zA-Z0-9\s]', '', s)

class vera_access(Document):

	def get_baseurl(self,type):
		settings = frappe.get_doc('doorctl_settings')
		room = frappe.get_doc('short_term_rentals',self.room)
		url = "http://" + settings.vera_ip + ":" + settings.vera_port
		url += "/data_request?id=" + type + "&DeviceNum=" + str(room.vera_device_number)
		url += "&serviceId=urn:micasaverde-com:serviceId:DoorLock1"
		return url

	def get_inserturl(self,slot):
		# user = frappe.get_doc('door_user',{'code':self.parent_doc.code})
		user = self.parent_doc
		url = self.get_baseurl('action')
		name = remove_special_characters(user.full_name)
		url += "&action=SetPin&UserCodeName=" + name
		url += "&newPin=" + str(user.code)
		url += "&user=" + str(slot)
		return url

	def get_pincodes(self):
		url = self.get_baseurl('variableget')
		url += "&Variable=PinCodes"
		r=requests.get(url)
		return r.text
	
	def add_user(self):
		'''find 1st available slot but don't add if already exists'''
		user = self.parent_doc
		this_pin = user.code
		pins = self.get_pincodes().split('\t')
		for x in range(30,0,-1):
			pin = pins[x][:-1] #remove trailing semi-colon
			pinobjs = pin.split(',')
			slot = pinobjs[0]; status = pinobjs[1]
			if status == '0':
				new_slot = slot
			else:
				code = pinobjs[4]; name = pinobjs[5] 
				if code == this_pin:
					frappe.throw ("pin already exists in vera hub")
		url = self.get_inserturl(new_slot)
		r = requests.get(url)
		if r.status_code != 200:
			frappe.throw("bad comm with vera hub")
		self.slot = new_slot
			# replace frappe.throw with return a flag so calling function can rollback changes (everywhere)


	def delete_user(self):
		if not self.slot:
			return
		url = self.get_baseurl('action')
		url += "&action=ClearPin&UserCode=" + self.slot
		r = requests.get(url)
		if r.status_code != 200:
			frappe.throw("bad comm with vera hub")
		return

	def update_user(self):
		'''requires delete and re-create'''
		pass

