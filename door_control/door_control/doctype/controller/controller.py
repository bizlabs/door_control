# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from uhppoted import uhppote

def get_uhpp():
	bind = '0.0.0.0'
	broadcast = '255.255.255.255:60000'
	listen = '0.0.0.0:60001'
	debug = False
	return uhppote.Uhppote(bind, broadcast, listen, debug)

class controller(Document):

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
		if (ctrls):
			nc_total = len(ctrls)
			existing_ctrls = frappe.get_all('controller',pluck='serial_number')
			cnt_new = self.get_new_ctrls(ctrls, existing_ctrls)

		return cnt_new