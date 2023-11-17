'''

This script takes in csv files exported from octopus from any date range you choose on their site and adds it to the
preconfigured SQL tables as described at https://github.com/milkandbourbons/octopus-energy-sql#step-advanced-1-quicker-less-prone-to-mitstakes

Caveats are that the JSON data usually returned from the API, the gas data is already in kWh. but when exported as csv from:
https://octopus.energy/dashboard/new/accounts/YOURACCOUNT/consumption/home under "Get Your Geek On", they are delivered
in cubic meters. This script converts to kWh using an industry standard formula as described at:
https://octopus.energy/blog/statement-questions/#:~:text=Your%20energy%20usage%20is%20calculated,%2D%20Usage%20(in%20kWh).
You will need to confirm the calorific values from your paper bill if you want it to be exact. Enter the numbers on line 138-140.

'''

import pandas as pd
from datetime import timedelta, datetime
import _config
import requests
import mysql.connector as sql
today =                  datetime.now()
today_date_string =      today.strftime(f"%Y-%m-%dT%H:%M:%S")
start_cheap = timedelta(hours=int(_config.cheap_rate_start_time[0:2]), minutes=int(_config.cheap_rate_start_time[3:5]))
end_cheap = timedelta(hours=int(_config.cheap_rate_stop_time[0:2]), minutes=int(_config.cheap_rate_stop_time[3:5]))


#urls
intelligent_go_url =       f"{_config.base_url}/products/{_config.product_code}/"
elec_consumption_url =     f"{_config.base_url}/electricity-meter-points/{_config.mpan}/meters/{_config.serialno}/consumption/?page_size=25000&period_from={_config.move_in_date}Z&period_to={today_date_string}Z&order_by=period"
account_url =              f"{_config.base_url}/accounts/{_config.accn_number}/"
elec_rates_url =           f"{_config.base_url}/products/{_config.product_code}/electricity-tariffs/{_config.tariff_code}/standard-unit-rates/"
elec_standingcharge_url =  f"{_config.base_url}/products/{_config.product_code}/electricity-tariffs/{_config.tariff_code}/standing-charges/"
elec_day_unit_url =        f"{_config.base_url}/products/{_config.product_code}/electricity-tariffs/{_config.tariff_code}/day-unit-rates/"
elec_night_unit_url =      f"{_config.base_url}/products/{_config.product_code}/electricity-tariffs/{_config.tariff_code}/night-unit-rates/"
gas_standing_charge_url =  f"{_config.base_url}/products/{_config.gas_product_code}/gas-tariffs/{_config.gas_tariff_code}/standing-charges/"
gas_unit_url =             f"{_config.base_url}/products/{_config.gas_product_code}/gas-tariffs/{_config.gas_tariff_code}/standard-unit-rates/"
gas_consumption_url =      f"{_config.base_url}/gas-meter-points/{_config.mprn}/meters/{_config.gas_serial_number}/consumption/?page_size=25000&period_from={_config.move_in_date}Z&period_to={today_date_string}Z&order_by=period"

#retrieve accountinfo
account_details =           requests.get(account_url, auth=(_config.api_key,''))

###ELEC
elec_consumption_details =  requests.get(elec_consumption_url, auth=(_config.api_key,''))
elec_unit_rates =           requests.get(elec_rates_url, auth=(_config.api_key,''))
elec_standingcharges =      requests.get(elec_standingcharge_url, auth=(_config.api_key,''))
elec_day_unit_rates =       requests.get(elec_day_unit_url, auth=(_config.api_key,''))
elec_night_unit_rates =     requests.get(elec_night_unit_url, auth=(_config.api_key,''))

###GAS
gas_standing_charges =      requests.get(gas_standing_charge_url, auth=(_config.api_key,''))
gas_unit_rates =            requests.get(gas_unit_url, auth=(_config.api_key,''))
gas_consumption_details =   requests.get(gas_consumption_url, auth=(_config.api_key,''))

db = sql.connect(
    host =      _config.sql_host_address,
    user =      _config.sql_user,
    passwd =    _config.sql_password,
    database =  _config.sql_database)
addtodata = db.cursor()

#load csv at local location:
df1 = pd.read_csv(_config.elec_csv_location)
df2 = pd.read_csv(_config.gas_csv_location)


