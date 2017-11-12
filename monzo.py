import requests
import json
import urllib
import sys
import locale
import babel.numbers
import decimal
import dateutil.parser
import datetime

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6Im9hdXRoY2xpZW50XzAwMDA5NFB2SU5ER3pUM2s2dHo4anAiLCJleHAiOjE1MTA0NzQ4MzMsImlhdCI6MTUxMDQ1MzIzMywianRpIjoidG9rXzAwMDA5UVN4MkhrekpGU0I4RklINmYiLCJ1aSI6InVzZXJfMDAwMDk4YjlMc3R0TTRpMnVBODFiZCIsInYiOiIyIn0.yxBoa-gTfpyHsuLNyJO9tUpX_rdTgW-NmRURDGO6hJk'}


def call(url, payload):
    r = requests.get(url, params=urllib.urlencode(payload, doseq = True), headers=headers)
    return r.json()

def getAccountDetails():
    resp = call('https://api.monzo.com/accounts', {})
    return [resp['accounts'][1]['account_number'], resp['accounts'][1]['sort_code'], resp['accounts'][1]['id'], resp['accounts'][1]['description']]

def getBalance():
    resp = call('https://api.monzo.com/balance', {'account_id': getAccountDetails()[2]})
    return [(-1 * resp['spend_today']/100), resp['balance']/100]

def getTransactions():
    resp = call('https://api.monzo.com/transactions', {'account_id': getAccountDetails()[2]})
    return resp

def calcCosts():
    mIn = 0.0
    mOut = 0.0
    for val in getTransactions()["transactions"]:
        if "decline_reason" not in val:
            current = val["amount"]
            if current < 0: mOut -= current
            else: mIn += current

    return("Total In: " + str(mIn / 100) + "\nTotal Out: " + str(mOut / 100) + "\nNet: " + str((mIn - mOut) / 100))

def formatTransaction(transaction):
    return (("Description: " + transaction['description']
            +"\nAmount: " + babel.numbers.format_currency(decimal.Decimal(transaction['amount']/100), 'GBP')
            +"\nDate: " + transaction['created']
            +"\nCurrency: " + transaction['currency']
            +"\nTransaction ID: " + transaction['id']
            +"\nNotes: " + transaction['notes'])).encode('utf-8')

def filterTransaction(pendingBool):
    arr = getTransactions()["transactions"]
    categories = ['general', 'eating_out', 'expenses', 'transport', 'cash', 'bills', 'entertainment', 'shopping', 'holidays', 'groceries']
    categoriesShort = ['ge', 'eo', 'ex', 't', 'c', 'b', 'en', 's', 'h', 'gr']
    for currentTransaction in range(len(arr)):
            for i in range(len(categories)):
                if(arr[currentTransaction]['category'] == categories[i] and (sys.argv[2] == categories[i] or sys.argv[2]== categoriesShort[i])):
                    if(pendingBool):
                        if(arr[currentTransaction]['settled'] == '' and arr[currentTransaction]['notes'] != 'Active card check'):
                            print(formatTransaction(arr[currentTransaction])+"\n-------------------")
                    else:
                        print(formatTransaction(arr[currentTransaction]) + "\n-------------------")

def filterDateTransaction(start, end):
    arr = getTransactions()["transactions"]
    for val in arr:
        parsed1 = dateutil.parser.parse(start)
        parsed2 = dateutil.parser.parse(end).replace(tzinfo=None)
        input_parsed = dateutil.parser.parse(val['created']).replace(tzinfo=None)

        if parsed1 <= input_parsed  <= parsed2: 
            print(formatTransaction(val)+"\n-------------------")

def feedItem(title, body, image):
    #NOT POSSIBEL TO URLENCODE 2D IN PYTHON
    r = requests.post("https://api.monzo.com/feed", params=urllib.urlencode({"account_id": getAccountDetails()[2], "type": "basic","params": {"title": "test", "body": body, "image_url": image}},doseq = True), headers=headers)
    #print(r.request.form)
    return r.content;

# Argument logic
if(len(sys.argv) > 1):
    if(sys.argv[1] == "details"):
        acc = getAccountDetails()
        print("Account Holder: " + acc[3] + "\nAccount number: " + acc[0] + "\nSort code: " + acc[1]  + "\nBIC number: MONZGB21" + "\nBank address: 230 City Road, London EC1V 2QY")
    elif(sys.argv[1] == "balance"):
        bal = getBalance()
        print("Balance: " + babel.numbers.format_currency(decimal.Decimal(bal[1]), 'GBP') + "\nSpent today: " + babel.numbers.format_currency(decimal.Decimal(bal[0]), 'GBP'))
    elif(sys.argv[1] == "transactions"):
        if(len(sys.argv) == 3):
            filterTransaction(False)
        else:
            for val in getTransactions()['transactions']:
                print(formatTransaction(val)+"\n-------------------")
    elif(sys.argv[1] == "spent"):
        print(calcCosts())
    elif(sys.argv[1] == "pending"):
        arr = getTransactions()['transactions']
        if(len(sys.argv) ==3):
            filterTransaction(True)

        else:
            for i in range(len(arr)):
                    if(arr[i]['settled'] == '' and arr[i]['notes'] != 'Active card check'):
                        print(formatTransaction(arr[i])+"\n-------------------")
    elif(sys.argv[1] == "transaction_filter"):
        if(len(sys.argv) == 4):
            filterDateTransaction(sys.argv[2], sys.argv[3])
        else:
            print("Error: missing param")
    elif(sys.argv[1] == "feed_item"):
        if(len(sys.argv) == 5):
            #feedItem(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
            print(feedItem("Test thing", "more test thing", "http://www.nyan.cat/cats/original.gif"))
        else:
            print("Error: missing param")    

    else:
        print("Command not found. \n \nTry: \ndetails: list your account details"+
        "\nbalance: list your balance\ntransactions: list all transactions"+
        "\nspent: display total input and output"+
        "\npending: show all transactions that have not been settled"+
        "\nTransaction_filter (start date, end date): filter transaction by date range")
