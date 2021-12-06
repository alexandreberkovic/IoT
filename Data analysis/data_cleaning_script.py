# Data cleaning script
# # Imports 

# ## Files
# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, '/Users/alexandreberkovic/Desktop/Year_4/SIoT/Iot')
from Scraping import scraping_script
# ## Packages
import pandas as pd
import datetime
import time
import warnings
import math
import statistics
import numpy as np
import scipy.stats
import openpyxl
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pyspark.sql import SparkSession
import pymongo 
from pymongo import MongoClient
import dns
from time import sleep
from pprint import pprint
from googleapiclient import discovery
from googleapiclient import errors
from df2gspread import df2gspread as d2g
from pathlib import Path
warnings.filterwarnings('ignore')

# main directory
root = Path('/Users','alexandreberkovic','Desktop', 'Year_4','SIoT','IoT')

# Google sheets API credentials for connection
# define the scope
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# add credentials to the account
creds = ServiceAccountCredentials.from_json_keyfile_name('Google_API_OAUTH.json', scope)
# authorize the clientsheet 
client = gspread.authorize(creds)

# ## API data from Sheets
def get_api():
    # get the instance of the Spreadsheet
    sheet = client.open('Sleep Data')
    # get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)
    # get all the records of the data
    api_data = sheet_instance.get_all_records()
    # convert the json to dataframe
    api = pd.DataFrame.from_dict(api_data)
    return api


# ## Sensor data from MongoDB
def get_sensor():
    # Replace the uri string with your MongoDB deployment's connection string.
    conn_str = "mongodb+srv://importdata:alexandre@iot.abtve.mongodb.net/Withings_Sleep_Data?retryWrites=true&w=majority"

    # set a 5-second connection timeout, serverSelectionTimeoutMS=5000
    clientmongo = pymongo.MongoClient(conn_str) 

    try:
        print('Available databases:')
        print(clientmongo.list_database_names())
    except Exception:
        print("Unable to connect to the server.")

    db = clientmongo.get_database('IoT')
    records = db.Withings_Sleep_Data
    list(records.find())[0]['sensors']
    data = list(records.find())
    lst = []
    for i in range(len(data)):
        lst.append([data[i]['_id'], data[i]['sensors']['humidity'],
                data[i]['sensors']['temperature'], data[i]['sensors']['light'],
                data[i]['ts']] )

    # Create the pandas DataFrame
    sensor = pd.DataFrame(lst, columns = ['_id', 'sensors.humidity', 'sensors.temperature', 'sensors.light', 'ts'])
    return sensor


# ## Scraping data
def get_scraping():
    #run scraping script to update data
    scraping_script.main()
    scraping = pd.read_csv(root / 'Scraping/Scraping_data.csv')
    return scraping


# # Cleaning

def clean_scraping(scraping):
    # ## Scraping
    # inital dataframe
    # remove useless sscolumn
    scraping = scraping.drop('Unnamed: 0', 1)
    # split period start and end time into two columns
    scraping[['Start', 'End']] = scraping['Time'].str.split('-', expand=True)
    # drop the time column
    scraping = scraping.drop('Time', 1)
    # full date/time to use as timeseries after
    scraping['Start'] = scraping['Date'] + scraping['Start']
    scraping['End'] = scraping['Date'] + ' ' + scraping['End']
    # drop useless column
    scraping = scraping.drop('Date',1)
    # formating the date and time as datetime for use as time series
    scraping['Start'] = pd.to_datetime(scraping['Start'], format = '%d %B %Y %H:%M')
    scraping['End'] = pd.to_datetime(scraping['End'], format = '%d %B %Y %H:%M')
    # add date column
    scraping['Date'] = pd.to_datetime(scraping['End']).dt.to_period('D')
    return scraping


