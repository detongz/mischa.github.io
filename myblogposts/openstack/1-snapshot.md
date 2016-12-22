# cinder & nova snapshot区别和联系

cinder、nova都有创建snapshot的功能。

cinder snapshot针对的是volume，nova snapshot针对的是instance，通过nova创建snapshot后上传到glance。

具体到cli，直接查help里面有没有snapshot即可。

```
cgsnapshot-create   Creates a cgsnapshot.
cgsnapshot-delete   Removes one or more cgsnapshots.
cgsnapshot-list     Lists all cgsnapshots.
cgsnapshot-show     Shows cgsnapshot details.
                    Creates a consistency group from a cgsnapshot or a
snapshot-create     Creates a snapshot.
snapshot-delete     Removes one or more snapshots.
snapshot-list       Lists all snapshots.
snapshot-metadata   Sets or deletes snapshot metadata.
snapshot-metadata-show
                    Shows snapshot metadata.
snapshot-metadata-update-all
                    Updates snapshot metadata.
snapshot-rename     Renames a snapshot.
snapshot-reset-state
                    Explicitly updates the snapshot state.
snapshot-show       Shows snapshot details.

image-create                Create a new image by taking a snapshot of a running server.
volume-snapshot-create      DEPRECATED: Add a new snapshot.
volume-snapshot-delete      DEPRECATED: Remove a snapshot.
volume-snapshot-list        DEPRECATED: List all the snapshots.
volume-snapshot-show        DEPRECATED: Show details about a snapshot.
```

glance 的help信息中则没有snapshot相关的信息，因此从cinder、nova入手。

Cinder前身是nova中的 nova-volume 服务， F版及以后被分离出来成为Cinder这个独立项目。

Cinder为虚拟机提供持久化的块存储能力，实现虚拟机volume的创建、挂载卸载、snapshot等生命周期管理。

Instance snapshot和 cinder snapshot区别和联系：

instance snapshot 能对一个instance的系统盘在某一时刻创建快照，这个快照可用于创建Glance镜像，这个镜像用于创建新的instance。

cinder snapshot是对一个 cinder volume（磁盘）在某一时刻创建快照，这比instance snapshot更灵活。这个快照可以用来创建新实例的启动磁盘，可以用这个快照创建磁盘后把它作为存储卷添加到已有的/新建的instance里去。

有的说法是nova snapshot创建的镜像不存用户数据，而cinder snapshot能存用户数据，这个待考证，还有说法是可以用cinder snapshot建glance镜像，待考证。。

reference：

http://docs.openstack.org/user-guide/cli-use-snapshots-to-migrate-instances.html
https://www.ibm.com/developerworks/community/blogs/132cfa78-44b0-4376-85d0-d3096cd30d3f/entry/Snapshot_Instance_%E6%93%8D%E4%BD%9C%E8%AF%A6%E8%A7%A3_%E6%AF%8F%E5%A4%A95%E5%88%86%E9%92%9F%E7%8E%A9%E8%BD%AC_OpenStack_36?lang=en
http://serverfault.com/questions/268719/amazon-ec2-terminology-ami-vs-ebs-vs-snapshot-vs-volume/268727#268727
