# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, requests, json

def get_subbase_url():
    settings = frappe.get_doc('doorctl_settings')
    ip_addr = settings.rest_ip
    port = settings.rest_port
    base = 'http://' + ip_addr + ":" + port + "/uhppote/device"
    return base

def get_all_controllers():
	url = get_subbase_url()
	r = requests.get(url)	
	cnt_new = 0
	if r.status_code == 200:
		ctrls = r.json()['devices']
		nc_total = len(ctrls)
		existing_ctrls = frappe.get_all('controller',pluck='serial_number')
		cnt_new = get_new_ctrls(ctrls, existing_ctrls)
	return cnt_new

def get_new_ctrls(all, exist):
	new_ctrls = []
	cnt = 0
	for dev in all:
		nf = 0
		for e in exist:
			if str(dev['device-id']) == e:
				nf += 1
		if nf == 0: # none found, so must be new controller
			# another rest call to get the controller info...
			url = get_subbase_url() + "/" + str(dev['device-id'])
			r = requests.get(url)
			a = r.json()['device']
			pass  # xxx now we need to organize the info for the a.xxx stuff below
			new_ctrl = frappe.new_doc('controller')
			new_ctrl.serial_number = str(dev['device-id'])
			new_ctrl.ip_address = a['ip-address']
			new_ctrl.mac_address = a['mac-address']
			new_ctrl.version = a['version']
			new_ctrl.gateway = a['gateway-address']
			new_ctrl.subnet_mask = a['subnet-mask']
			new_ctrl.type = a['device-type']
			new_ctrl.date = a['date']

			new_ctrl.insert()
			cnt += 1
	return cnt
    
class controller(Document):

    def send_swipe(self):
        url = self.get_baseurl()
        req = {
            "door": 0,
            "card-number": 123456,
            "direction": 1,
            "PIN": 1234   
        }
        r = requests.post(url, json = req)
        return r


    @frappe.whitelist()
    def search_new_controllers(self):
        return get_all_controllers()
        
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
        
    def delete_card(self, cardnum):
        base = self.get_baseurl()
        url = base + "/card/" + str(cardnum)
        payload = {}
        headers = {'Accept': 'application/json'}
        r=requests.request("DELETE",url, headers=headers, data=payload)
        return True
    
    def get_cards(self):
        base = self.get_baseurl()
        url = base + "/cards"
        r=requests.get(url)
        cards = r.json()['cards']
        return cards
    
    def get_baseurl(self):
        base = get_subbase_url()
        base += "/" + str(self.serial_number)
        return base
    
    def get_card(self,card):
        base = self.get_baseurl()
        url = base + "/card/" + str(card)
        r=requests.get(url)
        fullcard = r.json()['card']
        if 'PIN' not in fullcard:
            fullcard['PIN'] = 0
        return fullcard
	

