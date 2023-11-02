
import requests
import time
from datetime import datetime, timedelta
import mysql.connector as sql
import schedule

'''
######################################################
THIS SECTION IS FOR CONFIGURATION OF YOUR ACCOUNT DETAILS.
API key available at https://octopus.energy/dashboard/new/accounts/personal-details/api-access
######################################################
'''
accn_number =        "ACCCOUNT NUMBER"
product_code =       "PRODUCT CODE"
tariff_code =        "TARIFF CODE"
intelligent_go_url = f"https://api.octopus.energy/v1/products/{product_code}/"
move_in_date =       "2023-10-20T00:00:00" #or use the date you would like to start getting data.
base_url =           "https://api.octopus.energy/v1" #take care with trailing slash (don't use it).
api_key =            "YOUR API KEY"
today =              datetime.now()
today_date_string =  today.strftime("%Y-%m-%dT00:00:00")
#electricity config
mpan =              "ELEC METER MPAN NUMBER"
serialno =          "ELEC SERIAL NUMBER"
#gas config
mprn =              "GAS MPRN NUMBER"
gas_serial_number = "GAS SERIAL NUMBER"
start_cheap = timedelta(hours=23, minutes=30) #change these values if the cheap rate starts at a different time
end_cheap = timedelta(hours=5, minutes=30) #change these values if the cheap rate starts at a different time

'''
######################################################
END OF MAIN CONFIG
You still need to configure your SQL Server details on line 72
######################################################
'''

#urls
elec_consumption_url =    f"{base_url}/electricity-meter-points/{mpan}/meters/{serialno}/consumption/?page_size=25000&period_from={move_in_date}Z&period_to={today_date_string}Z&order_by=period"
account_url =             f"{base_url}/accounts/{accn_number}/"
elec_rates_url =          f"{base_url}/products/{product_code}/electricity-tariffs/{tariff_code}/standard-unit-rates/"
elec_standingcharge_url = f"{base_url}/products/{product_code}/electricity-tariffs/{tariff_code}/standing-charges/"
elec_day_unit_url =       f"{base_url}/products/{product_code}/electricity-tariffs/{tariff_code}/day-unit-rates/"
elec_night_unit_url =     f"{base_url}/products/{product_code}/electricity-tariffs/{tariff_code}/night-unit-rates/"
gas_unit_url =            f"{base_url}/v1/products/{product_code}/gas-tariffs/{tariff_code}/standing-charges/"
gas_consumption_url =     f"{base_url}/gas-meter-points/{mprn}/meters/{gas_serial_number}/consumption/"

#retrieve accountinfo
account_details =          requests.get(account_url, auth=(api_key,''))
elec_consumption_details = requests.get(elec_consumption_url, auth=(api_key,''))
elec_unit_rates =          requests.get(elec_rates_url, auth=(api_key,''))
elec_standingcharges =     requests.get(elec_standingcharge_url, auth=(api_key,''))
elec_day_unit_rates =      requests.get(elec_day_unit_url, auth=(api_key,''))
elec_day_unit_rates =      requests.get(elec_night_unit_url, auth=(api_key,''))
gas_unit_rates =           requests.get(gas_unit_url, auth=(api_key,''))
gasconsumption =           requests.get(gas_consumption_url, auth=(api_key,''))


def GetElectric():
    today =              datetime.now()
    today_date_string =  today.strftime("%Y-%m-%d %H:%M:%S")
    print("Getting the data from Octopus Energy API...")
    print(f"The time is: {today_date_string}")

    #connect to sql database
    '''
    ######################################################
    Add SQL Server details below
    ######################################################
    '''
    db = sql.connect(
    host="HOST ADDRESS",
    user="SQL USER",
    passwd="SQL PASSWORD",
    database="SQL DATABASE NAME")
    addtodata = db.cursor()
    '''
    ######################################################
    END SQL config
    ######################################################
    '''

    #get values
    standing_charges = elec_standingcharges.json()
    standing_charge =  standing_charges['results'][0]['value_inc_vat']/100
    prices =           elec_unit_rates.json()
    highrate =         prices['results'][1]['value_inc_vat']/100
    lowrate =          prices['results'][0]['value_inc_vat']/100
    elec_rows =        elec_consumption_details.json()

    
    addtodata.execute("TRUNCATE TABLE electricity") #clear out the sql table ready for new values, 25000 results from octopus give a year of 30mins results
    for values in elec_rows['results']:
        for value in values:
            kwh =            values['consumption']
            jsontime =       values['interval_start']
            startdate =      values['interval_start'][0:10]
            starttime =      values['interval_start'][11:19]
            starttimestamp = startdate +" "+ starttime
            enddate =        values['interval_end'][0:10]
            endtime =        values['interval_end'][11:19]
            endtimestamp =   enddate +" "+ endtime
            #have to format as time becuase python hated me for comparing time strings
            formattedstarttime = timedelta(hours=(int(starttime[0:2])),minutes=int(starttime[3:5]))
            formattedendtime = timedelta(hours=(int(endtime[0:2])),minutes=int(endtime[3:5]))
            #is it BST?
            if len(jsontime) > 20:
                summer = 1
            else:
                summer = 0
            #which rate to use?
            if formattedstarttime <= start_cheap and formattedendtime > end_cheap:
                if starttime == "12:00:00":
                    cost = kwh * highrate + standing_charge
                    rateused = "On High Rate, Standing Charge Added"
                    car_charge_cost = 0
                else:
                     cost = kwh * highrate
                     rateused = "On High Rate"
                     car_charge_cost = 0
            else:
                    cost = kwh * lowrate
                    rateused = "On Low Rate"
                    #this car charging is not accurate, its totalling the whole use cost on low rate, but the car may not charge for all 6 hours.
                    car_charge_cost = kwh * lowrate

        #send the data collected to the sql table
        addtodata.execute("INSERT INTO electricity (kwh, high_price, low_price,\
        standing_charge, start_time, end_time, rate, cost, car_charge_cost, summer_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",\
        (kwh, highrate, lowrate, standing_charge, starttimestamp, endtimestamp, rateused, cost, car_charge_cost, summer))
    db.commit()
    print("Electrickery has been gotten")
    print(f"Last retrieved at {today_date_string}")

schedule.every().day.at("07:30").do(GetElectric)

#run once on manual startup
do_once = True
while do_once:
     print("Getting the data for initial startup!")
     GetElectric()
     do_once = False
    
while True:
    schedule.run_pending()
    time.sleep(1)