def clean_api(api):
    # ## API
    # drop useless columns
    api = api.drop(['Device ','Mac','Snoring duration','Snoring episodes','Status','Regularity','Recovery'], 1)
    # remove unwanted text
    for i in range(len(api)):
        api['Duration'][i] = api['Duration'][i].split('SleepDuration:')[-1]
        api['In'][i] = api['In'][i].split('InBedDateandTime:')[-1]
        api['Out'][i] = api['Out'][i].split('OutofBedDateandTime:')[-1]
        api['Light Sleep'][i] = api['Light Sleep'][i].split('LightSleepDuration:')[-1]
        api['Deep Sleep'][i] = api['Deep Sleep'][i].split('DeepSleepDuration:')[-1]
        api['REM Sleep'][i] = api['REM Sleep'][i].split('RemSleepDuration:')[-1]
        api['Score'][i] = api['Score'][i].split('SleepScore:')[-1]
        api['BPM'][i] = api['BPM'][i].split('HeartRateAverage:')[-1]
        api['Awake'][i] = api['Awake'][i].split('AwakeDuration:')[-1]
        api['Interruptions'][i] = api['Interruptions'][i].split('NbInterruptions:')[-1]
        api['TTS'][i] = api['TTS'][i].split('TimeToSleep:')[-1]
    # remove leading or trailing whitespaces
    for col in api.columns:
        api[col] = api[col].str.strip()
    # format datetime
    api['In'] = pd.to_datetime(api['In'], format = '%B %d, %Y at %I:%M%p')
    api['Out'] = pd.to_datetime(api['Out'], format = '%B %d, %Y at %I:%M%p')
    #make durations as integers (minutes)
    ts = ['Duration','Light Sleep', 'Deep Sleep', 'REM Sleep', 'Awake', 'TTS']
    for col in ts:
        for i in range(len(api)):
            hour = int(api[col][i].split(':')[0])
            minute = int(api[col][i].split(':')[1])
            api[col][i] = hour*60 + minute
    # make sur int columns are good type
    api[["Score", "BPM", "Interruptions"]] = api[["Score", "BPM", "Interruptions"]].apply(pd.to_numeric)
    api['Date'] = pd.to_datetime(api['Out']).dt.to_period('D')
    return api

def clean_sensor(sensor):
    # ## Sensor
    # drop useless column
    sensor = sensor.drop('_id', 1)
    # rename other columns
    sensor = sensor.rename({'sensors.humidity': 'Humidity', 'sensors.light': 'Light', 'sensors.temperature' : 'Temperature', 'ts' : 'Time stamp'}, axis=1)
    # add date column
    sensor['Date'] = pd.to_datetime(sensor['Time stamp']).dt.to_period('D')
    return sensor

# # Analysis

# 1. need to delete sensor data not in the sleeping time frame
# 2. need to average out light, humidity and temperature
# 3. time series visualisation
# 4. simple correlations
# 5. create model to determine best sleeping criteria based on deep sleep and also score (one specific and one average out)


def sensor_bis(sensor,api):
    sensor_new = pd.DataFrame(columns = ['Humidity','Light','Temperature','Time stamp'])
    for i in range(len(api)):
        for j in range(len(sensor)):
            if api['In'][i] <= sensor['Time stamp'][j] <= api['Out'][i]:
                sensor_new = sensor_new.append(sensor.loc[[j]])
            else:
                pass
    # well the light goes directly to 0 at night ... logical but i guess that's what happens
    sensor_new = sensor_new.reset_index()
    sensor_new = sensor_new.drop('index',1)
    return sensor_new

def sensor_val(api,sensor_new):
    # ## Restrict sensor data
    humidity = pd.DataFrame(columns = ['Out','Mean', 'Median', 'Std', 'Variance', 'Min', 'Max', 'Range'])
    temperature = pd.DataFrame(columns = ['Out','Mean', 'Median', 'Std', 'Variance', 'Min', 'Max', 'Range'])
    light = pd.DataFrame(columns = ['Out','Mean', 'Median', 'Std', 'Variance', 'Min', 'Max', 'Range'])

    hum_lst = []
    temp_lst = []
    light_lst = []

    for i in range(len(api)):
        hum_lst = []
        temp_lst = []
        light_lst = []
        for j in range(len(sensor_new)):
            if api['In'][i] <= sensor_new['Time stamp'][j] <= api['Out'][i]:
                hum_lst.append(sensor_new['Humidity'][j])
                temp_lst.append(sensor_new['Temperature'][j])
                light_lst.append(sensor_new['Light'][j])
            else:
                pass
        if len(hum_lst) != 0:
                
            hum_metrics = [api['Out'][i],statistics.mean(hum_lst),statistics.median(hum_lst),statistics.stdev(hum_lst),
                        statistics.variance(hum_lst),min(hum_lst),max(hum_lst),max(hum_lst)-min(hum_lst)]
            temp_metrics = [api['Out'][i],statistics.mean(temp_lst),statistics.median(temp_lst),statistics.stdev(temp_lst),
                        statistics.variance(temp_lst),min(temp_lst),max(temp_lst),max(temp_lst)-min(temp_lst)]
            light_metrics = [api['Out'][i],statistics.mean(light_lst),statistics.median(light_lst),statistics.stdev(light_lst),
                        statistics.variance(light_lst),min(light_lst),max(light_lst),max(light_lst)-min(light_lst)]
        
            hum_length = len(humidity)
            temp_length = len(temperature)
            light_length = len(light)
            
            humidity.loc[hum_length] = hum_metrics
            temperature.loc[temp_length] = temp_metrics
            light.loc[light_length] = light_metrics

    humidity['Date'] = pd.to_datetime(humidity['Out']).dt.to_period('D')
    temperature['Date'] = pd.to_datetime(temperature['Out']).dt.to_period('D')
    light['Date'] = pd.to_datetime(light['Out']).dt.to_period('D')

    humidity = humidity.drop('Out',1)
    temperature = temperature.drop('Out',1)
    light = light.drop('Out',1)
    return humidity, temperature, light


