# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class v_cards(Document):
	
	def db_insert(self, *args, **kwargs):
		frappe.msgprint("insert not implemented")

	def delete(self):
		frappe.msgprint("delete not implemented")
		

	def load_from_db(self):
		parsed = self.name.split(':')
		ID = parsed[0]; name = parsed[1]
		ctrl = frappe.get_doc('controller',ID)
		card = ctrl.get_card(name)
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
		pass

	def db_update(self):
		frappe.msgprint("save not implemented")

	@staticmethod
	def get_list(args):
		s = set()
		cardset = []
		ctrls = frappe.get_all('controller')
		for ID in ctrls:
			ctrl = frappe.get_doc('controller',ID.name)
			cards = ctrl.get_cards()
			for card in cards:
				cardset.append({
					'name': str(ctrl.serial_number) + ":" + str(card), 
					'controller':	ctrl.serial_number, 
					'code':			card,
					# 'start_date':	'xxx',
					# 'end_date':		'xxx',
					# 'doors':		'xxx',
					})
		return cardset
			

		# for a in self.override:
		# 	if a.controller not in s:
		# 		s.add(a.controller)
		# 		ctrl = frappe.get_doc('controller',a.controller)
		# 		allcards_obj = ctrl.get_cards()
		# 		allcards_str = json.dumps(allcards_obj, indent=4, sort_keys=True, default=str)
		# 		cardset.append(allcards_str)
		# x = [frappe._dict(doc) for controller, code in cardset.items()]
		# return x
		pass

	@staticmethod
	def get_count(args):
		pass

	@staticmethod
	def get_stats(args):
		pass

