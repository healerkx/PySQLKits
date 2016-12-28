#!/usr/bin/env python3

import sys, datetime
import MySQLdb
import requests, urllib, json
from prettytable import PrettyTable
import PyToDo



def fetch_today_entries(): 
    """
    List today TODO entries in table
    """
    begin_time_str = str(datetime.date.today())
    end_time_str = str(datetime.date.today() + datetime.timedelta(1))
    entries = PyToDo.fetch_entries(begin_time_str, end_time_str)
    return entries

def list_entries():
    entries = fetch_today_entries()

    tab = PrettyTable(['ID', 'TODO', 'Begin time', 'End time'])
    # TODO: Add fields names
    for entry in entries:
        entry_status = entry['entry_status']
        begin_time = entry['begin_time'][:-3]
        end_time = entry['end_time'][:-3]
        if entry_status == 0:
            begin_time = ''
            end_time = ''
        elif entry_status == 1:
            end_time = ''


        tab.add_row([entry['entry_id'], entry['entry_content'], begin_time, end_time])
 
    print(tab)


def add_entry(content):
    PyToDo.add_entry(content, str(datetime.datetime.now()))

def send_report_login():
    with open('/Users/healer/.todo/config', 'r') as f:
        lines = f.readlines()
    username, password = '', ''
    for line in lines:
        ps = line.split('=')
        if ps[0] == 'username':
            username = ps[1].strip()
        elif ps[0] == 'password':
            password = ps[1].strip()
    # print(username, password)
    url = 'http://xwork.intra.ffan.com/user/check_login.json'
    data = {'userName': username, 'passWord': password}
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
    resp = requests.post(url, data=data, headers=headers, 
                         verify=False, allow_redirects=False)
    cookie = resp.headers['set-cookie']
    content = str(resp.content, 'utf-8')
    print(content)
    result = json.loads(content)
    if str(result['status']) == '0':
        return (True, cookie)
    return (False, None)

report_template="""
date[]:2016-12-26 Monday
proj_level1[]:技术需求（BO）
proj_level2[]:无编号_BO（主站）
hour[]:8
content[]:
desc[]:
proj_from[]:
id[]:
dept1:应用研发中心
dept2:P端营销研发部
"""
def get_report_post(report):
    lines = report_template.split('\n')
    post = {}
    for line in lines:
        if ':' not in line:
            continue
        parts = line.split(':')
        post[parts[0]] = parts[1]

    post['content[]'] = report

    date = datetime.date.today()
    weekday = ['', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][date.isoweekday()]
    post['date[]'] = '%s %s' % (date, weekday)
    return post

def send_report():
    entries = fetch_today_entries()
    idx = 1
    contents = []
    for entry in entries:
        contents.append('%d. %s' % (idx, entry['entry_content']))

    report = '\n'.join(contents)
    result, cookie = send_report_login()
    if not result:
        print("Login failed")

    url = 'http://xwork.intra.ffan.com/work/saveAjax.json'
    data = get_report_post(report)
    headers = { "cookie": cookie }

    # print(data)
    response = requests.post(url, data=data, headers=headers, verify=False, allow_redirects=False)
    print(response.content.decode('utf-8'))

def main():
    pass

def usage():
    return """
Python TODO list cli 0.1
Command list:
      add
      list
      report
    """

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(usage())
        exit()

    command = sys.argv[1]
    if command == 'list':
        list_entries()
    elif command == 'add':
        content = sys.argv[2]
        add_entry(content)
    elif command == 'report':
        send_report()
    elif command == 'test':
        print(datetime.date.today().isoweekday())