def export_csv(sensor,sensor_new,api,scraping,light,temperature,humidity):
    sensor.to_csv(root / 'Output data/CSV/sensor.csv',index=False)
    sensor_new.to_csv(root / 'Output data/CSV/sensor_lim.csv',index=False)
    api.to_csv(root / 'Output data/CSV/api.csv',index=False)
    scraping.to_csv(root / 'Output data/CSV/scraping.csv',index=False)
    light.to_csv(root / 'Output data/CSV/light.csv',index=False)
    temperature.to_csv(root / 'Output data/CSV/temperature.csv',index=False)
    humidity.to_csv(root / 'Output data/CSV/humidity.csv',index=False)


def export_excel(sensor,sensor_new,api,scraping,light,temperature,humidity):
    sensor.to_excel(root / 'Output data/Excel/sensor.xlsx',index=False)
    sensor_new.to_excel(root / 'Output data/Excel/sensor_lim.xlsx',index=False)
    api.to_excel(root / 'Output data/Excel/api.xlsx',index=False)
    scraping.to_excel(root / 'Output data/Excel/scraping.xlsx',index=False)
    light.to_excel(root / 'Output data/Excel/light.xlsx',index=False)
    temperature.to_excel(root / 'Output data/Excel/temperature.xlsx',index=False)
    humidity.to_excel(root / 'Output data/Excel/humidity.xlsx',index=False)


def df_to_sheets(spreadsheet_id,sheet_id,df):
    rangeAll = '{0}!A1:Z'.format('Sheet1')
    body = {}
    sheet = service.spreadsheets()
    resultClear = sheet.values().clear(spreadsheetId=spreadsheet_id,range=rangeAll,body=body).execute()
    d2g.upload(df, spreadsheet_id, credentials=creds, row_names=True)
    sh = client.open_by_key(spreadsheet_id)
    request = {
        "requests": [
            {
                "deleteDimension": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1
                    }
                }
            }
        ]
    }
    result = sh.batch_update(request)


def main():
    # id is formatted as [spreadsheet_id,sheet_id]
    sensor_id = ['10kzvn3N_r0JCOg5YOiq3-g8YGNCsyFhxTMzaTgjumqo','293125075']
    sensor_lim_id = ['1e8ppR7ydPUEt4yeAODlisB4vkK5eqRNw4vEy2WH14T8','5009018']
    light_id = ['11y8zF8dhQA01','1627881621']
    humidity_id = ['112RK_2LYe','1333840194']
    temperature_id = ['15yfjXf8N9sY3pg2q7cC','1580061427']
    api_id = ['1biW_5JQxfRlV191VVvAigGe','467514419']
    scraping_id = ['1cL2Xb43sGiwG_qxdD_XH','1024484030']

    api_raw = get_api()
    sensor_raw = get_sensor()
    scraping_raw = get_scraping()
    sleep(2)
    api = clean_api(api_raw)
    sensor = clean_sensor(sensor_raw)
    scraping = clean_scraping(scraping_raw)
    sensor_new = sensor_bis(sensor,api)
    humidity, temperature, light = sensor_val(api,sensor_new)

    export_csv(sensor,sensor_new,api,scraping,light,temperature,humidity)
    # export_excel(sensor,sensor_new,api,scraping,light,temperature,humidity)

    ids = [sensor_id, sensor_lim_id, light_id, humidity_id, temperature_id, api_id, scraping_id]
    dfs = [sensor,sensor_new,light,humidity,temperature,api,scraping]

    # for i in range(len(ids)):
    #     df_to_sheets(ids[i][0],ids[i][1],dfs[i])

if __name__ == "__main__":
    main()