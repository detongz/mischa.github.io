# Heat 认证模型第二部分 - Stack Domain Users

翻译：zhangdetong

原作者 Steve Hardy 是Heat社区的以为从很早就参与了设计和开发的一位核心开发者。
作者写作时间是2014年8月，和上一篇一样，应该以Icehouse版本为准。
翻译时间为2016年11月，Ocata版本正在开发中。

[原文地址](https://hardysteven.blogspot.com/2014/04/heat-auth-model-updates-part-2-stack.html?showComment=1480042996365#c9135691387438895727)

这篇文章里涉及到了最近被实现的[实例用户blueprint](https://blueprints.launchpad.net/heat/+spec/instance-users)，其中使用了keystone的[domain](https://github.com/openstack-attic/identity-api/blob/master/v3/src/markdown/identity-api-v3.md#domains-v3domains)，domain中用户相关的证书，这些证书是在heat创建的实例里部署的。

**译文：**

## 所以为什么heat要创建用户呢？

这就说来话长了。Heat由于历史原因，需要完成以下几方面功能：

  1. 给实例里面的agent提供meatadata，agent会轮询是否有改变并把metadata里面的配置都应用到实例里面去。
  2. 发出信号表示一些动作完成，尤其是在一台启动的虚拟机上配置软件（因为nova一旦生成了一台VM，就把它的状态变为“Active”，不是当heat已经把他配置完成才改变状态）
  3. 提供实例内部应用级的状态或指标，例如允许在一些服务的性能指标或质量指标改变时执行AutoScaling操作。

Heat提供了可以实现所有这些功能的API，但是这些API需要某种认证，例如证书，这样无论什么agent在实例上运行都可以访问之。因此证书必须被不熟在实例内部，例如下面的图片展示了如果使用heat-cfntools的agent会发生些什么：

![heat-cfntools agent 数据流，结合了CFN的API](../img/software_config5_small.png)

heat-cfntools agent使用签名的请求，签名请求需要一个通过keystone创建的ec2秘钥，这个秘钥用于给heat cloudformation和cloudwatch兼容的API的请求签名。这些API是通过签名验证（需要keystone的ec2tokens扩展）的方式被heat认证的。

问题是，ec2密钥对是和一个用户挂钩的。我们不想部署直接于stack owner相关的证书，否则任何（隐式不可信的）实例的缺陷都可能导致一个巨大的缺陷，即攻击者可以控制有stack访问权限的用户可以访问的任何内容。

我用cfntools/ec2tokens举了个例子，如果使用任何可以通过keystone获取（如token，username/password）、可以用来通过heat API进行认证的证书，相同的问题都会存在。

因此我们需要分离的、隔离的证书部署到实例里。这样一来我们可以把允许的访问行为限制到所需的最少情况。我们的第一次尝试是这样的：

 - 在和stack owner同一个project下用Keystone里创建一个新用户（即可以明确地通过User和AccessKey资源创建也可以用WaitConditionHandle和ScalingPolicy资源。我们从内部获取一个ec2秘钥，用于产生一个没有被签过名的URL）
 - 添加“heat stack user”到一个特殊的role——默认的“heat_stack_user”里面（通过配置heat.conf里的heat_stack_user_role进行修改)
 - 通过policy.json来限制API接口的访问，我们期望其他服务也会像这样被限制，或是通过网络隔离/防火墙规则来完全禁止访问。

这种方式有缺陷，这个缺陷导致了这个[长期存在的bug](https://bugs.launchpad.net/heat/+bug/1089261),这个问题有集中解决方法：

- 需要创建stack的用户被允许在keystone中创建用户，这必然需要有管理员权限的role。
- 不能提供完全的隔离，即便是policy规则，依然是可能存在有缺陷的stack被滥用于认证（例如把用户在同一项目中获取的metadata用于其他stack）
- 这样会把项目的用户列表用假用户（对于用户和操作者的角度看来）弄得混乱，这些用户只是heat实现的细节，我们也把它们都暴露给了终端用户。

## 这听起来挺差的，有木有其他方法呢？

我们已经思考了有段时间了，我们讨论了很多种解决方案：

 - 通过trusts授权一个用户role的子集（驳回）
 - 基于一些随机的“token”来搞我们自己的认证机制（一些人觉得这个想法不错，但是我反对之）
 - 使用keystone的OAuth秘钥和签名请求（由于keystoneclient不支持而驳回）
   - 通过创建一个完全隔离的heat专用的keystone domain，从而隔离实例里面的用户。这个方案是 [Adam Young](http://adam.younglogic.com/category/software/openstack/) 提出的，也是我们在[Icehouse版本中进行实现的方案](https://blueprints.launchpad.net/heat/+spec/instance-users)。

## “Stack Domain Users”的细节

新的方法是一个对已有的实现进行的有效优化。我们封装了所有stack定义的用户（即由于heat模板里的内容而被创建的用户），把他们放到另一个隔开的domain里，这个domain是特别用来包含仅仅和heat stack有关的东西的。创建一个“domain admin”用户，heat使用这个用户，管理在“stack user domain”里用户的生命周期。

下面我将讨论两个方面，一是部署环境的时候需要做的事，即启动Heat里的stack domain user（Icehouse或其后版本）；二是当创建一个stack的时候实际上做了什么，以及如何解决我们之前提出的问题：

### 在部署heat的时候：

- 生成一个特殊的keystone domain。例如一个成为“heat”且把heat.conf中的ID值设置为“stack_user_domain”
- 生成一个有足够权限进行创建/删除project的用户，在“heat”这个domain下被创建。例如，在devstack中会生成一个“heat_domain_admin”的用户，并给予之heat domain的管理员role
- domain admin用户的用户名/密码在heat.conf里进行设置（即stack_domain_admin和stack_domain_admin_password）。这个用户代表stack owner对“stack domain user”进行管理，因此stack owner本身并不必须是admin。由于heat_domain_admin仅赋予了“heat”domain的管理员权限，因此这个上报途径的风险得到了控制。

这些都在使用近期的devstack时自动完成，但是如果使用其他方法进行部署，那需要使用python-openstackclient（这是keystone v3的CLI接口）进行domain和user的创建：

### 创建domain：

$OS_TOKEN 是以token，例如service admin token，或是其他对一个拥有有效的role进行user和domain创建的有效token。

$KS_ENDPOINT_V3 是v3 keystone终端，例如 http://<keystone>:5000/v3，<keystone>是IP地址或是可以解析到的keystone service名。

```
openstack --os-token $OS_TOKEN --os-url=$KS_ENDPOINT_V3 --os-identity-api-version=3 domain create heat --description "Owns users and projects created by heat"
```

这行命令会返回一个domain ID，在下面会被用到$HEAT_DOMAIN_ID配置中。

### 创建用户：

openstack --os-token $OS_TOKEN --os-url=$KS_ENDPOINT_V3 --os-identity-api-version=3 user create --password $PASSWORD --domain $HEAT_DOMAIN_ID heat_domain_admin --description "Manages users and projects created by heat"

这行命令返回user ID，在下面会被用到$DOMAIN_ADMIN_ID配置中。

### 把用户设为domain管理员：

openstack --os-token $OS_TOKEN --os-url=$KS_ENDPOINT_V3 --os-identity-api-version=3 role add --user $DOMAIN_ADMIN_ID --domain $HEAT_DOMAIN_ID admin

接下来需把domain ID，用户名和密码添加到heat.conf里面：

```
stack_domain_admin_password = <password>


stack_domain_admin = heat_domain_admin

stack_user_domain = <domain id returned from domain create above>
```

### 当一个用户创建了一个stack时：

- 如果stack包含任何需要创建一个“stack domain user”的resource的话，就要在“heat”domain下创建一个新的“stack domain project”
- 任何需要一个用户的资源，我们在“stack domain project”中创建这个用户。它和heat stack在heat数据库里有关联关系，但是和stack owner project完全隔离且不相关（从认证的角度来说不相关）。
- 用户创建stack domain依然会被分配heat_stack_user的role，在访问API的时候他们所能访问的是根据policy.json限制的。
- 在解析API请求的时候，我们会做内部查询，并允stack owner的project（默认的stack的API路径）和“stack domain user”从数据库里获取某个制定的stack的详细信息，依然服从policy.json的配置。

需要澄清最后一条，意思是目前有两个地址可以从heat API请求相同的信息，例如请求resource-metadata：

```GET v1/​{stack_owner_project_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/metadata```

或是

```GET v1/​{stack_domain_project_id}​/stacks/​{stack_name}​/​{stack_id}​/resources/​{resource_name}​/metadata```

stack owner会使用第一种方法（例如heat resource-metadata {stack_name} {resource_name}会使用第一种格式的get请求），其他instance中的用户都会使用第二种get方法。

这解决了所有之前提出的问题：

- stack owner 不再需要admin role，因为heat_domain_admin用户会管理stack domain user
- 实现了完全隔离，在stack domain project里创建的用户不能够访问除了heat明确允许的资源以外的其他任何资源。访问任何其他的stack和访问任何stack-owner拥有的资源，都会失败
- stack-owner project中的用户列表不受影响，因为我们已经在另一个domain里创建了一个完全不同的project
