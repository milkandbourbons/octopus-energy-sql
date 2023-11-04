#!/usr/bin/python3
import requests
import time
from datetime import datetime, timedelta
import mysql.connector as sql
import schedule
import _config

today =                  datetime.now()
today_date_string =      today.strftime("%Y-%m-%dT00:00:00")

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
gas_unit_url =             f"{_config.base_url}/v1/products/{_config.product_code}/gas-tariffs/{_config.tariff_code}/standing-charges/"
gas_consumption_url =      f"{_config.base_url}/gas-meter-points/{_config.mprn}/meters/{_config.gas_serial_number}/consumption/"

#retrieve accountinfo
account_details =          requests.get(account_url, auth=(_config.api_key,''))
elec_consumption_details = requests.get(elec_consumption_url, auth=(_config.api_key,''))
elec_unit_rates =          requests.get(elec_rates_url, auth=(_config.api_key,''))
elec_standingcharges =     requests.get(elec_standingcharge_url, auth=(_config.api_key,''))
elec_day_unit_rates =      requests.get(elec_day_unit_url, auth=(_config.api_key,''))
elec_day_unit_rates =      requests.get(elec_night_unit_url, auth=(_config.api_key,''))
gas_unit_rates =           requests.get(gas_unit_url, auth=(_config.api_key,''))
gasconsumption =           requests.get(gas_consumption_url, auth=(_config.api_key,''))


def GetElectric():
    today =              datetime.now()
    today_date_string =  today.strftime("%Y-%m-%d %H:%M:%S")
    print("Getting the data from Octopus Energy API...")

    #connect to sql database

    db = sql.connect(
    host =      _config.sql_host_address,
    user =      _config.sql_user,
    passwd =    _config.sql_password,
    database =  _config.sql_database)
    addtodata = db.cursor()

    #get values
    standing_charges = elec_standingcharges.json()
    prices =           elec_unit_rates.json()
    highrate =         prices['results'][1]['value_inc_vat']/100
    lowrate =          prices['results'][0]['value_inc_vat']/100
    elec_rows =        elec_consumption_details.json()

    
    addtodata.execute("TRUNCATE TABLE electricity") #clear out the sql table ready for new values, 25000 results from octopus give a year of 30mins results
    for values in elec_rows['results']:
        car_charge_cost = 0
        standing_charge = 0
        jsontime =           values['interval_start']
        startdate =          values['interval_start'][0:10]
        starttime =          values['interval_start'][11:19]
        starttimestamp =     startdate +" "+ starttime
        enddate =            values['interval_end'][0:10]
        endtime =            values['interval_end'][11:19]
        endtimestamp =       enddate +" "+ endtime
        # had to format as time becuase python hated me for comparing time strings
        formattedstarttime = timedelta(hours=(int(starttime[0:2])),minutes=int(starttime[3:5]))
        formattedendtime =   timedelta(hours=(int(endtime[0:2])),minutes=int(endtime[3:5]))
        kwh =                values['consumption']
        #is it BST?
        if len(jsontime) > 20:
            summer = 1
        else:
            summer = 0
        #which rate to use?
        if formattedstarttime <= start_cheap and formattedendtime > end_cheap:
            if starttime == "12:00:00":
                standing_charge = standing_charges['results'][0]['value_inc_vat']/100
                cost = kwh * highrate + standing_charge
                rateused = "On High Rate, Standing Charge Added"
            else:
                    cost = kwh * highrate
                    rateused = "On High Rate"
                    standing_charge = 0
        else:
                cost = kwh * lowrate
                rateused = "On Low Rate"
                standing_charge = 0
                if kwh >= 2.2: #a 7kw charger draws 3.5kw per 30 mins, i found in testing that nothing draws more than 2.2kw at
                               #night apart from the car, so this for me is a reliable metric for the car being on charge. YMMV
                    car_charge_cost = kwh * lowrate  
                    

        #send the data collected to the sql table
        addtodata.execute("INSERT INTO electricity (kwh, high_price, low_price,\
        standing_charge, start_time, end_time, rate, cost, car_charge_cost, summer_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",\
        (kwh, highrate, lowrate, standing_charge, starttimestamp, endtimestamp, rateused, cost, car_charge_cost, summer))
    db.commit()
    print("Electrickery has been gotten")
    print(f"Last retrieved at {today_date_string}")
    print(f"I will get fresh data at {_config.schedule_time} tomorrow.")
    print("waiting...")

schedule.every().day.at(_config.schedule_time).do(GetElectric)

#run once on manual startup
do_once = True
while do_once:
     print("Getting the data for initial startup!")
     GetElectric()
     do_once = False
    
while True:
    schedule.run_pending()
    time.sleep(1)
