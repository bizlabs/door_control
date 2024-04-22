# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests
from frappe.utils import today

class controller_card(Document):

	@frappe.whitelist()
	def add_card(self, cardnum, doors, pin):
		# add card to all controllers
		ctlrs = frappe.get_all('controller')
		for ctlr in ctlrs:
			controller = frappe.get_doc('controller',ctlr)
			user = frappe.get_doc({
				'doctype': 'door_user',
				'code':		cardnum,
				'pin':		pin,
				'start':	today(),
				'end':		"2099-12-31",
			})
			controller.add_card(user, doors)
		
	def on_trash(self):
		controller = frappe.get_doc('controller',self.controller)
		base = controller.get_baseurl()
		url = base + "/card/" + str(self.cardnum)

		payload = {}
		headers = {
		'Authorization': 'Basic <credentials>'
		}
		response = requests.request("DELETE", url, headers=headers, data=payload)
		pass

	@frappe.whitelist()
	def get_all_cards(self):
		# ip_addr = "10.44.35.38"
		# port = "8080"
		# base = 'http://' + ip_addr + ":" + port + "/uhppote/device/"
		# base = get_base()
		controllers = frappe.db.get_all('controller', pluck='name')
		cnt = 0
		for ctrl_str in controllers:
			controller = frappe.get_doc('controller', ctrl_str)
			base = controller.get_baseurl()
			# base_devurl = base + controller
			url = base + "/cards"
			r=requests.get(url)
			cards = r.json()['cards']
			db_cards = frappe.db.get_all('controller_card', fields = ['ctrl_card', 'name'])
			for cardnum in cards:
				card = self.get_card(cardnum,base)['card']
				ctrl_card = ctrl_str + " : " + str(cardnum)
				db_card = [i for i in db_cards if i['ctrl_card'] == ctrl_card ]

				if db_card == []:
					card_doc = frappe.new_doc('controller_card')
					card_doc = self.setup_card(card_doc, card, controller, ctrl_card)
					res = card_doc.insert()
					cnt += 1
				else:
					card_doc = frappe.get_doc('controller_card',db_card[0].name)
					card_doc = self.setup_card(card_doc, card, controller, ctrl_card)
					res = card_doc.save()

					# #not found so insert new card in database
					# card_doc = frappe.new_doc('controller_card')
					# card_doc = self.setup_card(card_doc, card, controller, ctrl_card)
					# res = card_doc.insert()
					# cnt += 1

		num_orphans = self.mark_orphan_cards()
		frappe.msgprint ("Added " + str(cnt) + " card(s)")
		frappe.msgprint ("found and marked " + str(num_orphans) + " orphans")
		return r
		
	def setup_card(self,card_doc,card,controller,ctrl_card):
		card_doc.controller = controller
		card_doc.cardnum = 		card['card-number']
		card_doc.start_date = 	card['start-date']
		card_doc.end_date = 	card['end-date']
		card_doc.d1 = 			card['doors']['1']
		card_doc.d2 = 			card['doors']['2']
		card_doc.d3 = 			card['doors']['3']
		card_doc.d4 = 			card['doors']['4']
		card_doc.ctrl_card =	ctrl_card

		return card_doc

		# 	'doctype':			'controller_card',
		# 	'controller':		controller,
		# 	'cardnum':			card['card-number'],
		# 	# 'pin':				card.pin,
		# 	'start_date':		card['start-date'],
		# 	'end_date':			card['end-date'],
		# 	'd1':				card['doors']['1'],
		# 	'd2':				card['doors']['2'],
		# 	'd3':				card['doors']['3'],
		# 	'd4':				card['doors']['4'],
		# 	'ctrl_card':		ctrl_card,
		# })
		# return card_doc
		
	def get_card(self, card, base):
		url = base + "/card/" + str(card)
		r = requests.get(url)
		card = r.json()
		return card

	def mark_orphan_cards(self):
		cnt = 0
		controllers = frappe.get_all('controller')
		cards = []
		for controller in controllers:
			cards.extend(self.get_cards_from_controller(controller))
		dbcards = frappe.db.get_all('controller_card',pluck='ctrl_card')
		for dbcard in dbcards:
			# if card not exist on indicated controller, mark it as orphan
			words = dbcard.split()
			ctrl = words[0]
			card = words[2]
			if (ctrl + " : " + card) in cards:
				continue
			else:
				orphans = frappe.get_all('controller_card', {'controller':ctrl, 'cardnum':card})
				dbc = frappe.get_doc('controller_card',orphans[0].name)
				dbc.orphan = True
				dbc.save()
				cnt += 1
		return cnt
		
			
	def get_cards_from_controller(self,ctrl):
		controller = frappe.get_doc('controller',ctrl)
		base = controller.get_baseurl()
		url = base + "/cards"
		payload = {}
		headers = {
		'Accept': 'application/json'
		}
		response = requests.request("GET", url, headers=headers, data=payload)
		cards = response.json()['cards']
		ctrl_cards = []
		for card in cards:
			ctrl_cards.append(controller.serial_number + " : " + str(card))

		return ctrl_cards
