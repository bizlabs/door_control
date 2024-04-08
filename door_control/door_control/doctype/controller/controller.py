# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from uhppoted import uhppote
import datetime, requests, json

def get_uhpp():
	bind = '0.0.0.0'
	broadcast = '255.255.255.255:60000'
	listen = '0.0.0.0:60001'
	debug = False
	return uhppote.Uhppote(bind, broadcast, listen, debug)

class controller(Document):

	@frappe.whitelist()
	def add_card(self, cardnum, doors, pin):
		base = self.get_baseurl()
		url = base + "/card/" + str(cardnum)
		start = "1970-01-01"
		end = "2099-12-31"
		payload = json.dumps({
		"start-date": start,
		"end-date": end,
		"doors": {'1':int(doors[0]),'2':int(doors[1]),'3':int(doors[2]),'4':int(doors[3])},
		"PIN": int(pin)
		})
		headers = {
		'Content-Type': 'application/json',
		'Authorization': 'Basic <credentials>'
		}

		response = requests.request("PUT", url, headers=headers, data=payload)

	@frappe.whitelist()
	def add_card_py(self,cardnum,doors,pin):
		start = datetime.datetime(1970, 1, 1)
		end = datetime.datetime(2099, 12, 31)
		u=get_uhpp()
		ID = int(self.serial_number); cd = int(cardnum)
		d1 = int(doors[0]); d2 = int(doors[1]); d3 = int(doors[2]); d4 = int(doors[3])
		u.put_card(ID, cd, start, end, d1, d2, d3, d4, int(pin))
		status = True
		return status
	
	def delete_card(self, cardnum):
		base = self.get_baseurl()
		url = base + "/card/" + str(cardnum)
		payload = {}
		headers = {'Accept': 'application/json'}
			# prolly should see if exists first.  return false if not deleted
		r=requests.request("DELETE",url, headers=headers, data=payload)
		return True

	def delete_card_py(self, cardnum):
		u = get_uhpp()
		try:
			res = u.delete_card(int(self.serial_number), int(cardnum) )
		except:
			pass
		status = True
		return status

	def get_baseurl(self):
		# ip_addr = "10.44.35.38"
		ip_addr = self.ip_address
		port = "8080"
		base = 'http://' + ip_addr + ":" + port + "/uhppote/device/"
		base += self.serial_number
		return base

	def get_new_ctrls(self,all, exist):
		new_ctrls = []
		cnt = 0
		for a in all:
			nf = 0
			for e in exist:
				if a.controller == e:
					nf += 1
			if nf == 0: # none found, so must be new controller
				new_ctrl = frappe.new_doc('controller')
				new_ctrl.serial_number = str(a.controller)
				new_ctrl.ip_address = a.ip_address.compressed
				new_ctrl.mac_address = a.mac_address
				new_ctrl.version = a.version
				new_ctrl.gateway = a.gateway.compressed
				new_ctrl.subnet_mask = a.subnet_mask.compressed

				new_ctrl.insert()
				cnt += 1
		return cnt

	@frappe.whitelist()
	def get_all_controllers(self):
		u = get_uhpp()
		ctrls = u.get_all_controllers()
		cnt_new = 0
		if (ctrls):
			nc_total = len(ctrls)
			existing_ctrls = frappe.get_all('controller',pluck='serial_number')
			cnt_new = self.get_new_ctrls(ctrls, existing_ctrls)

		return cnt_new
	
	def get_card(self,card):
		base = self.get_baseurl()
		url = base + "/card/" + str(card)
		r=requests.get(url)
		fullcard = r.json()['card']
		if 'pin' not in fullcard:
			fullcard['pin'] = 0
		return fullcard
	
	def get_cards(self):
		base = self.get_baseurl()
		url = base + "/cards"
		r=requests.get(url)
		cards = r.json()['cards']
		return cards