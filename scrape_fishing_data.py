import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
import datetime
import re
from googlesearch import search
today = (pd.Timestamp(datetime.date.today()))

# get_tides: loads html file of specific tide table for Pearlington, MS into a Pandas dataframe.  Cleans dataframe and
# selects the data for the next week.
# return: a list of dataframes detailing sunrise, high tide, and low tide for the next week.


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


# get_weather: loads html file of url for weather data for Pearlington MS into a Pandas Dataframe. Cleans the data and
# selects a week's worth of weather.
# return: Pandas dataframe with a week of weather data.
def get_weather():
    response = requests.get('https://weather.com/weather/tenday/l/f795e22a7d7da0717643ec585d76482217d135add9e3c78'
                            '2015376e5cd987cd4')
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


# weather_conditions: takes the get_weather dataframe as an argument and prints each day and weather conditions
# contained within the dataframe.
def weather_conditions(week_df):
    for ind in week_df.index:
        print('for the day of ' + str(week_df['Day'][ind]) + ', the conditions are: ' + str(week_df['Description'][ind])
              + ', the chance of rain is: ' + str(week_df['Precip'][ind]))


# get_moon_phase: loads a url as a BeautifulSoup object.  Parses that url as a string through a regex to extract moon
# phase data and the corresponding dates.  Converts the dates to a standard datetime format using dateparser.
# return: a Pandas dataframe containing the moon phase data.

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
    moon_df["Day"] = new_date_list
    print(moon_df)
    return moon_df


# phase_add: takes get_weather dataframe and get_moon_phase dataframe as arguments.  Iterates through them and checks if
# any dates are within 3 days of a moon phase.  If so, that moon phase is appended to a list.  If no moon phases match a
# given date, append "No phase data" to the list.  NOTE: iteration is still not working as intended.  The conditional
# statements do not seem to catch the days that come before a given moon phase, and don't reliably flag the right moon
# phase.  Also occasionally they append more than 7 items to the list of phases, so sometimes the flag variable doesn't
# prevent multiple phase statuses from being appended for the same date. Work in Progress.
def phase_add(moon_df, week_df):
    phases = []
    margin = datetime.timedelta(days=3)
    for ind in moon_df.index:
        flag = True
        phase_day = moon_df['Day'][ind]
        phase_status = moon_df['Phase'][ind]
        for i in week_df.index:
            upper_limit = phase_day + margin
            lower_limit = phase_day - margin
            if lower_limit <= week_df['Day'][i] <= upper_limit:
                phases.append(phase_status)
                flag = False
            else:
                pass
        if flag:
            phases.append('No phase data')

# phases.append('No phase data')
    print(phases)

# get_tides()
# weather_conditions(get_weather())
# get_weather()
# get_moon_phase()


phase_add(get_moon_phase(), get_weather())