def ProcessElec():
    today =              datetime.now()
    today_date_string =  today.strftime("%Y-%m-%d %H:%M:%S")
    print("Getting the data from Octopus Energy API...")
    print("Getting Electic data...")
    #get values
    standing_charges = elec_standingcharges.json()
    prices =           elec_unit_rates.json()
    highrate =         prices['results'][1]['value_inc_vat']/100
    lowrate =          prices['results'][0]['value_inc_vat']/100
    elec_rows =        elec_consumption_details.json()
    threshold_val =    2.9 # sensitivity for detecting car plug-in. Must be a float greater than 2.0
    addtodata.execute("TRUNCATE TABLE electricity") #clear out the sql table ready for new values, 25000 results from octopus give a year of 30mins results
    for index, values in df1.iterrows():
        car_charge_cost      = 0
        standing_charge      = 0
        bump_charge_cost     = 0
        jsontime =           values[' Start'] #len=26
        startdate =          values[' End'][0:11]
        starttime =          values[' Start'][12:20]
        starttimestamp =     startdate +" "+ starttime
        enddate =            values[' End'][0:11]
        endtime =            values[' End'][12:20]
        endtimestamp =       enddate +" "+ endtime
        kwh =                values['Consumption (kWh)']
        formattedstarttime = timedelta(hours=(int(jsontime[12:14])),minutes=int(jsontime[15:17]))
        formattedendtime = timedelta(hours=(int(jsontime[12:14])),minutes=int(jsontime[15:17]))
#threshold helps detect a plugged in car, divided by 2 for result per 30mins + 0.9 for sensitivity for very short plug-in durations.
        car_charging_threshold = float(_config.ev_charger_size)/threshold_val
        #is it BST?
        if len(jsontime) > 20:
            summer = 1
        else:
            summer = 0
        #which rate to use?
        if formattedstarttime <= start_cheap and formattedendtime > end_cheap:
            if starttime == "12:00:00":
                standing_charge = standing_charges['results'][0]['value_inc_vat']/100
                if kwh > float(_config.ev_charger_size)/threshold_val:
                    bump_charge_cost = kwh * highrate
                    rateused = "On High Rate, Standing Charge Added and Bump Charging"
                    cost = kwh * highrate + standing_charge
                else:
                    cost = kwh * highrate + standing_charge
                    rateused = "On High Rate, Standing Charge Added"
                    current_price = prices['results'][1]['value_inc_vat']/100
            else:
                    cost = kwh * highrate
                    rateused = "On High Rate"
                    standing_charge = 0
                    current_price = prices['results'][1]['value_inc_vat']/100
                    if kwh > float(_config.ev_charger_size)/threshold_val:
                        bump_charge_cost = kwh * highrate
                        rateused = "On High Rate, Bump Charging"
        else:
                cost = kwh * lowrate
                rateused = "On Low Rate"
                standing_charge = 0
                current_price = prices['results'][0]['value_inc_vat']/100
                if kwh >= float(_config.ev_charger_size)/threshold_val: #a 7kw charger draws 3.5kw per 30 mins...
                    car_charge_cost = kwh * lowrate
                    rateused = "On Low Rate, Car Charging" 
        #send the data collected to the sql table

        addtodata.execute("INSERT INTO electricity (kwh, high_price, low_price, current_price,\
        standing_charge, start_time, end_time, rate, cost, car_charge_cost, bump_charge_cost, threshold, summer_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",\
        (kwh, highrate, lowrate, current_price, standing_charge, starttimestamp, endtimestamp, rateused, cost, car_charge_cost, bump_charge_cost, car_charging_threshold,summer))
        db.commit()


    print("Electric data done.")

def ProcessGas():
    print("Getting Gas data...")
    gas_consumption =        gas_consumption_details.json()
    gas_standing_details =   gas_standing_charges.json()
    gas_prices =             gas_unit_rates.json()
    gas_price =              gas_prices['results'][1]['value_inc_vat']/100
    calorific_value =        39.3
    vol_correction =         1.02264
    convert_from_joules =    3.6
    addtodata.execute("TRUNCATE TABLE gas") #clear out the sql table ready for new values, 25000 results from octopus give a year of 30mins results
    for index, values in df2.iterrows():
        gas_startdate =          values[' Start'][0:11]
        gas_starttime =          values[' Start'][12:20]
        gas_starttimestamp =     gas_startdate +" "+ gas_starttime
        gas_enddate =            values[' End'][0:11]
        gas_endtime =            values[' End'][12:20]
        gas_endtimestamp =       gas_enddate +" "+ gas_endtime
        gas_kwh =                values['Consumption (m³)'] * vol_correction * calorific_value / convert_from_joules
        if gas_starttime == "12:00:00":
            gas_standing_charge =    gas_standing_details['results'][0]['value_inc_vat']/100
            gas_cost = gas_kwh * gas_price + gas_standing_charge
        else:
            gas_cost = gas_kwh * gas_price 
            gas_standing_charge = 0
        addtodata.execute("INSERT INTO gas (gas_kwh, start_time, end_time, standing_charge, cost) VALUES (%s, %s, %s, %s, %s)",\
        (gas_kwh, gas_starttimestamp, gas_endtimestamp, gas_standing_charge, gas_cost))
    db.commit()
    print("Gas data done.")

ProcessElec()
ProcessGas()
db.close()