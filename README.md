mysql_sniffer 是一个基于 MySQL 协议的抓包工具，用来实时抓取 MySQL 服务端的请求，并格式化输出，输出内容包括访问时间、来源 IP、执行的SQL语句。

在进行MySQL 8.0升级时，了解新版本对SQL语法的改变和新增的功能是非常重要的。通过使用mysql_sniffer，DBA可以在升级之前对现有的SQL语句进行抓取和分析，以确保在新版本中能够正常运行。


例有一些已知SQL语法与MySQL 8.0不兼容，例如：
```
grant ALL on *.* to admin@'%' identified by 'hechunyang';
select NVL(id/0,'YES') from test.t1 where id = 1;
select user_id,sum(amount) from test.user group by user_id DESC limit 10;
```
