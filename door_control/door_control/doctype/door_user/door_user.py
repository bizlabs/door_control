# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, json, requests


class door_user(Document):

	@frappe.whitelist()
	def get_access_by_template(self):
		accs = frappe.get_all('access', 
			filters = {'parent': self.template,},
			fields = ['name', 'access','controller','doornum'],
			# fields: ['name', 'access','name','name','name','controller','name','doornum'],
		)
		return accs
	
	
	def on_trash(self):
		controllers = frappe.db.get_all('controller', pluck='name')
		for ctrl_str in controllers:
			controller = frappe.get_doc('controller', ctrl_str)
			controller.delete_card(self.code)

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
						for access in user.override:
							if access.controller == controller.serial_number:
								break # out of access loop and go to next db_card (which immediately breaks below to next card)
						#didn't find this controller so we'll add it 
						user.add_controller(fullcard, controller)
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
					new_user.insert()
					#set child element
					new_user.add_controller(fullcard, controller)


				# xxx delete below after confirming move to function works
					# doors = [fullcard.door_1,fullcard.door_2,fullcard.door_3,fullcard.door_4]
					# for d in [1,2,3,4]:
					# 	access = {
					# 		'controller':	controller.name,
					# 		'doornum': 		d,
					# 		'access':		doors[d-1],
					# 		}
					# 	new_user.append('override', access)
					new_user.save()
		frappe.msgprint("done importing")
					
					
			#xxx now look for matching card/controller set in db
			# and create a new one with foreign = true if not found
	
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
		pass
		db_code = frappe.db.get_value('door_user',self.name,'code')
		if db_code == None:
			return # this is a new user so don't check if code is changed
		if db_code != str(self.code):
			frappe.throw("You cannot change the code.  Create a new user instead")

	def validate(self):
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
			controller.add_card(self.code, doorset, self.pin)
			# res = u.put_card(int(ctrl), int(self.code), start, end, d1, d2, d3, d4, int(self.pin) )


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