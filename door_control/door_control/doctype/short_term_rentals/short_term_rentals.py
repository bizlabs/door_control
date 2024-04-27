# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class short_term_rentals(Document):

	# @property
	# def vera_access(self):
	# 	return self.load_vera_access()

	@frappe.whitelist()
	def load_vera_access(self):
		vaccs = frappe.get_all('vera_access',
			filters={'room':self.name},
			fields=['slot','parent'])
		for vacc in vaccs:
			user = frappe.get_doc('door_user',vacc.parent)
			vacc['full_name'] = user.full_name
			vacc['user'] = vacc['parent']
			self.append('vera_access',vacc)
		# self.save()
		return self.vera_access

	@property
	def raw_pins(self):
		return self.get_pincodes()

	@property
	def door_num(self):
		ctrl = frappe.get_doc('controller',self.uhppote_controller)
		for i in range(1,5):
			if self.door_name == getattr(ctrl,'doorname_'+str(i)):
				return i
		return 0
		
	@frappe.whitelist()
	def get_pincodes(self):
		try:
			vacc = frappe.get_doc('vera_access',{'room':self.name})
		except:
			return None
		pins = vacc.get_pincodes()
		return pins
	
	# @frappe.whitelist()
	# def add_user(self):
	# 	vacc = frappe.get_doc('vera_access',{'room':self.name})
	# 	res = vacc.add_user()
	# 	return res