# PySQLKits

### It's a toolkits set for MySQL, implementing in Python 3.5

- batchinsert is for generating multi-lines of insert SQL, 
> usage:

```
i = Insert('kx_user', 
    user_id=None,
    company_id=[2, 3, 5], 
    username=ChineseName(unique=True), 
    age=range(20, 90), 
    mobile=ChinaMobile(),
    time=DatetimeRange(begin='2015-12-23', end='2016-12-23'),
    order_id=IntegerRange(begin=100, end=1000, step=2, order='asc'))

i.set_fields_order(['user_id', 'username', 'age', 'mobile', 'company_id', 'time', 'order_id'])
i.perform(20)
```

- datachain is for query from MySQL and Redis with SimpleQuery language (A simple script language I implements with PLY), then render the query results in pretty format.

> usage:
```
python datachain.py simplequery.sq
```
- mysqlbinlog is a tool to parse MySQL binlog files, yield Row-Events.
> It's supposed to access the path /examples, I give two examples using mysqlbinlog, One reads the current binlog changes and flush them into Redis. Another is for display an entry's change history.



- mysqldiff compare two databases for diff, and generating create table, alter table, drop table SQL lines.
> This script (original version) is from my friend Zhoujing(https://github.com/lexchou), Access, amazing...
```
python3 mysqldiff.py root:root@localhost/mydb root:123456@192.168.1.101:3307/mydb
```