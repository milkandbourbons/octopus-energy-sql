#!/usr/bin/python3
'''

THIS SECTION IS FOR CONFIGURATION OF YOUR ACCOUNT DETAILS.
API key available at https://octopus.energy/dashboard/new/accounts/personal-details/api-access
Also available on that link are the account number, mpan and mprn. The API key starts "sk_live_xxxx...."

Fine account details such as product_code and tariff_code below can be viewed as JSON at
https://api.octopus.energy/v1/products/, just squint and look along to find the tariff name you
are on and the other details are there between the curly braces.

Every value should be a string, ie. "inside quotes".

'''
accn_number =            "YOUR ACCOUNT NUMBER"
product_code =           "YOUR PRODUCT CODE"
base_url =               "https://api.octopus.energy/v1" #take care with trailing slash (don't use it).
tariff_code =            "YOUR TARIFF CODE"
move_in_date =           "2023-10-20T00:00:00" #or use the date you would like to start getting data.
api_key =                "sk_live_THE REST OF THE KEY"
cheap_rate_start_time =  "23:30"
cheap_rate_stop_time =   "05:30"
sql_host_address =       "IP ADDRESS OR FQDN"
sql_user =               "SQL USERNAME"
sql_password =           "SQL PASSWORD"
sql_database =           "SQL DATABASE NAME"
schedule_time =          "07:30" #the time for the script to grab fresh data from octopus - they only update once per 24hrs, after midnight.

#electricity config
mpan =                   "MPAN NUMBER OF THE METER"
serialno =               "SERIAL NUMBER OF THE METER"
#gas config
mprn =                   "MPRN OF THE GAS METER"
gas_serial_number =      "GAS SERIAL NUMBER"

'''

END OF MAIN CONFIG

'''
