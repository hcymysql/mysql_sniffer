mysql_sniffer 是一个基于 MySQL 协议的抓包工具，用来实时抓取 MySQL 服务端的请求，并格式化输出，输出内容包括访问时间、来源 IP、执行的SQL语句。

在进行MySQL 8.0升级时，了解新版本对SQL语法的改变和新增的功能是非常重要的。通过使用mysql_sniffer，DBA可以在升级之前对现有的SQL语句进行抓取和分析，以确保在新版本中能够正常运行。

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

#### 那么，如何判断业务上的未知SQL是否与MySQL 8.0兼容呢？

#### mysql_sniffer工具可以帮助你

# 使用方法：
```
usage: mysql_sniffer [-h] -p PORT [-l LOG] [-c] [-v]

MySQL packet sniffer

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  MySQL server port
  -l LOG, --log LOG     Log file path
  -c, --console         Print log to console
  -v, --version         show program's version number and exit
```

```
shell> chmod 755 mysql_sniffer
```

在 MySQL 5.7 或者 MariaDB 机器上执行（SSH的ROOT权限）
```
shell> ./mysql_sniffer -p 3306
```
默认会把线上的SQL语句（select/insert/update/delete）存入mysql_packet.sql文件里。

![image](https://github.com/hcymysql/mysql_sniffer/assets/19261879/7ed20afb-db0e-4e7a-9892-f03ccb34e5aa)

![image](https://github.com/hcymysql/mysql_sniffer/assets/19261879/9a7177ea-3af5-49da-a2f3-c86ad4fb5a89)

#### 抓取1-10分钟数据，然后把mysql_packet.sql文件拷贝到MySQL 8.0测试环境里，然后执行下面的命令：
```
mysql -S /tmp/mysql_mysql8_1.sock test < mysql_packet.sql > /dev/null
```
#### 看报错信息。没有报错，就代表SQL是兼容的。

#### 注：请确保生产环境和测试环境的表结构一致，测试环境不需要任何数据。

--------------------------------------------
# 测试
1） 假定 192.168.1.1 是 MySQL 5.7 / MariaDB，在该机器上运行./mysql_sniffer -p 3306 -c 

2） 在  192.168.1.2 机器上运行sysbench，模拟出生产环境数据读写。

3） mysql_sniffer会实时打印出目前运行的SQL语句。




