# Copyright (c) 2024, bizlabs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import requests


class controller_card(Document):

	@frappe.whitelist()
	def add_card(self, cardnum, doors, pin):
		# add card to all controllers
		ctlrs = frappe.get_all('controller')
		for ctlr in ctlrs:
			controller = frappe.get_doc('controller',ctlr)
			controller.add_card(cardnum, doors, pin)
		pass


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
			db_cards = frappe.db.get_all('controller_card', pluck='ctrl_card')
			for cardnum in cards:
				ctrl_card = ctrl_str + " : " + str(cardnum)
				if ctrl_card in db_cards:
					continue
				card = self.get_card(cardnum,base)['card']
				card_doc = frappe.get_doc({
					'doctype':			'controller_card',
					'controller':		controller,
					'cardnum':			card['card-number'],
					# 'pin':				card.pin,
					'start_date':		card['start-date'],
					'end_date':			card['end-date'],
					'd1':				card['doors']['1'],
					'd2':				card['doors']['2'],
					'd3':				card['doors']['3'],
					'd4':				card['doors']['4'],
					'ctrl_card':		ctrl_card,
				})
				res = card_doc.insert()
				cnt += 1
		num_orphans = self.mark_orphan_cards()
		frappe.msgprint ("Added " + str(cnt) + " card(s)")
		frappe.msgprint ("found and marked " + str(num_orphans) + " orphans")
		return r
	
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
