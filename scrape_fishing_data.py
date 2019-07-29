import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
import datetime
import re
from googlesearch import search
today = (pd.Timestamp(datetime.date.today()))


def get_tides():
    response = requests.get('https://www.tide-forecast.com/locations/Pearlington-Pearl-River-Mississippi/tides/latest')
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find_all('table', {'class': 'tide-table'})
    df = pd.read_html(str(table))[0]
    new_df = df.drop([2], axis=1)
    date_list = new_df[0]
    new_date_list = []
    for date in date_list:
        new_date = dateparser.parse(date)
        new_date_list.append(new_date)
    new_df[0] = new_date_list
    # today = (pd.Timestamp(datetime.date.today()))
    margin = datetime.timedelta(weeks=1)
    cutoff = today + margin
    week_df = new_df[new_df[0] < cutoff]
    week_df.columns = ['Day', 'Time', 'Tide_up', 'Tide_dn', 'Status']
    high_tide_df = week_df[week_df["Status"] == 'High Tide']
    low_tide_df = week_df[week_df['Status'] == 'Low Tide']
    sunrise_df = week_df[week_df['Status'] == "Sunrise"]
    tide_df_list = [sunrise_df, low_tide_df, high_tide_df]

    print(sunrise_df)
    print(low_tide_df)
    print(high_tide_df)
    return tide_df_list


def get_weather():
    response = requests.get('https://weather.com/weather/tenday/l/Pearlington+MS+USMS0285:1:US')
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find_all('table', {'class': 'twc-table'})
    df = pd.read_html(str(table))[0]
    new_df = df.drop(['Day'], axis=1)
    new_df.columns = ['Day', 'Description', 'High/Low', 'Precip', 'Wind', 'Humidity']
    date_list = new_df['Day']
    #print(date_list)
    new_date_list = []
    for date in date_list:
        new_date = dateparser.parse(date)
        new_date_list.append(new_date)
    # today = (pd.Timestamp(datetime.date.today()))
    new_date_list[0] = today
    #print(new_date_list)
    new_df['Day'] = new_date_list
    margin = datetime.timedelta(weeks=1)
    cutoff = today + margin
    week_df = new_df[new_df['Day'] < cutoff]
    print(week_df)
    return week_df


def weather_conditions(week_df):
    for ind in week_df.index:
        print('for the day of ' + str(week_df['Day'][ind]) + ', the conditions are: ' + str(week_df['Description'][ind])
              + ', the chance of rain is: ' + str(week_df['Precip'][ind]))


def get_moon_phase():
    url = 'https://www.timeanddate.com/moon/phases/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find(id='mn-cyc')
    table_data = table.find_all('td')
    phase_list = []
    date_list = []

    pattern = re.compile(r'(?:Third|First|New|Full)[ ](?:Quarter|Moon)')
    matches = pattern.findall(str(table_data))
    for match in matches:
        phase_list.append(match)

    pattern = re.compile(r'\w+[ ]\d{1,2}')
    matches = pattern.findall(str(table_data))
    for match in matches:
        date_list.append(match)
    new_date_list = []
    for date in date_list:
        new_date = dateparser.parse(date)
        new_date_list.append(new_date)

    moon_df = pd.DataFrame()
    moon_df['Phase'] = phase_list
    moon_df["Date"] = new_date_list
    return moon_df


get_tides()
weather_conditions(get_weather())
# get_weather()
get_moon_phase()




