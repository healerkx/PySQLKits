# PySQLKits


### It's a toolkit set for MySQL, implementing in Python 3.5


- batchinsert is for generating insert SQL statements, also support data set having relations. 
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

- datachain is a tool for query data from MySQL and Redis with SimpleQuery language (A simple script language I implement using PLY), then render the results in pretty tables, in both terminator and browser.

> usage:
```
python datachain.py simplequery.sq
```

- mysqlbinlog is a SDK to parse MySQL binlog files, yield Row-Events.
> It's supposed to access the path /examples, I give some examples using mysqlbinlog:

> - mysql-redis-sync reads the current binlog changes and flush them into Redis.
> - entry-traceback shows an entry's change history.
> - entry-watcher shows the current changing entries in some tables you concern.

- mysqldiff compare two databases for diff, and generating create table, alter table, drop table SQL lines.
> This script (original version) is from my friend Zhoujing(https://github.com/lexchou), Access, amazing...
```
python3 mysqldiff.py root:root@localhost/mydb root:123456@192.168.1.101:3307/mydb
```

- relations is a tool to reveal tables' relationship, TODO: I want to represent the relation graphically.