# mysql_sniffer
mysql_sniffer 是一个基于 MySQL 协议的抓包工具，实时抓取 MySQL 服务端的请求，并格式化输出，输出内容包括访问时间、来源 IP、执行的SQL语句。

mysql_sniffer 抓取 MySQL 5.7 或者 MariaDB 的SQL语句并存到mysql_packet.sql文件里，然后DBA在测试环境 MySQL 8.0 中运行，看SQL语法是否报错，以便检测升级到MySQL 8.0的SQL语法兼容性。

例有一些已知SQL语法与MySQL 8.0不兼容，例如：
```
grant ALL on *.* to admin@'%' identified by 'hechunyang';
select NVL(id/0,'YES') from test.t1 where id = 1;
select user_id,sum(amount) from test.user group by user_id DESC limit 10;
```
