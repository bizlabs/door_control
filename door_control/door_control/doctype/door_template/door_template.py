# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class door_template(Document):
	def validate(self):
		if self.flags.in_insert:
			return
		frappe.msgprint("UPDATING TEMPLATE")
		tot_cnt = usr_cnt = 0
		users = frappe.get_all('door_user')
		for user_name in users:
			user = frappe.get_doc('door_user',user_name)
			if user.template != self.name: # xxx if user is not this template
				continue # to next user
			run_cnt = 0
			for ap in user.override:
				#if not overridden, change to template 
				#so find the self.access item that matches this doornum and controller combo
				if not ap.override:
					tp = [i for i in self.access if i.doornum == ap.doornum and i.controller == ap.controller]
					ap.access = tp[0].access
					tot_cnt += 1 ; run_cnt += 1

			if not run_cnt == 0:
				usr_cnt += 1
		
			user.save()
		frappe.msgprint("Total changes: " + str(tot_cnt))
		frappe.msgprint("Users changed: " + str(usr_cnt))

		frappe.msgprint("please refresh your browswer now")
			# door_user validation will take care of updating controller