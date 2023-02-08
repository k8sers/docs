# 在OKE上部署ERDA

Erda是云原生 PaaS 平台，一站式具备 DevOps、微服务观测治理、多云管理以及快数据治理等平台级能力。本文介绍如何在OKE中安装Erda社区版。

![img](https://static.erda.cloud/site/images/c1f1c4f5-fc1c-43b2-9223-2233fd37ff31.png?x-oss-process=image/format,webp)

# 快捷命令

快捷命令使用做好的Demo压缩包，快速在一个OKE集群中创建出一个Erda集群

![image-20230208101443055](README.assets/image-20230208101443055.png)

```shell
#卸载
helm uninstall erda -n erda-system
helm uninstall ingress -n erda-system
kubectl delete namespace erda-system

#开始安装
kubectl create namespace erda-system

#ingress
helm install ingress ingress-nginx/ingress-nginx -n erda-system
kubectl edit cm ingress-ingress-nginx-controller -n erda-system
#添加metadata中的注解：ingressclass.kubernetes.io/is-default-class: "true",
#除此之外添加关闭强制https跳转的配置data.

kubectl get svc -n erda-system
#配置DNS，指向Ingress Controller LB IP，等待10分钟左右让DNS生效（阿里云DNS+OCI VM的组合半分钟就能生效）

#redis
kubectl apply -f redis-yaml/redisfailover-secret.yaml -n erda-system
kubectl apply --server-side -f redis-yaml/databases.spotahome.com_redisfailovers.yaml -n erda-system
kubectl apply -f redis-yaml/all-redis-operator-resources.yaml -n erda-system
kubectl apply -f redis-yaml/redis-failover.yaml -n erda-system
kubectl apply -f redis-yaml/redis-service.yaml -n erda-system

#ERDA
helm install erda ./erda  -n erda-system --create-namespace --set global.domain=erda.oracle.fit --set erda.operator.tag="2.3" --set redis.enabled=false --set erda.clusterName=cluster-cpgxxdznoaq --set redis.redisFailover.secret=Oracle123456
```

分析的常用命令

```shell
kubectl get statefulset -n erda-system
kubectl get pod |grep 0/1 -n erda-system
kubectl get erda erda -n erda-system

kubectl config set-context $(kubectl config current-context) --namespace=erda-system
```

![image-20230208101014301](README.assets/image-20230208101014301.png)

![image-20230208102721461](README.assets/image-20230208102721461.png)

# 详细制作步骤和细节说明

接下来介绍我们的Demo（及yaml文件）是如何一步步做出来的

## 1. 创建OCI资源

##### Step 1.  创建OKE及VCN 

为了方便测试，我们使用快速方式创建一个公网OKE和公网Node：

![image-20230117180750119](readme.assets/image-20230117180750119.png)

![image-20230117182730282](readme.assets/image-20230117182730282.png)

在上图中，先把节点数量置为0，因为下面我们需要定制启动盘大小，后续(Step 2)还需要更新配置，把一个自动扩容磁盘的脚本加上，加上后才扩大节点到2台(Step 3)。

![image-20230117182403867](readme.assets/image-20230117182403867.png)

上传虚拟机私钥，等会要登录到WorkNode中修改配置

![image-20230117182518297](readme.assets/image-20230117182518297.png)

点击创建，等待完成：

![image-20230117183022144](readme.assets/image-20230117183022144.png)

![image-20230117183107922](readme.assets/image-20230117183107922.png)



##### Step 2. 创建NFS共享存储

点击菜单 **Storage => File System**，在界面中点击**Create File System**按钮，创建一个共享文件系统。这里，我将文件系统的名字和挂载点的名字改得更具有可读性，并让挂载点网络位于Node所在网络。

![image-20230117191843867](readme.assets/image-20230117191843867.png)

![image-20230118103434185](README.assets/image-20230118103434185.png)

得到一个挂载点( 但这里先不挂载，我们会是Step 4中用初始化脚本统一挂载)

```shell
sudo mkdir /netdata
sudo mount -o nosuid,resvport 10.0.10.191:/FileSystem-Erda /netdata
sudo sh -c 'echo "10.0.10.191:/FileSystem-Erda /netdata nfs deafults,nosuid,resvport 0 0" >> /etc/fstab'
```



如果已经有Node子网内所有协议已放行，请忽略下面的步骤：（10.0.10.0/24 All Protocals）：

在挂载前，需要先开通网络访问策略，进入 **Networking => Virtual Cloud Networks => oke-Node所在VCN  vcn-quick-Wilbur-Erda-1d8ba0783 => Node所在子网 oke-nodesubnet-quick-Wilbur-Erda-1d8ba0783-regional => Node所用安全列表 oke-nodeseclist-quick-Wilbur-Erda-1d8ba0783** 。新增以下4条Ingress规则（我的NFS和Node都在10.0.10.0/24子网）：

![image-20230118103603435](README.assets/image-20230118103603435.png)



##### Step 2. 添加磁盘扩容的初始化脚本 

等待创建完成后，在 **Containers  => Clusters => Cluster details => Node pools** 中，编辑**pool1**

![image-20230117183425776](readme.assets/image-20230117183425776.png)

找到隐藏的高级选型中的初始化脚本， 填入（**记得更换Mount Target的IP**）

```shell
#!/bin/bash
curl --fail -H "Authorization: Bearer Oracle" -L0 http://169.254.169.254/opc/v2/instance/metadata/oke_init_script | base64 --decode >/var/run/oke-init.sh
bash /var/run/oke-init.sh

sudo dd iflag=direct if=/dev/sda of=/dev/null count=1
echo "1" | sudo tee /sys/class/block/sda/device/rescan
echo "y" | sudo /usr/libexec/oci-growfs


sudo mkdir /netdata
#把下面的IP换成你的Mount Target显示的IP
sudo mount -o nosuid,resvport 10.0.10.191:/FileSystem-Erda /netdata
sudo sh -c 'echo "10.0.10.191:/FileSystem-Erda /netdata nfs deafults,nosuid,resvport 0 0" >> /etc/fstab'
sudo mount -a
```

![image-20230117183637248](readme.assets/image-20230117183637248.png)

保存。

##### Step 3. 扩容

![image-20230117183736279](readme.assets/image-20230117183736279.png)

把0台扩大成2台，等待扩容完成，约5分钟左右。



##### Step4. 访问 OKE (K8s)

复制OKE的访问命令，这个命令可以帮助我们创建一个k8s config文件 (需要事先安装oci client工具，在CloudSehll已自动配置好oci client，我们之间用即可)

![image-20230117184415756](readme.assets/image-20230117184415756.png)

打开OCI的控制台，贴入命令后按回车执行。  现在试试访问一个kubectl命令

![image-20230117185024436](readme.assets/image-20230117185024436.png)

##### Step 5.  调整Worknode的容器配置

执行

```shell
chmod -R 600 ~/.kube/config
kubectl get node -o wide
```

在 **EXTERNAL-IP** 列 可以看到Node的公网IP。使用ssh登录公网IP，用户名为**opc**， 方式为密钥（使用Step1中上传公钥对应的密钥），端口22

![image-20230117185808579](readme.assets/image-20230117185808579.png)



```shell
sudo vim /etc/crio/crio.conf
```

在末尾添加

```properties
insecure_registries = ["0.0.0.0/0"]
```

保存并执行

```shell
sudo systemctl daemon-reload
sudo systemctl restart crio
sudo systemctl status crio
```

## 2. 安装Ingress

ERDA依赖Ingress，先装它

##### Step 1. 安装Ingress

```shell
kubectl create clusterrolebinding <my-cluster-admin-binding> --clusterrole=cluster-admin --user=<user-OCID>
#比如 kubectl create clusterrolebinding jdoe_clst_adm --clusterrole=cluster-admin --user=ocid1.user.oc1..fmgq

helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress ingress-nginx/ingress-nginx -n erda-system
```

##### Step 2. 调整Ingress


将helm创建出来的Ingress Class配置成默认的Ingress（除此之外还可以配置关闭强制跳转https）

```shell
kubectl edit cm ingress-ingress-nginx-controller -n erda-system
```

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  annotations:
    ingressclass.kubernetes.io/is-default-class: "true"
    meta.helm.sh/release-name: ingress
    meta.helm.sh/release-namespace: erda-system
  creationTimestamp: "2023-02-07T09:11:26Z"
  labels:
    app.kubernetes.io/component: controller
    app.kubernetes.io/instance: ingress
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: ingress-nginx
    app.kubernetes.io/part-of: ingress-nginx
    app.kubernetes.io/version: 1.5.1
    helm.sh/chart: ingress-nginx-4.4.2
  name: ingress-ingress-nginx-controller
  namespace: erda-system
  resourceVersion: "2014798"
  uid: 6ecf4d33-e7c0-4a6c-ad71-685fee0ee3fd
data:
  ssl-redirect: "false"
```

![image-20230208103253697](README.assets/image-20230208103253697.png)

## 3. 安装开源Redis Operator

Erda-redis-operator在K8s 1.25版本启动失败，二进程程序无法调试，也没找到开源代码。

![image-20230130165504901](README.assets/image-20230130165504901.png)

从TF脚本里可以找到spotahome redis-operator的影子，所以我们自己装个redis-operator。注意erda创建的secret erda-redis-auth，里面有个密码，这个密码在Helm ERDA README.md中有说明。

![image-20230202141502180](README.assets/image-20230202141502180.png)

但因为默认里面有2个等号，开源版RedisOperator会识别成转义后的符号，所以后面的我们安装Erda的时候换一个新的默认密码（helm install erda的时候用--set 指明redis默认密码）

![image-20230208094842817](README.assets/image-20230208094842817.png)

##### Step 1.  下载Redis Operator部署文件

```shell
REDIS_OPERATOR_VERSION=v1.2.4

#用于声明自定义资源
wget https://raw.githubusercontent.com/spotahome/redis-operator/${REDIS_OPERATOR_VERSION}/manifests/databases.spotahome.com_redisfailovers.yaml 

#用于部署Redis Operator
wget https://raw.githubusercontent.com/spotahome/redis-operator/${REDIS_OPERATOR_VERSION}/example/operator/all-redis-operator-resources.yaml
```

修改all-redis-operator-resources.yaml, 删掉了2个自定义资源，修改命名空间为erda-system：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: redisoperator
  name: redisoperator
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redisoperator
  strategy:
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: redisoperator
    spec:
      serviceAccountName: redisoperator
      containers:
        - image: quay.io/spotahome/redis-operator:latest
          imagePullPolicy: IfNotPresent
          name: app
          securityContext:
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            runAsUser: 1000
          resources:
            limits:
              cpu: 100m
              memory: 50Mi
            requests:
              cpu: 10m
              memory: 50Mi
      restartPolicy: Always
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: redisoperator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: redisoperator
subjects:
  - kind: ServiceAccount
    name: redisoperator
    namespace: erda-system
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: redisoperator
rules:
  - apiGroups:
      - databases.spotahome.com
    resources:
      - redisfailovers
      - redisfailovers/finalizers
    verbs:
      - "*"
  - apiGroups:
      - apiextensions.k8s.io
    resources:
      - customresourcedefinitions
    verbs:
      - "*"
  - apiGroups:
      - ""
    resources:
      - pods
      - services
      - endpoints
      - events
      - configmaps
      - persistentvolumeclaims
      - persistentvolumeclaims/finalizers
    verbs:
      - "*"
  - apiGroups:
      - ""
    resources:
      - secrets
    verbs:
      - "get"
  - apiGroups:
      - apps
    resources:
      - deployments
      - statefulsets
    verbs:
      - "*"
  - apiGroups:
      - policy
    resources:
      - poddisruptionbudgets
    verbs:
      - "*"
  - apiGroups:
      - coordination.k8s.io
    resources:
      - leases
    verbs:
      - "*"
      
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: redisoperator
---

apiVersion: v1
kind: Service
metadata:
  annotations:
    prometheus.io/path: /metrics
    prometheus.io/port: http
    prometheus.io/scrape: "true"
  name: redisoperator
  labels:
    app: redisoperator
spec:
  type: ClusterIP
  ports:
  - name: metrics
    port: 9710
    protocol: TCP
    targetPort: metrics
  selector:
    app: redisoperator
```

![image-20230202184820238](README.assets/image-20230202184820238.png)

##### Step 2. 创建密钥

redis-yaml/redisfailover-secret.yaml:

```yaml
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: erda-redis-auth
  namespace: erda-system
data:
  password: T3JhY2xlMTIzNDU2
```

这个密码是明文Oracle123456经过Base64编码后的文件。

*注意：这个明文会被放到Redis Pod的环境变量中，如果有Linux环境变量识别不了的符号，那密码会被Linux转义*

##### Step 3 创建哨兵部署文件

用于创建一个单节点的哨兵版Redis: redis-failover.yaml

```yaml
apiVersion: databases.spotahome.com/v1
kind: RedisFailover
metadata:
  name: redisfailover
spec:
  sentinel:
    replicas: 1
  redis:
    replicas: 1
  auth:
    secretPath: erda-redis-auth
```

补一个和Erda Redis同名的Service：redis-service.yaml

```shell
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/component: sentinel
    app.kubernetes.io/managed-by: redis-operator
    app.kubernetes.io/name: redisfailover
    app.kubernetes.io/part-of: redis-failover
    redisfailovers.databases.spotahome.com/name: redisfailover
  name: rfs-erda-redis
  namespace: erda-system
spec:
  ports:
  - name: sentinel
    port: 26379
    protocol: TCP
    targetPort: 26379
  selector:
    app.kubernetes.io/component: sentinel
    app.kubernetes.io/name: redisfailover
    app.kubernetes.io/part-of: redis-failover
  type: ClusterIP
```

##### Step 4.  安装Redis

```shell
kubectl apply -f redis-yaml/redisfailover-secret.yaml -n erda-system
kubectl apply --server-side -f redis-yaml/databases.spotahome.com_redisfailovers.yaml -n erda-system
kubectl apply -f redis-yaml/all-redis-operator-resources.yaml -n erda-system
kubectl apply -f redis-yaml/redis-failover.yaml -n erda-system
kubectl apply -f redis-yaml/redis-service.yaml -n erda-system
```



## 4. 安装ERDA

ERDA社区版最高支持 K8s 1.20版本。  我们创建的OKE中K8s是1.25版本，要调整部分内容

##### Step 1. 下载ERDA

在OCI Cloud Shell中执行

```shell
helm repo add erda https://charts.erda.cloud/erda
helm repo update
helm search repo erda
helm pull erda/erda
tar xzvf erda-2.2.0.tgz
```

![image-20230118131315782](README.assets/image-20230118131315782.png)

##### Step 2. 修改ERDA

打开OCI右上角Editoer，编辑 erda/crds/erda_crd.yaml。因为K8s 1.22版本不再支持Beta版的CRD，所以将CRD格式调整为以下内容

```shell
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: erdas.erda.terminus.io
spec:
  conversion:
    strategy: None
  group: erda.terminus.io
  names:
    kind: Erda
    listKind: ErdaList
    plural: erdas
    singular: erda
  scope: Namespaced
  versions:
  - additionalPrinterColumns:
    - description: Erda cluster current status
      jsonPath: .status.phase
      name: Status
      type: string
    - description: last message
      jsonPath: .status.conditions[0].reason
      name: LastMessage
      type: string
    name: v1beta1
    schema:
      openAPIV3Schema:
        properties:
          spec:
            type: object
            x-kubernetes-preserve-unknown-fields: true
          status:
            type: object
            x-kubernetes-preserve-unknown-fields: true
        type: object
    served: true
    storage: true
    subresources:
      status: {}
```

![image-20230208103924260](README.assets/image-20230208103924260.png)

在erda/templates/erda-operator-clusterrole.yaml的结尾处追加新版本所需的权限： 

```shell
  - apiGroups:
      - autoscaling.k8s.io
    resources:
      - verticalpodautoscalers
    verbs:
      - '*'
  - apiGroups:
      - autoscaling
    resources:
      - horizontalpodautoscalers
    verbs:
      - '*'
```



##### Step 3. 安装Erda

erda.operator.tag的镜像使用Github的最新版2.3，否则会造成erda-operator启动失败（创建crd"dices.dice.terminus.io"失败）。

redis密钥也需要改成设置未Linux环境变量后不被转义的密码。

```shell
helm install erda ./erda  -n erda-system --create-namespace --set global.domain=erda.oracle.fit --set erda.operator.tag="2.3" --set redis.enabled=false --set erda.clusterName=cluster-cpgxxdznoaq --set redis.redisFailover.secret=Oracle123456
```

![image-20230130170828150](README.assets/image-20230130170828150.png)



![image-20230208101014301](README.assets/image-20230208101014301.png)

![image-20230208102721461](README.assets/image-20230208102721461.png)

# 未完待续

能注册，能进入用户中心，但是无法跳转到首页（提示OAuth认证错误）



## 相关材料

* ERDA安装说明：https://docs.erda.cloud/2.2/manual/install/helm-install/helm-install-demo.html
* K8s CRD定义：https://kubernetes.io/docs/reference/kubernetes-api/extend-resources/custom-resource-definition-v1/
* Erda Operator : https://github.com/erda-project/erda-operator
* 开源Redis Operator：https://github.com/spotahome/redis-operator
* k8s 1.18 + erda 安装视频： https://www.bilibili.com/video/BV1fQ4y1z7Xz/?spm_id_from=333.999.0.0&vd_source=87d3f33c930eb977519850fe5fc3a2b0