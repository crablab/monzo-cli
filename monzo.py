import requests
import json
import urllib
import sys
import locale
import babel.numbers
import decimal
import dateutil.parser
import datetime

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6Im9hdXRoY2xpZW50XzAwMDA5NFB2SU5ER3pUM2s2dHo4anAiLCJleHAiOjE1MTA0OTcyOTUsImlhdCI6MTUxMDQ3NTY5NSwianRpIjoidG9rXzAwMDA5UVRVUmpLTEVwejZucWlpZFYiLCJ1aSI6InVzZXJfMDAwMDk4YjlMc3R0TTRpMnVBODFiZCIsInYiOiIyIn0.BWIrY2Pp9W8sDbJ7trjZUJA-hwPnhO3G1i7l3l3evAs"
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer ' + key}


def call(url, payload):
    r = requests.get(url, params=urllib.urlencode(payload, doseq = True), headers=headers)
    return r.json()

def getAccountDetails():
    resp = call('https://api.monzo.com/accounts', {})
    return [resp['accounts'][1]['account_number'], resp['accounts'][1]['sort_code'], resp['accounts'][1]['id'], resp['accounts'][1]['description']]

def getBalance():
    resp = call('https://api.monzo.com/balance', {'account_id': getAccountDetails()[2]})
    return [(-1 * float(resp['spend_today'])/100), float(resp['balance'])/100]

def getTransactions():
    resp = call('https://api.monzo.com/transactions', {'account_id': getAccountDetails()[2]})
    return resp

def calcCosts(transArray):
    mIn = 0.0
    mOut = 0.0
    for val in transArray:
        #disregard declined transactions
        if "decline_reason" not in val:
            current = val["amount"]
            #inputs are positive, outputs are negative
            if current < 0: mOut -= current
            else: mIn += current

    return("Total In: " + babel.numbers.format_currency(decimal.Decimal(str(mIn / 100)), 'GBP') + "\nTotal Out: " + babel.numbers.format_currency(decimal.Decimal(str(mOut / 100)), 'GBP') + "\nNet: " + babel.numbers.format_currency(decimal.Decimal(str((mIn-mOut) / 100)), 'GBP'))

def formatTransaction(transaction):
    #format the output
    return (("Description: " + transaction['description']
            +"\nAmount: " + babel.numbers.format_currency(decimal.Decimal(float(transaction['amount'])/100), 'GBP')
            +"\nDate: " + transaction['created']
            +"\nCurrency: " + transaction['currency']
            +"\nTransaction ID: " + transaction['id']
            +"\nNotes: " + transaction['notes'])).encode('utf-8')

def filterTransaction(pendingBool):
    arr = getTransactions()["transactions"]
    trans_arr = []
    #categories
    categories = ['general', 'eating_out', 'expenses', 'transport', 'cash', 'bills', 'entertainment', 'shopping', 'holidays', 'groceries']
    categoriesShort = ['ge', 'eo', 'ex', 't', 'c', 'b', 'en', 's', 'h', 'gr']
    #for every element, check it against every category
    for currentTransaction in range(len(arr)):
            for i in range(len(categories)):
                if(arr[currentTransaction]['category'] == categories[i] and (sys.argv[2] == categories[i] or sys.argv[2]== categoriesShort[i])):
                    #only look at non settled payments
                    if(pendingBool):
                        if(arr[currentTransaction]['settled'] == '' and arr[currentTransaction]['notes'] != 'Active card check'):
                            print(formatTransaction(arr[currentTransaction])+"\n-------------------")
                            trans_arr.append(arr[currentTransaction])
                    else:
                        print(formatTransaction(arr[currentTransaction]) + "\n-------------------")
                        trans_arr.append(arr[currentTransaction])
    #calculate the input/ouput and print
    print(calcCosts(trans_arr))

def filterDateTransaction(start, end):
    #filter by date
    arr = getTransactions()["transactions"]
    trans_arr = []
    for val in arr:
        parsed1 = dateutil.parser.parse(start)
        parsed2 = dateutil.parser.parse(end).replace(tzinfo=None)
        input_parsed = dateutil.parser.parse(val['created']).replace(tzinfo=None)

        if parsed1 <= input_parsed  <= parsed2:
            trans_arr.append(val)
            print(formatTransaction(val)+"\n-------------------")
    print(calcCosts(trans_arr))

def feedItem(title, body, image):
    params = urllib.urlencode({"account_id": getAccountDetails()[2], "type": "basic", "params[title]": title, "params[body]": body, "params[image_url]": image})

    url = "https://api.monzo.com/feed"

    #Special headers for form encoding
    header = {
    'authorization': "Bearer " + key,
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    'postman-token': "e8579ff1-4d58-911e-25af-bbe5d2d171e5"
    }

    response = requests.request("POST", url, data=params, headers=header)

    print(response.text)
    #print(r.request.data)
    return response.content;
def help():
    #print the help
    print("Command not found. \n \nTry: \ndetails: list your account details"+
        "\nbalance: list your balance"+
        "\ntransactions (\x1B[3moptional\x1B[0m category): list all transactions"+
        "\nspent: display total input and output"+
        "\npending: show all transactions that have not been settled"+
        "\ntransaction_filter (start date, end date): filter transaction by date range")

# Argument logic
if(len(sys.argv) > 1):
    #details
    if(sys.argv[1] == "details"):
        acc = getAccountDetails()
        print("Account Holder: " + acc[3] + "\nAccount number: " + acc[0] + "\nSort code: " + acc[1]  + "\nBIC number: MONZGB21" + "\nBank address: 230 City Road, London EC1V 2QY")
    #balance
    elif(sys.argv[1] == "balance"):
        bal = getBalance()
        print("Balance: " + babel.numbers.format_currency(decimal.Decimal(bal[1]), 'GBP') + "\nSpent today: " + babel.numbers.format_currency(decimal.Decimal(bal[0]), 'GBP'))
    #transactions
    elif(sys.argv[1] == "transactions"):
        if(len(sys.argv) == 3):
            filterTransaction(False)
        else:
            for val in getTransactions()['transactions']:
                print(formatTransaction(val)+"\n-------------------")
    #amount spent
    elif(sys.argv[1] == "spent"):
        print(calcCosts(getTransactions()["transactions"]))
    #non settled payments
    elif(sys.argv[1] == "pending"):
        arr = getTransactions()['transactions']
        if(len(sys.argv) ==3):
            filterTransaction(True)
        else:
            for i in range(len(arr)):
                    if(arr[i]['settled'] == '' and arr[i]['notes'] != 'Active card check'):
                        print(formatTransaction(arr[i])+"\n-------------------")
    #filter by date
    elif(sys.argv[1] == "transaction_filter"):
        if(len(sys.argv) == 4):
            filterDateTransaction(sys.argv[2], sys.argv[3])
        else:
            print("Error: missing param")
    #feed item
    elif(sys.argv[1] == "feed_item"):
        if(len(sys.argv) == 5):
            feedItem(sys.argv[2], sys.argv[3], sys.argv[4])
        else:
            print("Error: missing param")
    #Dinosaur challenge
    elif(sys.argv[1] == "dino"):
        feedItem("Dinosaur Challenge", "Steve is badass", "http://www.animateit.net/data/media/nov2011/f44ocl.gif")

    else:
        help()
else:
    help()
