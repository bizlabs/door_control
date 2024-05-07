# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, json, requests


class door_user(Document):

	@frappe.whitelist()
	def get_access_by_template(self):
		if self.template == None:
			accs = None
		else:
			accs = frappe.get_all('access', 
				filters = {'parent': self.template,},
				fields = ['name', 'access','controller','doornum'],
				# fields: ['name', 'access','name','name','name','controller','name','doornum'],
			)
		return accs
	
	
	def on_trash(self): 
		if self.db_delete_only:
			return
		controllers = frappe.db.get_all('controller', pluck='name')
		for ctrl_str in controllers:
			if any(x for x in self.override if x.controller == ctrl_str):
				controller = frappe.get_doc('controller', ctrl_str)
				controller.delete_card(self.code)
		self.delete_vera()

	@frappe.whitelist()
	def import_cards(self):
		controllers = frappe.db.get_all('controller', pluck='name')
		for ctrl_str in controllers:
			controller = frappe.get_doc('controller', ctrl_str)

			cards = controller.get_cards()
			db_cards = frappe.get_all('door_user', fields=['name','code'])
			for card in cards:
				found = False
				fullcard = controller.get_card(card)
				for db_card in db_cards:
					if card == int(db_card.code):
						found = True
						# check for controller and add a child record if needed
						user = frappe.get_doc('door_user', db_card.name)
						if not user.has_controller(controller):	
							#didn't find this controller so we'll add it 
							user.add_controller(fullcard, controller)
							user.db_save_only = True
							user.save()
						break # out of db_card and go to next card
				if not found:
					# fullcard = controller.get_card(card) # deleteme?
					new_user = frappe.get_doc({
						'doctype': 'door_user',
						'code': card,
						'pin': fullcard['PIN'],
						'foreign': True,
					})
					new_user.db_save_only = True
					# new_user.insert()
					#set child element
					new_user.add_controller(fullcard, controller)
					new_user.insert()
		frappe.msgprint("done importing")
   
	def has_controller(self,controller):
		for access in self.override:
			if access.controller == controller.serial_number:
				return True
		return False

	def add_controller(self, fullcard, controller):
		fd = fullcard['doors']
		doors = [fd['1'],fd['2'],fd['3'],fd['4'] ]
		for d in [1,2,3,4]:
			access = {
				'controller':	controller.name,
				'doornum': 		d,
				'access':		doors[d-1],
				}
			self.append('override', access)

	def before_save(self):
		'''don't allow changing users code'''
		db_code = frappe.db.get_value('door_user',self.name,'code')
		if db_code == None:
			return # this is a new user so don't check if code is changed
		if db_code != str(self.code):
			frappe.throw("You cannot change the code.  Create a new user instead")
	
	def before_validate(self):
		if self.override == []: # can happen if user is created in code (eg from ST guest module)
			self.copy_template()
	
		if self.active:
			# temp = self.copy_doc()
			# temp.save_card_on_controller()
			self.save_card_on_controller()
			self.save_vera()
		else:
			temp = self.copy_doc()
			for access in temp.override:
				access.access = False
			temp.save_card_on_controller()
			self.deactivate_vera()
		# continue with other validations
		return

	def save_card_on_controller(self):
		if self.db_save_only:
			self.db_save_only = False
			return
		if self.full_name == None:
			#ignore imports until name entered
			return
		start = datetime.datetime(1970, 1, 1)
		end = datetime.datetime(2099, 12, 31)
		s = set()
		access = {}
		for a in self.override:
			if a.controller not in s:
				s.add(a.controller)
				access[a.controller] = {'sn':a.controller, 'd1':99, 'd2':99, 'd3':99, 'd4':99}
				# access = {a.controller: {'name':a.controller, 'd1':99, 'd2':99, 'd3':99, 'd4':99} }

		for a in self.override:
			access[a.controller]['d'+str(a.doornum)] = a.access


		for ctrl, doors in access.items():
			d1 = doors['d1']
			d2 = doors['d2']
			d3 = doors['d3']
			d4 = doors['d4']
			doorset = [d1,d2,d3,d4]
			controller = frappe.get_doc('controller',ctrl)
			controller.add_card(self, doorset)
			# controller.add_card(self.code, doorset, self.pin)


	@frappe.whitelist()
	def get_card(self):
		s = set()
		cardset = []
		cardstr = ""
		for a in self.override:
			if a.controller not in s:
				s.add(a.controller)
				ctrl = frappe.get_doc('controller',a.controller)
				card = ctrl.get_card(self.code)

				cardset.append(card)
				cardstr += str(ctrl.serial_number) + ": " + str(card) + '\n'
		return cardstr


	@frappe.whitelist()
	def get_cards(self):
		s = set()
		cardset = []
		cardstr = ""
		for a in self.override:
			if a.controller not in s:
				s.add(a.controller)
				ctrl = frappe.get_doc('controller',a.controller)
				allcards_obj = ctrl.get_cards()
				allcards_str = json.dumps(allcards_obj, indent=4, sort_keys=True, default=str)
				cardset.append(allcards_str)
				cardstr += "ctrl: " + ctrl.serial_number + '\n' + allcards_str + '\n'
		return cardstr
	
	def copy_doc(self):
		new_user = frappe.get_doc({
			'doctype':		'door_user',
			'start':		self.start,
			'end':			self.end,
			'code':			self.code,
			'pin':			'0',
		})
		for oride in self.override:
			item = frappe.get_doc({
				'doctype':		'user_access',
				'override':		oride.override,
				'access':		oride.access,
				'doornum':		oride.doornum,
				'controller':	oride.controller,
				})
			new_user.append('override', item)
		for vacc in self.vera_access:
			item = frappe.get_doc({
				'doctype': 	'vera_access',
				'room': 	vacc.room,
				'devnum': 	vacc.devnum,
			})
			new_user.append('vera_access', item)
		return new_user
	
	def copy_template(self):
		template = frappe.get_doc('door_template',self.template)
		for acc in template.access:
			ov = frappe.get_doc({
				'doctype':		'user_access',
				'access':		acc.access,
				'doornum':		acc.doornum,
				'controller':	acc.controller,
			})
			self.append('override', ov)
		return

	def save_vera(self):
		'''read the old user, comparing self with it, add and delete vaccs appropriately'''
		if not self.flags.in_insert:
			old_user = frappe.get_doc('door_user',self.name)
			for vacc in old_user.vera_access:
				#if vacc is not in self.ver_access, delete it from vera hub
				if not any(getattr(obj, 'name', None) == vacc.name for obj in self.vera_access):
					vacc.delete_user()

		for vacc in self.vera_access:
			if not vacc.slot:
				vacc.add_user()
		return
	
	def delete_vera(self): 
		for vacc in self.vera_access:
			if self.active:
				vacc.delete_user()
			self.remove(vacc)
		return
	
	def deactivate_vera(self):
		'''remove from vera hub and remove slot number for vacc but don't remove
		the child table so that it can be re-added when/if re-activated'''
		for vacc in self.vera_access:
			vacc.delete_user()
			vacc.slot = None
		return