import requests
import json

headers = {'content-type': 'application/json'}
# url = 'http://rest.esms.vn/MainService.svc/json/GetBalance/9366C8747DFC3CA54DF320BA8D49AE/FC9DFF94837B54C9764838242D3CC4'
# url = 'http://rest.esms.vn/MainService.svc/json/SendMultipleMessage_V4_get?Content=Dear+Chi+Cuong%2C%0A%C4%82n+c%C6%A1m+tr%C6%B0a+th%C3%B4i+ch%E1%BB%8B+C%C6%B0%E1%BB%9Dng+%C6%A1i%0AThank+you&Phone=0906094896&Sandbox=0&ApiKey=9366C8747DFC3CA54DF320BA8D49AE&IsUnicode=0&SecretKey=FC9DFF94837B54C9764838242D3CC4&SmsType=4'
url = 'http://rest.esms.vn/MainService.svc/json/GetSendStatus?RefId=e1ffc6f4-cfd5-45c2-b1dc-1ed5275c554894&ApiKey=9366C8747DFC3CA54DF320BA8D49AE&SecretKey=FC9DFF94837B54C9764838242D3CC4'

data = {}
params = {}

res = requests.get(url, params=params, data=json.dumps(data), headers=headers)
print '====================res:', res.text