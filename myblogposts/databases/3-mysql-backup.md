# mysql备份

阿里云MySQL服务对备份的介绍：

>自动备份支持全量物理备份
>手动备份支持全量物理备份、全量逻辑备份和单库逻辑备份
>MySQL 5.7 备份文件最多保留 7 天，且不支持逻辑备份
>Binlog （500MB/个）产生完后立即压缩上传，24 小时内删除本地文件
>Binlog 文件会占用实例的磁盘容量，用户可以通过 一键上传 Binlog 将 Binlog 文件上传至 OSS，不影响实例的数据恢复功能，Binlog 也不再占用实例磁盘空间

我们尝试实现阿里云提供的功能.

即使我们的服务器不会遇到“被导弹摧毁”这种小概率事件，我们的数据库还是需要进行备份。备份的目的是为恢复数据库进行准备，没有备份当然无法进行恢复。除了进行备份,log信息对于恢复数据也必不可少.

文章讨论范围限于单节点环境.

*通过bin-log恢复被删除的数据*

模拟一次日至恢复的过程.

具体内容:
>1. mysqldump导出数据
>2. 在导出后继续修改数据
>3. "误删"表
>4. 在(1)时导出的数据导入
>5. 用重放bin-log记录下来的(2)操作


## 准备工作

1. 开启bin-log:

修改my.cnf,添加:

```
server-id=1
log-bin=mysql-bin
```

my.cnf配置文集中有一项datadir,这个目录下存着log,数据库文件等等.

重启mysql,开启bin-log记录日志.

2. 创建一个数据库testdb中的testlog表,并向其中写入一些数据.

例如:
```
mysql> create database testdb;
Query OK, 1 row affected (0.04 sec)

mysql> use testdb;
Database changed
mysql> create table testlog (id int,content text);
Query OK, 0 rows affected (0.12 sec)

mysql> insert into testlog values (1,"testing bin log recovery");
Query OK, 1 row affected (0.02 sec)
```


## 使用mysqldump工具导出数据

可以利用show master status查看当前使用的log文件.
```
mysql> show master status;
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000007 |     3752 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```

退出mysql shell,在命令行执行以下命令,把testdb数据库的testlog表导入/tmp/testdb.sql文件:
```
[root@backup mysql]# mysqldump -uroot testdb testlog -l -F >/tmp/test-log.sql
```

执行过mysqldump后当前的bin-log文件会更新,使用show master status查看:
```
mysql> show master status;
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000008 |     120  |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```

## 导出后继续进行一些ddl操作

读取testlog表内的数据:

```
mysql> select * from testlog;
+------+--------------------------+
| id   | content                  |
+------+--------------------------+
|    1 | testing bin log recovery |
|    2 | test2                    |
|    3 | test2                    |
|    3 | test4                    |
+------+--------------------------+
4 rows in set (0.00 sec)

```

## "误删"表

在mysql shell中执行:
```
mysql> drop table testlog;
Query OK, 0 rows affected (0.06 sec)

mysql> show tables;
Empty set (0.00 sec)
```

testdb中只创建了一个表,此时应为空.

## 用之前导出的数据恢复testlog表

命令行执行
```
[root@backup tmp]# mysql -u root testdb < testdb-log.sql
```

导入后的效果:
```
mysql> use testdb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+------------------+
| Tables_in_testdb |
+------------------+
| testlog          |
+------------------+
1 row in set (0.00 sec)

mysql> select * from testlog;
+------+--------------------------+
| id   | content                  |
+------+--------------------------+
|    1 | testing bin log recovery |
+------+--------------------------+
1 row in set (0.00 sec)
```

## 用重放bin-log记录下来的操作

这个步骤需要用到bin-log文件.

首先进入my.cnf中配置的datadir目录下,默认配置/var/lib/mysql,进入目录后使用mysqlbinlog工具查看二进制log文件:

```
[root@backup mysql]# mysqlbinlog mysql-bin.000008 | more
```
找到drop之前的节点,at ***的那个数字.

使用这个节点和该log文件进行操作重放.

```
[root@backup mysql]# mysqlbinlog mysql-bin.000008 --stop-position="810" mysql-bin.000008 | mysql -uroot
```

## 结果
```
mysql> select * from testlog;
+------+--------------------------+
| id   | content                  |
+------+--------------------------+
|    1 | testing bin log recovery |
|    2 | test2                    |
|    3 | test2                    |
|    3 | test4                    |
+------+--------------------------+
4 rows in set (0.00 sec)

```

---
参考：

https://aws.amazon.com/rds/mysql/details/

https://help.aliyun.com/document_detail/26206.html?spm=5176.doc26125.6.665.19vrCb
https://help.aliyun.com/document_detail/26207.html?spm=5176.doc26125.6.666.19vrCb
https://help.aliyun.com/document_detail/26208.html?spm=5176.doc26125.6.667.19vrCb

http://blog.csdn.net/laokaizzz/article/details/52071526
