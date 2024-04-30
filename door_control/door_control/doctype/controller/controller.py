# Copyright (c) 2024, Doug Mattingly and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime, requests, json, time
from frappe.utils import today

def get_subbase_url():
    settings = frappe.get_doc('doorctl_settings')
    ip_addr = settings.rest_ip
    port = settings.rest_port
    base = 'http://' + ip_addr + ":" + port + "/uhppote/device"
    return base

def get_all_controllers():
	url = get_subbase_url()
	r = rentget(url)	
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
			r = rentget(url)
			a = r.json()['device']
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
     
    @property
    def v_sn(self):
       return self.serial_number

    def get_events(self):
        url = self.get_baseurl()
        url += "/events"
        r=rentget(url)
        tries = 0
        while tries < 5:
            try:
                return r.json()['events']
            except:
                time.sleep(1)
                tries += 1
        # frappe.throw(r.json()['tag'] + "\n" + r.json()['message'] )
    
    def get_event(self,ndx):
        url = self.get_baseurl()
        url += "/event/" + str(ndx)
        r = rentget(url)
        tries = 0
        while tries < 5:
            try:
                return r.json()['event']
            except:
                time.sleep(1)
                tries += 1 
        # frappe.throw(r.json()['tag'] + "-" + r.json()['message'] )
            

    @frappe.whitelist()
    def send_swipe(self):
        devid = str(self.serial_number)
        url = "http://10.60.104.132:8000/uhppote/simulator/" + devid + "/swipe"
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
    def add_card_for_testing(self,cardnum, dstr, pin):
        user = frappe.get_doc({
            'doctype': 'door_user',
            'code':		cardnum,
            'pin':		pin,
            'start':	today(),
            'end':		"2099-12-31",
        })
        doors = [dstr[0],dstr[1],dstr[2],dstr[3]]
        self.add_card(user, doors)

    # @frappe.whitelist()
    def add_card(self, user, doors):
        base = self.get_baseurl()
        url = base + "/card/" + str(user.code)
        payload = json.dumps({
		"start-date": str(user.start),
		"end-date": str(user.end),
		"doors": {'1':int(doors[0]),'2':int(doors[1]),'3':int(doors[2]),'4':int(doors[3])},
		"PIN": int(user.pin)
		})
        # headers = {
		# 'Content-Type': 'application/json',
		# 'Authorization': 'Basic <credentials>'
		# }
        r = rentreq("PUT", url, data=payload)
        if r.status_code != 200:
            frappe.throw(str(r.status_code) + "PutCommErr: url: " + url)
        return True
        
                
    def delete_card(self, cardnum):
        base = self.get_baseurl()
        url = base + "/card/" + str(cardnum)
        r=rentdel(url)
        if r.status_code != 200:
            frappe.throw(str(r.status_code) + "DelCommErr: url: " + url)
        return True
    
    def get_cards(self):
        base = self.get_baseurl()
        url = base + "/cards"
        r=rentget(url)
        cards = r.json()['cards']
        return cards
    
    def get_baseurl(self):
        base = get_subbase_url()
        base += "/" + str(self.serial_number)
        return base
    
    def get_card(self,card):
        base = self.get_baseurl()
        url = base + "/card/" + str(card)
        r=rentget(url)
        fullcard = r.json()['card']
        if 'PIN' not in fullcard:
            fullcard['PIN'] = 0
        return fullcard
    
# non-class functions relentless requests

def rentget(url):
    '''relentless GET'''
    r = rentreq('GET', url, "")
    return r

def rentdel(url):
    r = rentreq('DELETE', url, "")
    return r

def rentreq(type, url, data):
    '''relentless requests - tries several times with pause between'''
    num_tries = 7
    pause = 1
    for i in range(1,num_tries+1):
        if type == 'GET':
            r = requests.get(url)
        elif type == 'PUT':
            r = requests.put(url, data)
        elif type == 'DELETE':
            r = requests.delete(url)
        if r.status_code == 200:
            return r
        time.sleep(pause)
    return r

            
            
