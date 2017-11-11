import requests
import json
import urllib2

def call(url, *params):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6Im9hdXRoY2xpZW50XzAwMDA5NFB2SU5ER3pUM2s2dHo4anAiLCJleHAiOjE1MTA0Mjc1MjQsImlhdCI6MTUxMDQwNTkyNCwianRpIjoidG9rXzAwMDA5UVJvZlFqVW1IZjl4SE5OT1QiLCJ1aSI6InVzZXJfMDAwMDk4YjlMc3R0TTRpMnVBODFiZCIsInYiOiIyIn0.cK_o_0bUtuD27QZyiHV6FJZxadnu5avUVTHdzuo8h90'}
    r = requests.get(url, headers=headers)

    return r.json()

def getAccountDetails():
    resp = call('https://api.monzo.com/accounts')
    #json.loads(resp)
    return [resp['accounts'][1]['account_number'], resp['accounts'][1]['sort_code'], resp['accounts'][1]['id']]

print(getAccountDetails()[0])