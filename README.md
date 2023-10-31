mysql_sniffer 是一个基于 MySQL 协议的抓包工具，用来实时抓取 MySQL 服务端的请求，并格式化输出，输出内容包括访问用户、访问时间、来源 IP、执行的SQL语句。

```
mysql_sniffer is a packet capture tool based on the MySQL protocol,used to capture real-time requests from the MySQL server and format the output.
The output includes user access, access time, source IP, and executed SQL statements.
```

https://www.oschina.net/p/hcymysql_mysql_sniffer

在进行MySQL 8.0升级时，了解新版本对SQL语法的改变和新增的功能是非常重要的。通过使用mysql_sniffer，DBA可以在升级之前对现有的SQL语句进行抓取和分析，以确保在新版本中能够正常运行。

使用mysql_sniffer工具可以带来以下几点好处：

1) 对SQL语法的改变有更深入的了解：MySQL 8.0引入了一些新的SQL语法，也对一些旧的语法进行了修改或弃用。通过mysql_sniffer，DBA可以抓取并分析现有的SQL语句，以确定它们是否会受到这些改变的影响。

2) 发现并解决潜在的问题：如果在新版本中，某些SQL语句无法正常运行，那么通过mysql_sniffer，DBA可以提前发现这些问题，并在升级之前进行修复。

```
When upgrading to MySQL 8.0, it is crucial to understand the changes and additions to SQL syntax in the new version.
By using mysql_sniffer, DBAs can capture and analyze existing SQL statements before upgrading to ensure they will function properly in the new version.

The benefits of using mysql_sniffer include:

Deeper understanding of changes to SQL syntax: MySQL 8.0 introduces new SQL syntax and modifies or deprecates some old syntax.
With mysql_sniffer, DBAs can capture and analyze existing SQL statements to determine if they will be affected by these changes.

Identification and resolution of potential issues: If certain SQL statements cannot function properly in the new version,
DBAs can identify and resolve these issues earlier by using mysql_sniffer before upgrading.
```

-------------------------------------------------
有一些已知SQL语法与MySQL 8.0不兼容，例如：
```
select NVL(id/0,'YES') from test.t1 where id = 1;
select user_id,sum(amount) from test.user group by user_id DESC limit 10;
```

第一条语句，NVL函数是MariaDB特有的，在MySQL 8.0中，要改成：
```
select IFNULL(id/0,'YES') from test.t1 where id = 1;
```

第二条语句，在MySQL 8.0中group by 字段 ASC/DESC 失效，要改成：
```
select user_id,sum(amount) from test.user group by user_id order by user_id DESC limit 10;
```

### 那么，如何判断业务上的未知SQL是否与MySQL 8.0兼容呢？

### mysql_sniffer工具可以帮助你

# 介绍
```
usage: mysql_sniffer [-h] -p PORT [-t TABLES [TABLES ...]] [-l LOG] [-c] [-r RUNTIME] [-v]

MySQL packet sniffer

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  MySQL server port
  -t TABLES [TABLES ...], --tables TABLES [TABLES ...]
                        Table names to capture
  -l LOG, --log LOG     Log file path
  -c, --console         Print log to console
  -r RUNTIME, --runtime RUNTIME
                        Runtime of packet sniffing in seconds
  -v, --version         show program's version number and exit
```

# 参数解释
```
-p 指定端口，MySQL默认3306
-c 是把抓取到的SQL打印到终端
-t 指定具体的表名，例如只抓取t1，t2，t3这三张表， -t t1 t2 t3 （不支持正则表达式，请写具体的表名）
-l 抓取的SQL保存在哪个文件里，不指定默认保存在mysql_packet.sql文件里
-r 抓取多长时间，单位秒
```

# 演示视频
https://www.douyin.com/video/7295397864006536502

# 使用
```
shell> chmod 755 mysql_sniffer
```

在 MySQL 5.7 或者 MariaDB 机器上执行（SSH的ROOT权限）
```
shell> ./mysql_sniffer -p 3306 -r 60
```
将会抓取60秒数据（-r 代表抓取的时间，单位秒），默认会把线上的SQL语句（select/insert/update/delete/call）存入mysql_packet.sql文件里。

![image](https://github.com/hcymysql/mysql_sniffer/assets/19261879/7ed20afb-db0e-4e7a-9892-f03ccb34e5aa)

![image](https://github.com/hcymysql/mysql_sniffer/assets/19261879/9a7177ea-3af5-49da-a2f3-c86ad4fb5a89)

#### 抓取1-10分钟数据，然后把mysql_packet.sql文件拷贝到MySQL 8.0测试环境里，然后执行下面的命令：
```
mysql -S /tmp/mysql_mysql8_1.sock yourDB -f < mysql_packet.sql > /dev/null
```
#### 看报错信息，是否含有（You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax）。
#### 没有语法错误，就代表SQL是兼容的。

#### 注：请确保生产环境和测试环境的表结构一致，测试环境不需要任何数据。

--------------------------------------------
# 测试
1） 假定 192.168.1.1 是 MySQL 5.7 / MariaDB，在该机器上运行./mysql_sniffer -p 3306 -c 

2） 在  192.168.1.2 机器上运行sysbench，模拟出生产环境数据读写。
```
shell> sysbench --test=/usr/share/sysbench/tests/include/oltp_legacy/oltp.lua --oltp_tables_count=1
--mysql-table-engine=innodb --oltp-table-size=100000 --max-requests=0 --max-time=120 --num-threads=12
--mysql-host=192.168.198.239 --mysql-port=3306  --mysql-user=admin
--mysql-password=hechunyang  --mysql-db=test  --db-driver=mysql  run
```

3） mysql_sniffer会实时打印出目前运行的SQL语句。

--------------------------------------------
注：工具适用于 Centos6 和 Centos7 系统。

mysql_sniffer（Centos7）

mysql_sniffer_centos6（Centos6）



