import requests

url = "https://api.monzo.com/feed"

payload = "account_id=acc_00009G2xtSTOgOD3SYXO3F&type=basic&params%5Btitle%5D=test&params%5Bbody%5D=testagain&params%5Bimage_url%5D=http%3A%2F%2Fwww.nyan.cat%2Fcats%2Foriginal.gif"
headers = {
    'authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6Im9hdXRoY2xpZW50XzAwMDA5NFB2SU5ER3pUM2s2dHo4anAiLCJleHAiOjE1MTA0NzQ4MzMsImlhdCI6MTUxMDQ1MzIzMywianRpIjoidG9rXzAwMDA5UVN4MkhrekpGU0I4RklINmYiLCJ1aSI6InVzZXJfMDAwMDk4YjlMc3R0TTRpMnVBODFiZCIsInYiOiIyIn0.yxBoa-gTfpyHsuLNyJO9tUpX_rdTgW-NmRURDGO6hJk",
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'postman-token': "e8579ff1-4d58-911e-25af-bbe5d2d171e5"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)