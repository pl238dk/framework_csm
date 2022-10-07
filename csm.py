#
# Framework for interacting with Cisco CSM
#
#

import requests
requests.packages.urllib3.disable_warnings()
import json
import os
import xml.etree.ElementTree as xml

'''
{
	'success': False,
	'result': '',
	'response_object':response,
}
'''

class CSM(object):
	def __init__(self, config=None):
		if config is None:
			print('[E] No configuration filename not provided')
		else:
			self.config = config
		return
	
	def load_configuration(self, config):
		config_file = 'configuration.json'
		path = os.path.abspath(__file__)
		dir_path = os.path.dirname(path)
		with open(f'{dir_path}/{config_file}','r') as f:
			raw_file = f.read()
		config_raw = json.loads(raw_file)
		if config not in config_raw['servers']:
			print('[E] Configuration not found in configuration.json')
		else:
			connection_info = config_raw['servers'][config]
			return connection_info
			#self.collector = connection_info['host']
			#self.authenticate(connection_info)
		return
	
	def login(self):
		self.session = requests.Session()
		self.session.trust_env = False
		proxies = {
			'http':''
		}
		self.session.proxies = proxies
		
		connection_info = self.load_configuration(self.config)
		self.collector = connection_info['host']
		
		authentication_params = {
			'username':	connection_info['username'],
			'password':	connection_info['password'],
		}
		payload = self.get_payload('loginRequest', authentication_params)
		
		auth_url = f'https://{self.collector}/nbi/login'
		response = self.post_request(auth_url, payload)
		return response
	
	def post_request(self, url, data):
		response_raw = self.session.post(url, data=data, verify=False)
		if response_raw.status_code == 200:
			return {
				'success':	True,
				'result':	response_raw.text,
				'response_object':	response_raw,
			}
		else:
			return {
				'success':	False,
				'result':	'',
				'response_object':	response_raw,
			}
		return
	
	def get_payload(self, function_name, parameters):
		'''
		args:
			function_name:	<type 'str'>
			parameters:	<type 'dict'>
		returns:
			XML payload in <type 'str'> format
		raises:
			n/a
		'''
		internal_payload_list = [
			f'<{key}>{parameters[key]}</{key}>'
			if
			key
			else
			''
			for key in parameters
		]
		internal_payload = ''.join(internal_payload_list)
		data = (
			f'<?xml version="1.0" encoding="UTF-8"?>'
			f'<ns1:{function_name} xmlns:ns1="csm">'
				f'<protVersion>1.0</protVersion>'
				f'<reqId>123</reqId>'
				f'{internal_payload}'
			f'</ns1:{function_name}>'
		)
		return data
	
	def logout(self):
		params = {}
		payload = self.get_payload('logoutRequest', params)
		logout_url = f'https://{self.collector}/nbi/logout'
		response = self.post_request(logout_url, payload)
		return response
	
	def get_device_list_by_type(self, device_type):
		url = f'https://{self.collector}/nbi/configservice/getDeviceListByType'
		params = {
			'deviceCapability':	device_type,
		}
		payload = self.get_payload('deviceListByCapabilityRequest', params)
		response = self.post_request(url, payload)
		return response
	
	def get_config_by_name(self, device_name):
		url = f'https://{self.collector}/nbi/configservice/getDeviceConfigByName'
		params = {
			'name':	device_name,
		}
		payload = self.get_payload('deviceConfigByNameRequest', params)
		response = self.post_request(url, payload)
		return response
	
	def parse_xml(self, xml_raw):
		output = []
		xml_element = xml.fromstring(xml_raw)
		entries_full = list(xml_element)
		if not entries_full:
			print('[E] nothing to parse')
			return
		# exclude defaults
		entries = [entry for entry in entries_full if entry.tag not in ['protVersion','reqId']]
		for entry in entries:
			#if entry.tag in ['protVersion', 'reqIq']: continue
			info = {
				'collector_source':	self.collector,
			}
			for attribute in list(entry):
				if len(list(attribute)) > 0:
					for attribute_child in list(attribute):
						info[attribute_child.tag] = attribute_child.text
				else:
					info[attribute.tag] = attribute.text
			output.append(info)
		return output

if __name__ == '__main__':
	c = CSM(config='')
	li_response = c.login()
	dlist = c.get_device_list_by_type('*')
	devices = c.parse_xml(dlist['result'])
	#
	names = [entry['deviceName'] for entry in devices]
	test_device = names[7]
	clist = c.get_config_by_name(test_device)
	config_raw = c.parse_xml(clist['result'])
	config = config_raw[0]['fullConfig']
	#
	lo_response = c.logout()
	print('[I] End')
