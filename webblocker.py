# coding: utf-8

import time
from datetime import datetime as dt

def get_hosts_file():
    #hosts_file = r'C:\Windows\System32\drivers\etc\hosts'
    hosts_file = r'/etc/hosts'
    return hosts_file

HOSTS_FILE = get_hosts_file()
WEBSITE_LIST = ['www.facebook.com', 'facebook.com', 'gmail.com', 'linkedin.com', 'www.linkedin.com']
REDIRECT_ADDRESS = '127.0.0.1'

PERIODS = [
    {
        'start_time': '9:00',
        'end_time': '12:00',
        'website_list': WEBSITE_LIST,
    },
    {
        'start_time': '11:00',
        'end_time': '18:00',
        'website_list': WEBSITE_LIST,
    },
    {
        'start_time': '19:30',
        'end_time': '23:30',
        'website_list': ['facebook.com', 'www.facebook.com'],
    },
]

def setup_periods(periods):
    for period in periods:
        period['start_time'] = get_time_from_string(period['start_time'])
        period['end_time'] = get_time_from_string(period['end_time'])
        period['state'] = False

def get_time_from_string(string_time):
    '''string_time format hh:mm (e.g., 18:00)'''
    hour, minute = string_time.split(':')
    hour, minute = int(hour), int(minute)
    return dt.now().replace(hour=hour, minute=minute)

def delta_seconds(end_time, start_time):
    wait_for = (end_time - start_time).total_seconds()
    return int(wait_for)

def in_period(moment, period):
    period['start_time'] = period['start_time'].replace(year=moment.year, month=moment.month, day=moment.day, second=0)
    period['end_time'] = period['end_time'].replace(year=moment.year, month=moment.month, day=moment.day, second=59)
    return period['start_time'] < moment < period['end_time']

def remove_websites_from_hosts(file, website_list):
    with open(file, 'r+') as f:
        content = f.readlines()
        f.seek(0)
        for line in content:
            if not any(website in line for website in website_list):
                # print('unblocked!!!!!')
                f.write(line)
        f.truncate()

def add_websites_to_hosts(file, website_list):
    # print('blocking')
    with open(file, 'r+') as f:
        content = f.read()
        for website in website_list:
            if website not in content:
                f.write(REDIRECT_ADDRESS + ' ' + website + '\n')

def main():
    setup_periods(PERIODS)
    while True:
        for period in PERIODS:
            if period['state'] == False and in_period(dt.now(), period):
                period['state'] = True
                add_websites_to_hosts(HOSTS_FILE, period['website_list'])
                wait_for = delta_seconds(period['end_time'], dt.now())
                # print(wait_for)
                time.sleep(wait_for)
                break
            elif period['state']:
                period['state'] = False
                remove_websites_from_hosts(HOSTS_FILE, period['website_list'])
        # print('not blocking')
        time.sleep(60)

if __name__ == '__main__':
    main()
