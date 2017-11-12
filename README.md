# monzo-cli

A terminal client for the Monzo Bank API - developers.monzo.com

## Installation
### Required Packages
 - Python 2.7.x
 - python-pip
 
 #### python packages
- requests
- json
- urllib
- sys
- locale
- babel.numbers
- decimal
- dateutil.parser
- datetime

### Instructions
1. Clone/Download the repository 
2. Install the required dependancies 
3. At the top of your file, add the access token aquired from developers.monzo.com
4. Have fun...

To run the script: `./monzo {commands}`

### Commands

`details ()`: outputs your account details 

`balance ()`: outputs todays spend and balance 

`transactions (*optional* catagory)`: outputs all transactions, optionally filtered by catagory 

`transaction_filter (start_date, end date)`: outputs all transactions within the specified period 

`pending ()`: outputs authorised but not presented transactions 

`spent ()`: outputs total cashflow 

`feed_item (title, description, image_url)`: generates a feed item 


## Upgrades
- Full oAuth2 support 
- Better handling of parameters (ie. composite commands) 
