# mysql/percona 备份 - xtrabackup

环境：
- Centos 7
- Xtrabackup 2.4
- Percona Server for MySQL 5.6

---
安装xtrabackup时我发现mysql、mariadb的rpm包和percona-cluster都有冲突。只好把mysql和mariadb全部卸载，再装percona-server。

percona和mariadb都是mysql的分支，percona-server使用上也是和mysql没有太多区别。

mysql存储引擎有两种——myisam和innodb。percona和自10.0.9起的mariadb的数据引擎都是对innodb进行了改进的XtraDB。

根据其官网的介绍和实际体验，percona和mysql还是有些许区别，mariadb基本可以完全兼容mysql。

## 安装xtrabackup

首先安装percona源

```
yum install http://www.percona.com/downloads/percona-release/redhat/0.1-3/percona-release-0.1-3.noarch.rpm
```

查看percona包：
```
yum list | grep percona
```

输出:
```
...
percona-release.noarch                   0.1-4                          installed
percona-xtrabackup-24.x86_64             2.4.5-1.el7                    @percona-release-x86_64
Percona-Server-client-55.x86_64          5.5.53-rel38.5.el7             percona-release-x86_64
Percona-Server-client-56.x86_64          5.6.34-rel79.1.el7             percona-release-x86_64
Percona-Server-client-57.x86_64          5.7.16-10.1.el7                percona-release-x86_64
Percona-Server-server-55.x86_64          5.5.53-rel38.5.el7             percona-release-x86_64
Percona-Server-server-56.x86_64          5.6.34-rel79.1.el7             percona-release-x86_64
Percona-Server-server-57.x86_64          5.7.16-10.1.el7                percona-release-x86_64
percona-xtrabackup.x86_64                2.3.6-1.el7                    percona-release-x86_64
percona-xtrabackup-22.x86_64             2.2.13-1.el7                   percona-release-x86_64
...
```

选择一个版本进行安装，例如
```
yum install -y percona-xtrabackup-24.x86_64
```

## 安装percona-server

从上面的list里面继续选一个percona-server版本进行安装，例如
```
yum install -y Percona-Server-server-56.x86_64
```

安装过程中会把percona-client一并安装。

启动数据库：```systemctl start mysql```

数据文件和配置文件默认依然分别位于/var/lib/mysql和/etc/my.conf


## 创建一个有足够权限的数据库用户

这一步可以忽略，使用已有的用户进行备份也没问题。

创建用户
```
mysql> create user zdt;
Query OK, 0 rows affected (0.00 sec)
```

用zdt用户登mysql，innobackupex需要用户拥有一定权限进行一些操作，试一试这条命令会不会报错：
```
mysql -u zdt

mysql> show engine innodb status;
ERROR 1227 (42000): Access denied; you need (at least one of) the PROCESS privilege(s) for this operation
```

报错的话就要给zdt用户赋予相应权限，使用root用户：

```
mysql -u root -p

GRANT RELOAD, LOCK TABLES, REPLICATION CLIENT, CREATE TABLESPACE, PROCESS, SUPER, INSERT, CREATE, SELECT ON *.* TO 'zdt'@'localhost';
GRANT RELOAD, LOCK TABLES, REPLICATION CLIENT, CREATE TABLESPACE, PROCESS, SUPER, INSERT, CREATE, SELECT ON *.* TO 'zdt'@'%';
```

*有一种说法是只赋予用户"RELOAD, LOCK TABLES, REPLICATION CLIENT"这三个权限，实验中发现只有这三个权限会报错，只给这三个权限是人家官网的一个例子，for example而已，一些文档写的真是呵呵。percona官方的解释可以[参考这里](https://www.percona.com/doc/percona-xtrabackup/2.4/using_xtrabackup/privileges.html#permissions-and-privileges-needed)。此外这篇文章里面并不会用到所有这些权限，不过还是把权限全给上了，今后慢慢补充权限的影响吧。*

再执行show engine innodb status就有结果了。

有关权限请进一步阅读:http://dev.mysql.com/doc/refman/5.7/en/privileges-provided.html


---
reference：
- https://www.percona.com/doc/percona-server/5.5/installation/yum_repo.html
- http://dev.mysql.com/doc/refman/5.7/en/privileges-provided.html
- http://kanyakonil.com/2015/08/26/resolving-access-denied-you-need-at-least-one-of-the-process-privileges-for-this-operation/
- https://www.percona.com/doc/percona-xtrabackup/2.4/using_xtrabackup/privileges.html
