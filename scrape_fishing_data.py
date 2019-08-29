import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
import datetime
import re
today = dateparser.parse(str(datetime.date.today()))

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
# selects a week's worth of weather. UPDATE: Some of the dates are being parsed with no space between the day and month.
# This causes the dateparser not to recognize them as dates and skip them.  Fixed using regex and removing the day
# entirely, as dateparser doesn't need it to spit out a standardised datetime. Also removed % from precipitation list to
# make numerical comparison easier in score_weather function.
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
    print(date_list)
    new_date_list = []
    fixed_date_list = []
    for date in date_list:
        matches = re.findall(r'[A-Z]{3}[ ]\d+', date)
        fixed_date = matches[0]
        fixed_date_list.append(fixed_date)

    for date in fixed_date_list:
        new_date = dateparser.parse(date)
        new_date_list.append(new_date)
    new_df['Day'] = new_date_list
    margin = datetime.timedelta(weeks=1)
    cutoff = today + margin
    week_df = new_df[new_df['Day'] <= cutoff]
    precip_list = []
    for i in week_df.index:
        precip_list.append(week_df['Precip'][i].split('%')[0])
    new_week_df = week_df.drop(['Precip'], axis=1)
    new_week_df['Precip'] = precip_list
    print(new_week_df)
    return new_week_df


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


# phase_add_v2: takes get_weather dataframe, get_moon_phase dataframe, and an int for days margin as arguments.
# Iterates through them and checks if any dates are within 3 days of a moon phase.  If so, that moon phase is appended
# to a list.  If no moon phases match a given date, append "No phase data" to the list.
# return: a new dataframe with Phase Status added as a column


def phase_add_v2(moon_df: pd.DataFrame, week_df: pd.DataFrame, days_margin=3):
    rtn = {}
    margin = datetime.timedelta(days=days_margin)
    phases = {}
    for idx in moon_df.index:
        phases[moon_df['Phase'][idx]] = moon_df['Day'][idx]
    for idx in week_df.index:
        day = week_df['Day'][idx]
        # print(idx, day)
        for phase in phases:
            if day - margin <= phases[phase] <= day + margin:
                rtn[day] = phase
                break
            else:
                try:
                    ph = rtn.pop(day)
                    rtn[day] = ph
                except KeyError:
                    rtn[day] = 'No phase'
    phase_column = []
    for p in rtn:
        phase_column.append(rtn[p])
    new_moon_df = week_df
    new_moon_df['Phase Status'] = phase_column
    print(new_moon_df)
    return new_moon_df


# score_weather: takes 2 dataframes as arguments. Checks if weather condition values are preferrable for each row of the
# first dataframe and changes a score value accordingly. Adds a score column to the first dataframe.  NOTE: Work in
# progress.  Second dataframe is proving difficult since it is a list of dataframes and not all days have high tide and
# some have multiple values.  It will not be as easy as checking the other values was.


def score_weather(new_moon_df, tide_df_list):
    scores = []
    for i in new_moon_df['Day'].index:
        scores.append(0)
    for i in new_moon_df.index:

        if int(new_moon_df["Precip"][i]) <= 50:
            scores[i] = scores[i] + 5
        if int(new_moon_df["Precip"][i]) <= 30:
            scores[i] = scores[i] + 2
        if new_moon_df['Phase Status'][i] == 'First Quarter':
            scores[i] = scores[i] + 5
        if new_moon_df['Phase Status'][i] == 'Third Quarter':
            scores[i] = scores[i] + 5
        if new_moon_df['Phase Status'][i] == 'New Moon':
            scores[i] = scores[i] + 10
        if int(new_moon_df['Wind'][i].split(' ')[1]) <= 15:
            scores[i] = scores[i] + 2
        else:
            pass
    new_moon_df['Score'] = scores
    high_score = new_moon_df.loc[new_moon_df['Score'].idxmax()]
    print(new_moon_df)
    print(high_score)


# get_weather()
# phase_add(get_moon_phase(), get_weather())
# phase_add_v2(moon_df=get_moon_phase(), week_df=get_weather())
# phase_add_v2(get_moon_phase(), get_weather())
score_weather(phase_add_v2(get_moon_phase(), get_weather()), get_tides())

