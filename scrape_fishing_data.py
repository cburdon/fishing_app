import pandas as pd
import requests
from bs4 import BeautifulSoup
import dateparser
import datetime
from googlesearch import search


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
    today = (pd.Timestamp(datetime.date.today()))
    margin = datetime.timedelta(weeks=1)
    cutoff = today + margin
    week_df = new_df[new_df[0] < cutoff]
    week_df.columns = ['Day', 'Time', 'Tide_up', 'Tide_dn', 'Status']
    high_tide_df = week_df[week_df["Status"] == 'High Tide']
    low_tide_df = week_df[week_df['Status'] == 'Low Tide']
    sunrise_df = week_df[week_df['Status'] == "Sunrise"]

    print(sunrise_df)
    print(low_tide_df)
    print(high_tide_df)


def get_weather():
    response = requests.get('https://weather.com/weather/tenday/l/Pearlington+MS+USMS0285:1:US')
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find_all('table', {'class': 'twc-table'})
    df = pd.read_html(str(table))[0]
    new_df = df.drop(['Day'], axis=1)
    new_df.columns = ['Day', 'Description', 'High/Low', 'Precip', 'Wind', 'Humidity']
    date_list = new_df['Day']
    new_date_list = []
    for date in date_list:
        new_date = dateparser.parse(date)
        new_date_list.append(new_date)
    today = (pd.Timestamp(datetime.date.today()))
    new_date_list[0] = today
    new_df['Day'] = new_date_list
    margin = datetime.timedelta(weeks=1)
    cutoff = today + margin
    week_df = new_df[new_df['Day'] < cutoff]
    print(week_df)


def get_moon_phase():
    # this is the function that isn't working properly.  It finds the url of the current month and year then
    # parses the table of moon phases, but all I can get is the table header when I need the table data instead.
    # Ideally I want to have it in a dataframe like the stuff in get_tides and get_weather, and then from there I want
    # to add it to a database.  Haven't gotten to that yet.
    month_list = ['january', 'february', 'march', 'april', 'may', 'june', 'july',
                  'august', 'september', 'october', 'november', 'december']

    month_number = datetime.date.today().month
    year_number = datetime.date.today().year
    for j in range(1, 13):
        if month_number == j:
            month = month_list[j - 1]
        pass
    url = f'https://www.moongiant.com/moonphases/{month}/{year_number}/'

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find('table')  # this will only find the table header, and the below code doesn't work as it should.
    table_rows = table.find_all('tr')
    for tr in table_rows:
        td = tr.find_all('td')
        print(td)  # this is empty for some reason. I've commented out some of the code to try and break down where it fails.
        # row = [i.text for i in td]
        # print(row)

    # df = pd.read_html(url, header=0)
    # print(df)


# get_tides()
# get_weather()
#
#
get_moon_phase()




