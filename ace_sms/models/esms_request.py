# -*- coding: utf-8 -*-

import requests
import json
import urllib
from werkzeug import urls
from odoo.tools.translate import quote, unquote, xml_translate, html_translate
from functools import reduce


class ESMSProvider():

    def __init__(self, base_url, api_key, secret_key):
        if not base_url:
            self.base_url = 'http://rest.esms.vn/MainService.svc/json/'
        else:
            self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key

    def _send_request(self, method, url, params, data):
        try:
            if method == 'get':
                headers = {'content-type': 'application/json'}
                resp = requests.get(url, params=params, data=json.dumps(data), headers=headers)
            else:
                headers = {'content-type': 'application/json'}
                resp = requests.post(url, params=params, data=json.dumps(data), headers=headers)
        except Exception as ex:
            return {
                'CodeResponse': '-9999',
                'Exception': ex
            }
        try:
            return json.loads(resp.text)
        except Exception as ex:
            return {
                'CodeResponse': '-9999',
                'Exception': ex
            }

    def account_info(self):
        url = "%s%s%s/%s" % (self.base_url, 'GetBalance/', self.api_key, self.secret_key)
        resp = self._send_request(method='get', url=url, params={}, data={})
        return resp

    def send_sms(self, data):
        if not data:
            data = {}
        data.update({
            'ApiKey': self.api_key,
            'SecretKey': self.secret_key,
        })
        data = urls.url_encode(data)
        url = "%sSendMultipleMessage_V4_get?%s" % (self.base_url, data)
        resp = self._send_request(method='get', url=url, params={}, data={})
        return resp

    def sms_check_status(self, sms_id):
        data = {
            'ApiKey': self.api_key,
            'SecretKey': self.secret_key,
            'RefId': sms_id
        }
        data = urls.url_encode(data)
        url = "%sGetSendStatus?%s" % (self.base_url, data)
        # url = "%s%s/%s/%s/%s" % (self.base_url, 'GetSendStatus', sms_id, self.api_key, self.secret_key)
        resp = self._send_request(method='get', url=url, params={}, data={})
        return resp