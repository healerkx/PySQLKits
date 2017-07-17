#!/usr/bin/env python3

import sys, datetime
import MySQLdb
import requests, urllib, json
from prettytable import PrettyTable
import PyToDo

proj_level2 = ''

def fetch_today_entries(): 
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
    # TODO: content need decode("GBK") when Windows cmd.
    PyToDo.add_entry(content, str(datetime.datetime.now()))

def start_entry(entry_id):
    PyToDo.begin_entry(int(entry_id))

def stop_entry(entry_id):
    PyToDo.end_entry(int(entry_id))

def send_report_login():
    with open('/Users/healer/.todo/config', 'r') as f:
        lines = f.readlines()
    username, password = '', ''
    global proj_level2
    for line in lines:
        ps = line.split('=')
        if ps[0] == 'username':
            username = ps[1].strip()
        elif ps[0] == 'password':
            password = ps[1].strip()
        elif ps[0] == 'proj_level2':
            proj_level2 = ps[1].strip()

    # print(username, password)
    url = 'http://xwork.intra.ffan.com/user/check_login.json'
    data = {'userName': username, 'passWord': password}
    headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Origin': 'http://xwork.intra.ffan.com',
               'Referer': 'http://xwork.intra.ffan.com/user/login',
               'X-Requested-With': 'XMLHttpRequest',
               'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
    session = requests.Session()
    session.trust_env = False               
    resp = session.post(url, data=data, headers=headers, 
                         verify=False, allow_redirects=False)
    
    content = str(resp.content, 'utf-8')
    # print(content)
    cookie = resp.headers['set-cookie']
    
    # print(content)
    result = json.loads(content)
    if str(result['status']) == '0':
        return (True, cookie)
    return (False, None)

report_template="""
proj_level1[]:技术需求
hour[]:8
desc[]:
proj_from[]:
id[]:
dept1:软件平台研发中心
dept2:平台产品研发部
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
    post['proj_level2[]'] = proj_level2
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
        idx += 1

    report = '\n'.join(contents)
    result, cookie = send_report_login()
    if not result:
        print("Login failed")
        exit()

    url = 'http://xwork.intra.ffan.com/work/saveAjax.json'
    data = get_report_post(report)
    headers = { "cookie": cookie }
    session = requests.Session()
    session.trust_env = False
    response = session.post(url, data=data, headers=headers, verify=False, allow_redirects=False)
    print(response.content.decode('utf-8'))

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
    elif command == 'start':
        entry_id = sys.argv[2]
        start_entry(entry_id)
    elif command == 'stop':
        entry_id = sys.argv[2]
        stop_entry(entry_id)
    elif command == 'report':
        send_report()

