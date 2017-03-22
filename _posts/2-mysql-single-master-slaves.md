# 创建MySQL一主一从集群

目标：一个主节点和一个副本。（单一的主从复制的应用场景足够应对中小性微信公众号的后台管理需求了，所以即便阿里云的MySQL产品做得很简单，用的人还是相当多。毕竟能用钱解决的事绝不花时间。）

环境Centos7, MySQL Community Server 5.6.35。

**正文：**

| 节点 | IP     |
| :----------- | :------------- |
| master       | 10.250.5.42       |
| slave        | 10.250.5.43       |


参考前一篇文章在两台安装mysql server。实验环境是两台新创建的虚拟机，数据都是空白的，暂时不考虑其他同步问题。

## 配置主节点

修改/etc/my.cnf文件。
```
[mysqld]
log-bin=mysql-bin
server-id=1
```

重启mysql服务后查看master节点状态：

```
mysql> SHOW MASTER STATUS;
+------------------+----------+--------------+------------------+-------------------+
| File             | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+------------------+----------+--------------+------------------+-------------------+
| mysql-bin.000001 |      120 |              |                  |                   |
+------------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```

在主节点上为副本集创建一个用户：

```
mysql> CREATE USER repl;
Query OK, 0 rows affected (0.00 sec)

mysql> GRANT REPLICATION SLAVE ON *.* TO repl IDENTIFIED BY 'pwdpwd';
Query OK, 0 rows affected (0.00 sec)
```

创建用户后：

```
mysql> FLUSH TABLES WITH READ LOCK;

mysql> UNLOCK TABLES;
```

## 配置从节点

vim /etc/my.cnf：
```
[mysqld]
server-id=2
```

设置完副本集的server-id后需要在从节点上用CHANGE MASTER TO命令设置一系列参数，用刚刚在master上创建的用户把slave连接过去：

```
mysql> CHANGE MASTER TO
    -> MASTER_HOST='10.250.5.42',
    -> MASTER_USER='repl',
    -> MASTER_LOG_FILE='mysql-bin.000001',
    -> MASTER_PORT=3306,
    -> MASTER_PASSWORD='pwdpwd';
Query OK, 0 rows affected, 2 warnings (0.07 sec)

mysql> START SLAVE;
Query OK, 0 rows affected (0.01 sec)
```

其中MASTER_LOG_FILE参数是通过在master节点上执行```SHOW MASTER STATUS；```获取的。

完工。

接下来在主节点上执行创建数据库等等操作就可以复制到从节点下了。

参考：
https://dev.mysql.com/doc/refman/5.7/en/replication-howto.html
