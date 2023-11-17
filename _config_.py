#!/usr/bin/python3

'''

THIS SECTION IS FOR CONFIGURATION OF YOUR ACCOUNT DETAILS.
API key available at https://octopus.energy/dashboard/new/accounts/personal-details/api-access
Also available on that link are the account number, mpan and mprn. The API key starts "sk_live_xxxx...."

Fine account details such as product_code and tariff_code below can be viewed as JSON at
https://api.octopus.energy/v1/accounts/<your account number>, just squint and look along to find the tariff name you
are on and the other details are there between the curly braces.

Every value should be a string, ie. "inside quotes".

'''
elec_csv_location =      "elec.csv"
gas_csv_location =       "gas_in_cubes.csv"
base_url =               "https://api.octopus.energy/v1" #take care with trailing slash (don't use it)
accn_number =            "YOUR ACCOUNT NUMBER"
product_code =           "YOUR PRODUCT CODE"
tariff_code =            "YOUR TARIFF CODE"
gas_product_code =       "YOUR GAS PRODUCT CODE" # gas product code, probably "VAR-22-11-01"
gas_tariff_code =        "YOU GAS TARIFF CODE" # gas tariff code, probably similar to "G-1R-VAR-22-11-01-D"
move_in_date =           "2023-10-20T00:00:00" # or use the date you would like to start getting data.
api_key =                "sk_live_THE REST OF THE KEY"
cheap_rate_start_time =  "23:30"
cheap_rate_stop_time =   "05:30"
sql_host_address =       "IP ADDRESS OR FQDN"
sql_user =               "SQL USERNAME"
sql_password =           "SQL PASSWORD"
sql_database =           "octopus"
schedule_time =          "07:30" # the time for the script to grab fresh data from octopus - they only update once per 24hrs, after midnight.
ev_charger_size =        "7.2"   # Value in kw
                                 # a 7.2kw charger draws ~3.5kw per 30 mins, this value is being used to determine if a car is on charge or not.
                                 # If, for example, you have a charger with an output of 22kw - you would enter "22.0" (a decimal must be used)      YMMV
#electricity config
mpan =                   "MPAN NUMBER OF THE METER"
serialno =               "SERIAL NUMBER OF THE METER"
#gas config
mprn =                   "MPRN OF THE GAS METER"
gas_serial_number =      "GAS SERIAL NUMBER"
'''

END OF MAIN CONFIG

'''