# Install mysql-community-server on centos7

**I know this seems simple, but since installation works still is a problem for further tasks, it's necessary to write a blog for this.**

Downloading rpm packages and find a good repo is quite a hard task.

Blogs online are buggy, my propose for writing this one is to reduce bugs when installing and speed up the downloading tasks under low bandwidth env.

*This blog is focusing on centos7.*

## axel - a friend of all low bandwidth users

Insdead of anxiously waiting wget to finish its procedure or the browser to reconnect its lost connection, axel is a preferable cli tool for linux users that helps us download more quickly.
Axel downloads in parallel, use ```-n``` to specify the number of processes to download.

Axel download source is [here](http://dl.fedoraproject.org/pub/epel/7/x86_64/a/axel-2.4-9.el7.x86_64.rpm).

For example:
```
axel -n 10 http://path/to/your/file
```

## yum repo for mysql-5.6-community-*

This repo contains almost everything needed under a centos7 env:
**http://repo.mysql.com/yum/mysql-5.6-community/el/7/i386/**

Either download rpm packages directly from this repo or download from [here]( http://repo.mysql.com/mysql-community-release-el7-5.noarch.rpm
) and install, if you are using the latter way please go through the reference link.

So axel a community-server rpm package:

```
axel -n 10 http://repo.mysql.com/yum/mysql-5.6-community/el/7/i386/mysql-community-server-5.6.15-4.el7.i686.rpmw
```

Download, then use ```yum install -y``` to install these packages, **in sequence**:

 - mysql-community-common
 - mysql-community-libs
 - mysql-community-client
 - community-server

While installing community-common, it's likely to come up with an error that community-common confilicts with mariadb-libs-*. Remove mariadb-libs-* manually. ```yum remove mariadb-libs```

After start mysql with ```systemctl start mysql```, mysql-server would be running.

ref:
http://www.mamicode.com/info-detail-503994.html
