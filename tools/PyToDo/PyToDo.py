# -*- coding:  utf-8 -*-

from bottle import route, run, template, get, post, request, view, static_file
import json
import MySQLdb
import MySQLdb.converters
import MySQLdb.cursors
import json, datetime, urllib, re, os


@route('/templates/<filename:path>')
def server_static(filename):
    templates_path = os.path.join(os.getcwd(), 'templates')
    return static_file(filename, root=templates_path)

def get_connection(db='pytodo'):
    host = 'localhost'
    port = 3306
    user, passwd = 'root', 'root'

    conv = MySQLdb.converters.conversions.copy()
    conv[12] = str  # for MySQL datetime type

    conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port, 
            charset="utf8", 
            cursorclass=MySQLdb.cursors.DictCursor, 
            conv=conv)
    return conn

def query(sql):
    with get_connection() as cursor:
        result = cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return (data, result)

@route('/')
@view('templates/index.tpl')
def index():
    return {}

def fetch_entries(begin_time, end_time):
    sql = "select * from td_entry where status=1 and create_time>'%s' and create_time<'%s'" % (begin_time, end_time)
    data, result = query(sql)
    return data

@get('/entries/<day>')
def get_someday_entries(day):
    begin_time_str = str(datetime.date.today())
    end_time_str = str(datetime.date.today() + datetime.timedelta(1))
    if day == 'today':
        begin_time_str = str(datetime.date.today())
        end_time_str = str(datetime.date.today() + datetime.timedelta(1))
    elif day == 'yesterday':
        begin_time_str = str(datetime.date.today() + datetime.timedelta(-1))
        end_time_str = str(datetime.date.today())
    elif re.match('\d{8}', day):
        begin_time_str = str(datetime.datetime.strptime(day, '%Y%m%d'))
        end_time_str = str(datetime.datetime.strptime(day, '%Y%m%d') + datetime.timedelta(1))

    result = fetch_entries(begin_time_str, end_time_str)
    return json.dumps(result)


@get('/entries/<begin_time>/<end_time>')
def entries_range(begin_time, end_time):
    begin_time_str = str(datetime.datetime.strptime(begin_time, '%Y%m%d'))
    end_time_str = str(datetime.datetime.strptime(end_time, '%Y%m%d'))

    result = fetch_entries(begin_time_str, end_time_str)

    return json.dumps(data)

def add_entry(content, time):
    sql = "insert into td_entry values (null, '%s', 1, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, '%s', '%s');" % (content, time, time)
    data, result = query(sql)
    return result

@post('/entry')
def entry():
    create_time = str(datetime.datetime.now())
    # Why???
    d = urllib.parse.parse_qs(request.body.read().decode())
    # Why???
    content = d['content'][0].replace("'", "\\'")

    result = add_entry(content, create_time)
    return json.dumps({"result": result})

@get('/begin/entry/<entry_id:int>')
def begin_entry(entry_id):
    sql = "update td_entry set begin_time=CURRENT_TIMESTAMP, entry_status=1 where entry_id=%d" % entry_id
    data, result = query(sql)
    return json.dumps({"result": result})

@get('/end/entry/<entry_id:int>')
def end_entry(entry_id):
    sql = "update td_entry set end_time=CURRENT_TIMESTAMP, entry_status=2 where entry_id=%d" % entry_id
    data, result = query(sql)
    return json.dumps({"result": result})

if  __name__ == '__main__':
    run(host='localhost', port=7788, reloader=True, debug=True)

