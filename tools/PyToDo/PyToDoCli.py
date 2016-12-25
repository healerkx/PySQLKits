

import sys, datetime
import MySQLdb
from prettytable import PrettyTable
import PyToDo


def list_entries():
    """
    List today TODO entries in table
    """
    begin_time_str = str(datetime.date.today())
    end_time_str = str(datetime.date.today() + datetime.timedelta(1))
    entries = PyToDo.fetch_entries(begin_time_str, end_time_str)

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
    pass


def send_report():
    pass



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
        add_entry()
    elif command == 'send_report':
        send_report()



