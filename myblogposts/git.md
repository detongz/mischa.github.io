
# 毕业前最后一次例会：社区开发和Git

## Part1：Git一些背景知识

1. git rebase\git merge

git merge和rebase效果相似。

2. git fetch\git pull

pull=fetch+merge

在同步远程代码变更的时候：

```
git fetch origin
git rebase −p origin/develop
```

3. git push\git review

push是强推，review是放到服务器上存好，等测试、review通过后合并或放弃。

4. git stash



## Part2：参与到开源社区的建设中

这部分主要介绍如何在openstack社区里愉快的玩耍。

听说工作室用docker的比较多，大概写go的也多。docker上个月刚刚改名为moby了，忘记这件事的我在github上找了半天。改名的目的似乎是要把docker分成更细分的项目。docker社区接下来会有很多要开发的东西，*积极参与社区并作出贡献*与做*面向大学生的比赛*相比技术方面的含金量在找工作的时候对相应公司的相应岗位会更高。推荐对开源社区感兴趣的同学到社区中积极贡献代码。

openstack是一群子项目的集合。15年的时候当初docker和openstack拿来比较的文章天天都能看到，现在docker更专著paas，而openstack的paas功能的确是有一点点鸡肋&bug多。

工作室写go的同学请自觉主动关注docker和k8s社区。写python的可以看openstack社区人写的代码学习，或者给你们耳熟能详的web框架贡献代码都是可以的= =

*kubernetes不是英文单词，念`/koo ber ne tis/`这样。其缩写是k8s。*


现在Openstack社区有一套流程给开放者使用，这套流程为开放者和社区省了不少事。openstack社区在2015年初还没有应用CI/CD系统的时候，其开发和code review模式和现在docker、k8s社区用的模式相同：

- github上有一个专门项目记录issue，进行讨论；
- 代码审查是通过pull request发起的，比较麻烦；
- 自动化测试在开发人员的环境里运行


## 注意练习一些很有用的能力

一项兴趣爱好
阅读真实英文材料的能力（不是那种中国人写给中国人看还是鸡汤的那种）1年刻意练习足够
完成事情的能力，沟通的能力
保持身体健康的习惯

## refs:
https://wiki.openstack.org/wiki/How_To_Contribute
https://docs.openstack.org/infra/manual/developers.html
https://www.derekgourlay.com/blog/git-when-to-merge-vs-when-to-rebase/
