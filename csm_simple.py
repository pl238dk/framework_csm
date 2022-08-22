import requests
import getpass
import xml.etree.ElementTree as ET
import urllib3
urllib3.disable_warnings()

class csm(object):
	def __init__(self):
		return
	
	def login(self, host):
		self.session = requests.Session()
		self.host = host
		url = f'https://' + f'{host}/nbi/login'
		username = ''
		password = getpass.getpass(f'{host} PASSCODE: ')
		data = (
			f'<?xml version="1.0" encoding="UTF-8"?>'
			f'<ns1:loginRequest xmlns:ns1="csm">'
				f'<protVersion>1.0</protVersion>'
				f'<reqId>123</reqId>'
				f'<username>{username}</username>'
				f'<password>{password}</password>'
			f'</ns1:loginRequest>'
		)
		response = self.session.post(
			url,
			data=data,
			verify=False,
		)
		return response
	
	def logout(self, host):
		if not hasattr(self, 'session'): return
		url = f'https://' + f'{self.host}/nbi/logout'
		data = (
			f'<?xml version="1.0" encoding="UTF-8"?>'
			f'<ns1:logoutRequest xmlns:ns1="csm">'
				f'<protVersion>1.0</protVersion>'
				f'<reqId>123</reqId>'
			f'</ns1:logoutRequest>'
		)
		response = self.session.post(
			url,
			data=data,
			verify=False,
		)
		return response
	
	def approve_activity(self, activity_name):
		if not hasattr(self, 'session'): return
		url = f'https://' + f'{self.host}/nbi/configservice/approveCSMSession'
		data = (
			f'<ns1:csmApproveOperationRequest xmlns:ns1="csm">'
				f'<csmSessionName>{activity_name}</csmSessionName>'
				f'<approvalStatus>true</approvalStatus>'
			f'</ns1:csmApproveOperationRequest>'
		)
		response = self.session.post(
			url,
			data=data,
			verify=False,
		)
		return response
	
	def get_device_list_by_type(self, device_type):
		if not hasattr(self, 'session'): return
		url = f'https://' + f'{self.host}/nbi/configservice/getDeviceListByType'
		data = (
			f'<?xml version="1.0" encoding="UTF-8"?>'
			f'<ns1:deviceListByCapabilityRequest xmlns:ns1="csm">'
				f'<protVersion>1.0</protVersion>'
				f'<reqId>123</reqId>'
				f'<deviceCapability>{device_type}</deviceCapability>'
			f'</ns1:deviceListByCapabilityRequest>'
		)
		response = self.session.post(
			url,
			data=data,
			verify=False,
		)
		return response
	
	def get_config_by_name(self, device_name):
		url = f'https://' + f'{self.host}/nbi/configservice/getDeviceConfigByName'
		data = (
			f'<ns1:deviceConfigByNameRequest xmlns:ns1="csm">'
				f'<protVersion>1.0</protVersion>'
				f'<reqId>123</reqId>'
				f'<name>{device_name}</name>'
			f'</ns1:deviceConfigByNameRequest>'
		)
		response = self.session.post(
			url,
			data=data,
			verify=False,
		)
		return response
	
	def get_firewall_list(self):
		list_response = c.get_device_list_by_type('*')
		list_parsed = self.parse_xml(
			list_response.text,
			'deviceId',
		)
		output = [list_entry['deviceName'] for list_entry in list_parsed]
		return output
	
	def get_running_config(self, device_name):
		config_response = self.get_config_by_name(device_name)
		config_parsed = self.parse_xml(
			config_response.text,
			'device',
		)
		config_raw = config_parsed[0]['fullConfig']
		return config_raw
	
	def parse_xml(self, xml_raw, element_name):
		output = []
		et_raw = ET.fromstring(xml_raw)
		devices = et_raw.findall(element_name)
		for device in list(devices):
			device_info = {}
			for attribute in list(device):
				device_info[attribute.tag] = attribute.text
			output.append(device_info)
		return output

if __name__ == '__main__':
	c = csm('csm1')
	