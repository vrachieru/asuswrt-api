import json
import requests

from base64 import b64encode
from datetime import datetime

from .model import Client


class AsusWRT:

    _USER_AGENT = 'asusrouter-Android-DUTUtil-1.0.0.3.58-163'
    
    _CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def __init__(self, url, username, password):
        self._url = url
        self._username = username
        self._password = password
        self._session = requests.Session()

        self.refresh_asus_token()

    def is_asus_token_set(self):
        '''
        Check if authentication token is present
        '''
        return 'asus_token' in self._session.cookies.keys()

    def is_asus_token_valid(self):
        '''
        Check that the asus token is not older than 60 minutes
        '''
        try:
            return (datetime.now() - self._asus_token_timestamp).seconds < 60 * 60
        except:
            return False

    def refresh_asus_token(self):
        '''
        Refresh authentication token
        '''
        response = self.request(
            'POST', 
            '/login.cgi',
            {
                'login_authorization': b64encode(('%s:%s' % (self._username, self._password)).encode('utf-8')).decode('utf-8')
            }
        )

        self._asus_token_timestamp = datetime.now()

    def logout(self):
        '''
        Logout
        '''
        response = self.request(
            'GET',
            '/Logout.asp'
        )

        self._session = requests.Session()

    def get_sys_info(self):
        '''
        Get system information
        '''
        response = self.get('nvram_get(productid);nvram_get(firmver);nvram_get(buildno);nvram_get(extendno)')

        return {
            'model': response.get('productid'),
            'firmware': '%s_%s_%s' % (response.get('firmver'), response.get('buildno'), response.get('extendno'))
        }

    def get_cpu_mem_info(self):
        '''
        Get CPU and memory usage
        '''
        response = self.get('cpu_usage(appobj);memory_usage(appobj);')

        return {
            'cpu': response['cpu_usage'],
            'memory': {
                'total': response['memory_usage']['mem_total'],
                'used': response['memory_usage']['mem_used'],
                'free': response['memory_usage']['mem_free']
            }
        }

    def get_wan_state(self):
        ''''
        Get WAN state
        '''
        return self.get('wanlink_state(appobj)')

    def get_online_clients(self):
        '''
        Get online clients.

        :return: list of Client
        '''
        def get_client(mac):
            return next((client for client in clients if client.mac == mac), None)

        def update_interface(interface, interface_name):
            interface_clients = response.get('wl_sta_list_%s' % interface, {})
            for key, val in interface_clients.items():
                client = get_client(key)
                if client:
                    client.interface = interface_name
                    client.rssi = val.get('rssi')

        def update_custom():
            custom_clients = self.parse_custom_clientlist(response.get('custom_clientlist', ''))
            for key, val in custom_clients.items():
                client = get_client(key)
                if client:
                    client.alias = val.get('alias')

        response = self.get('get_clientlist(appobj);wl_sta_list_2g(appobj);wl_sta_list_5g(appobj);wl_sta_list_5g_2(appobj);nvram_get(custom_clientlist)')

        clients = response.get('get_clientlist', {})
        clients.pop('maclist', None)
        clients = list(map(Client, list(clients.values())))

        update_interface('2g', '2GHz')
        update_interface('5g', '5GHz')
        update_interface('5g_2', '5GHz-2')
        update_custom()

        return clients

    def parse_custom_clientlist(self, clientlist):
        '''
        Parse user set metadata for clients
        '''
        clientlist = clientlist.replace('&#62', '>').replace('&#60', '<').split('<')
        clientlist = [client.split('>') for client in clientlist]
        clientlist = {client[1]:{'alias': client[0], 'group': client[2], 'type': client[3], 'callback': client[4]} for client in clientlist if len(client) == 6}
        
        return clientlist

    def restart_service(self, service):
        '''
        Restart service
        '''
        return self.apply({'action_mode': 'apply', 'rc_service': service })

    def get(self, payload):
        '''
        Get
        '''
        response = self.request('POST', '/appGet.cgi', {'hook': payload})
        return response.json()

    def apply(self, payload):
        '''
        Apply
        '''
        return self.request('POST', '/applyapp.cgi', json.dumps(payload)).json()

    def request(self, method, path, payload=None):
        '''
        Make REST API call

        :param str method: http verb
        :param str path: api path
        :param dict payload: request payload
        :return: the REST response
        '''
        # if not self.is_asus_token_set() or (self.is_asus_token_set() and not self.is_asus_token_valid()):
        #     self.refresh_asus_token()

        return self._session.request(
            method = method.upper(),
            url = self._url + path,
            headers = {
                'User-Agent': self._USER_AGENT,
                'Content-Type': self._CONTENT_TYPE
            },
            data = payload,
            verify=False
        )
