# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from uhppoted import uhppote
import datetime, json

def get_uhpp():
	bind = '0.0.0.0'
	broadcast = '255.255.255.255:60000'
	listen = '0.0.0.0:60001'
	debug = False
	return uhppote.Uhppote(bind, broadcast, listen, debug)


class door_user(Document):
	
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
# xxx set pin to 0 if empty
			res = u.put_card(int(ctrl), int(self.code), start, end, d1, d2, d3, d4, int(self.pin) )

	@frappe.whitelist()
	def get_card(self):
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