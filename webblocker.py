#!/usr/bin/env python
# coding: utf-8

from datetime import datetime
import json
import os
import platform
import time


REDIRECT_ADDRESS = '127.0.0.1'


def get_hosts_file():
    if platform.system() == 'Linux':
        hosts_file = os.path.normpath('/etc/hosts')
    elif platform.system() == 'Windows':
        hosts_file = os.path.normpath(r'C:\Windows\System32\drivers\etc\hosts')
    return hosts_file


HOSTS_FILE = get_hosts_file()


def parse_rules_file(fname='rules.json'):
    with open(fname, 'r') as f:
        content = f.read()
    rules = json.loads(content)
    lists = rules.get('lists', [])
    periods = rules.get('periods', [])
    for period in periods:
        period['website_list'] = lists.get(period.get('website_list', ''), [])
    return periods


def setup_periods(periods):
    for period in periods:
        period['start_time'] = get_time_from_string(period['start_time'])
        period['end_time'] = get_time_from_string(period['end_time'])
        period['state'] = False


def get_time_from_string(string_time):
    '''string_time format hh:mm (e.g., 18:00)'''
    hour, minute = string_time.split(':')
    hour, minute = int(hour), int(minute)
    return datetime.now().replace(hour=hour, minute=minute)


def delta_seconds(end_time, start_time):
    wait_for = (end_time - start_time).total_seconds()
    return int(wait_for)


def in_period(moment, period):
    period['start_time'] = period['start_time'].replace(
        year=moment.year, month=moment.month, day=moment.day, second=0)
    period['end_time'] = period['end_time'].replace(
        year=moment.year, month=moment.month, day=moment.day, second=59)
    return period['start_time'] < moment < period['end_time']


def remove_websites_from_hosts(file, website_list):
    with open(file, 'r+') as f:
        content = f.readlines()
        f.seek(0)
        for line in content:
            if not any(website in line for website in website_list):
                f.write(line)
        f.truncate()


def add_websites_to_hosts(file, website_list):
    with open(file, 'r+') as f:
        content = f.read()
        for website in website_list:
            if website not in content:
                f.write(REDIRECT_ADDRESS + ' ' + website + '\n')


def process_rules(rules):
    try:
        return proccess_periods(rules)
    except KeyboardInterrupt:
        return proccess_user_abort(rules)


def proccess_periods(rules):
    for period in rules:
        if period['state'] is False and in_period(datetime.now(), period):
            period['state'] = True
            add_websites_to_hosts(HOSTS_FILE, period['website_list'])
            wait_for = delta_seconds(period['end_time'], datetime.now())
            time.sleep(wait_for)
            break
        elif period['state']:
            period['state'] = False
            remove_websites_from_hosts(HOSTS_FILE, period['website_list'])
    return 0


def proccess_user_abort(rules):
    for period in rules:
        if period['state']:
            period['state'] = False
            remove_websites_from_hosts(HOSTS_FILE, period['website_list'])
    return 1


def main():
    rules = parse_rules_file()
    setup_periods(rules)
    while True:
        if process_rules(rules):
            break
        time.sleep(60)


if __name__ == '__main__':
    main()
