import requests
import json
import urllib
import sys
import locale
import babel.numbers
import decimal

def call(url, payload):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8', 'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjaSI6Im9hdXRoY2xpZW50XzAwMDA5NFB2SU5ER3pUM2s2dHo4anAiLCJleHAiOjE1MTA0NTE3NjAsImlhdCI6MTUxMDQzMDE2MCwianRpIjoidG9rXzAwMDA5UVNPaVZBNk1iQnV1VmFKbDMiLCJ1aSI6InVzZXJfMDAwMDk4YjlMc3R0TTRpMnVBODFiZCIsInYiOiIyIn0.Iw8F8eXnfb0v9ac6co7_rSa44i4T3H3GDylgAqGIy7M'}
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
        cValue = val["amount"]
        if (cValue < 0):
            mOut += (cValue * -1)
        else:
            mIn += cValue
    return("Total In: " + str(mIn) + "\nTotal Out: " + str(mOut) + "\nNet: " + str(mIn - mOut))

def formatTransaction(transaction):
    return ("Description: " + transaction['description']
            +"\nAmount: " + babel.numbers.format_currency(decimal.Decimal(transaction['amount']/100), 'GBP')
            +"\nDate: " + transaction['created']
            +"\nCurrency: " + transaction['currency']
            +"\nTransaction ID: " + transaction['id']
            +"\nNotes: " + transaction['notes'])

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

    else:
        print("Command not found. \n \nTry: \ndetails: list your account details"+
        "\nbalance: list your balance\ntransactions: list all transactions"+
        "\nspent: display total input and output"+
        "\npending: show all transactions that have not been settled")
