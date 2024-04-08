# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from uhppoted import uhppote
import datetime, json, requests

def get_uhpp():
	bind = '0.0.0.0'
	broadcast = '255.255.255.255:60000'
	listen = '0.0.0.0:60001'
	debug = False
	return uhppote.Uhppote(bind, broadcast, listen, debug)


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
		
		# self.delete()

			# base = controller.get_baseurl()
			# url = base + "/card/" + str(self.code)
			# payload = {}
			# headers = {
			# 'Authorization': 'Basic <credentials>'
			# }
			# response = requests.request("DELETE", url, headers=headers, data=payload)
			# pass

	@frappe.whitelist()
	def import_cards(self):
		controllers = frappe.db.get_all('controller', pluck='name')
		for ctrl_str in controllers:
			controller = frappe.get_doc('controller', ctrl_str)

			# base = controller.get_baseurl()
			# url = base + "/cards"
			# r=requests.get(url)
			# cards = r.json()['cards']

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
						'pin': fullcard['pin'],
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

	def validate(self):
		u = get_uhpp()
		# x = datetime.datetime(2020, 5, 17)

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
		# xxx document what this does
		u = get_uhpp()
		s = set()
		cardset = []
		for a in self.override:
			if a.controller not in s:
				s.add(a.controller)
				ctrl = int(a.controller)
				card = int(self.code)
				card_obj =u.get_card(ctrl,card)
				card_dict = card_obj.__dict__
				# card_str = json.dumps(card_dict)
				card_str = json.dumps(card_dict, indent=4, sort_keys=True, default=str)
				cardset.append(card_str)
		return cardset


	@frappe.whitelist()
	def get_cards(self):
		u = get_uhpp()
		s = set()
		cardset = []
		for a in self.override:
			if a.controller not in s:
				s.add(a.controller)
				ctrl = int(a.controller)
				allcards_obj =u.get_cards(ctrl)
				allcards_dict = allcards_obj.__dict__
				# card_str = json.dumps(card_dict)
				allcards_str = json.dumps(allcards_obj, indent=4, sort_keys=True, default=str)
				cardset.append(allcards_str)
		return cardset