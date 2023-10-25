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

那么，如何判断业务上的未知SQL是否与MySQL 8.0兼容呢？

mysql_sniffer工具可以帮助你

# 使用方法：
```
shell> chmod 755 mysql_sniffer
shell> ./mysql_sniffer -p 3306
```

1）在生产环境下运行mysql_sniffer，抓取1-10分钟数据，然后把mysql_packet.sql文件拷贝到测试环境里，然后你执行。
```
mysql -S /tmp/mysql_mysql8_1.sock test < mysql_packet.log > /dev/null
```
看报错信息。没有报错，就代表SQL是兼容的。


