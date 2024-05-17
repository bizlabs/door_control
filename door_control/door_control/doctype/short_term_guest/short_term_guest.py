# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class short_term_guest(Document):

	def after_delete(self):
		'''delete door_user also. Allow door_user to handle deleting from controller or canceling on error'''
		user = frappe.get_doc('door_user',self.door_user)
		user.delete()
		return
		# frappe.msgprint("whoa!  need to uncomment code to delete associated user")
	
	def before_validate(self):
		user = self.get_user()
		if self.flags.in_insert:
			if user:
				group = frappe.get_doc('group',user.group).groupname if user.group else "no-group"
				frappe.throw("user already exists: " + user.full_name + " in group " + group)
			else:
				# settings = frappe.get_doc('doorctl_settings')
				new_user = frappe.new_doc('door_user')
				new_user = self.set_user(new_user)
				guests = frappe.get_all('short_term_guest',filters={'active':'1', 'room': self.room})
				for guest_name in guests:
					guest = frappe.get_doc('short_term_guest', guest_name)
					guest.check_overlapping_guests(self)
				new_user.append('vera_access',{'room':self.room})
				
				new_user.insert()
				self.door_user = new_user.name
			return

		else: # update, not insert
			user = frappe.get_doc('door_user',self.door_user)
			user = self.set_user(user)
			user.active = self.active
			user.save()
				# possible future feature to allow changing code which require del/add on vera and uhppote controllers

	def set_user(self,user):  
		settings = frappe.get_doc('doorctl_settings')
		user.full_name = 	self.guest_name
		user.group = 		settings.guest_group
		user.code = 		self.code
		user.pin =			'0'
		user.template = 	settings.guest_template
		return user

	def check_overlapping_guests(self,new_guest):
		'''if existing guest overlaps dates with new guest, do something about it
		perhaps ask user if they would like to deactivate or delete the old guest?
		however prompting from server requires realtime socketio which is not working rn'''
		overlap = True
		if overlap:
			frappe.throw("You must deactivate or delete existing guest first")

	def get_user(self):
		users = frappe.get_all('door_user', filters = {'code':self.code}, fields=['full_name','group'])
		if not users:
			return False
		else:
			return users[0]
	