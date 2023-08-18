# OKE VCN-Native及Flannel网络性能测试

创建2个OKE集群，apiendpoint和worknode都放到公网以便测试

* OKE-Native： Node Pool配置为3台VM.Optimized3.Flex 2 OCPU 16GB内存,  快速创建向导模式（自动创建网络），上下文名为oke-native
* OKE-Flannel： Node Pool配置为3台VM.Optimized3.Flex 2 OCPU 16GB内存，使用OKE-Native的网络,  上下文名为oke-flannel

创建1台测试服务器： 

* VM.Optimized3.Flex 4 OCPU 16GB内存， CentOS 7,  网络放到OKE的Node网络

## 1.制作测试工具

##### Step 1.  制作测试镜像

编写docker file

```shell
vim dockerfile
```

```shell
FROM centos:7.9.2009

RUN mkdir /root/tools
RUN cd /root/tools
RUN yum install -y wget
RUN wget --no-check-certificate https://iperf.fr/download/fedora/iperf3-3.1.3-1.fc24.x86_64.rpm -O /root/tools/iperf3-3.1.3-1.fc24.x86_64.rpm
RUN rpm -ivh /root/tools/iperf3-3.1.3-1.fc24.x86_64.rpm
COPY iperf-*.sh /root/ 
RUN chmod +x /root/*.sh
RUN ls /root/
EXPOSE 5201
WORKDIR /root/
```

编写启动脚本

```shell
echo 'iperf3 -c $IPERF_SERVER_HOST -i 1 w 1M' > iperf-client.sh
echo '/bin/iperf3 -s -i 1' > iperf-server.sh
chmod +x ./*.sh
```

编译并上传镜像

```shell
docker login -u 'sehubjapacprod/oracleidentitycloudservice/xxx@oracle.com' iad.ocir.io
docker image build . -t iperf:3.1
docker tag iperf:3.1 iad.ocir.io/sehubjapacprod/iperf:3.1
docker push iad.ocir.io/sehubjapacprod/iperf:3.1
```

##### Step 2. 部署测试工具

```shell
vim iperf-server.yaml
```

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: iperf-server
spec:
  selector:
    matchLabels:
      app: iperf-server
  template:
    metadata:
      labels:
        app: iperf-server
    spec:
      containers:
      - name: iperf-server
        image: iad.ocir.io/sehubjapacprod/wilbur/iperf:3.1
        imagePullPolicy: Always
        command:
          - sh
          - "/root/iperf-server.sh"
        ports:
        - containerPort: 5201
---
kind: Service
apiVersion: v1
metadata:
  name: iperf-nlb
  annotations:
    oci.oraclecloud.com/load-balancer-type: "nlb"
spec:
  selector:
    app: iperf-server
  type: LoadBalancer
  ports:
  - name: iperf
    port: 5201
    targetPort: 5201
```

##### 

```shell
vim iperf-client.yaml
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: iperf-client
  labels:
    app: iperf-client
spec:
  containers:
  - name: iperf-client
    image: iad.ocir.io/sehubjapacprod/wilbur/iperf:3.1
    imagePullPolicy: Always
    command:
      - sleep
      - "36000"
    ports:
    - containerPort: 5201
```





在Flannel集群和VCN-Native集群都部署测试客户端和服务端

```shell
kubectl apply -f iperf-server.yaml --context=oke-native
kubectl apply -f iperf-server.yaml --context=oke-flannel

kubectl apply -f iperf-client.yaml --context=oke-native
kubectl apply -f iperf-client.yaml --context=oke-flannel
```

**部署完后，手工将LB的带宽改为Flex 2048Mbps ~ 2128Mbps** (最大值尽量大点，这里配置2128是因为资源受限了)



##### Step 3. 部署结果


###### Flannel部署结果
node:

```shell
NAME          STATUS   ROLES   AGE    VERSION   INTERNAL-IP   EXTERNAL-IP       OS-IMAGE                  KERNEL-VERSION                    CONTAINER-RUNTIME
10.0.10.184   Ready    node    135m   v1.27.2   10.0.10.184   129.146.122.224   Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
10.0.10.225   Ready    node    135m   v1.27.2   10.0.10.225   129.146.79.228    Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
10.0.10.34    Ready    node    135m   v1.27.2   10.0.10.34    129.146.58.53     Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
```
pod:
```
NAME                 READY   STATUS    RESTARTS   AGE     IP             NODE          NOMINATED NODE   READINESS GATES
iperf-client         1/1     Running   0          6m33s   10.244.0.133   10.0.10.184   <none>           <none>
iperf-server-8vvm9   1/1     Running   1          19h     10.244.0.2     10.0.10.34    <none>           <none>
iperf-server-mxfmq   1/1     Running   1          19h     10.244.1.3     10.0.10.225   <none>           <none>
iperf-server-nxnrh   1/1     Running   1          19h     10.244.0.131   10.0.10.184   <none>           <none>
```

service:
```
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP                   PORT(S)             AGE    SELECTOR
iperf-nlb    LoadBalancer   10.96.238.13   10.0.20.220,129.146.109.147   5201:30195/TCP      11m    app=iperf-server
kubernetes   ClusterIP      10.96.0.1      <none>                        443/TCP,12250/TCP   137m   <none>
```

###### VCN-Native部署结果
node:

```shell
NAME          STATUS   ROLES   AGE     VERSION   INTERNAL-IP   EXTERNAL-IP       OS-IMAGE                  KERNEL-VERSION                    CONTAINER-RUNTIME
10.0.10.110   Ready    node    133m    v1.27.2   10.0.10.110   129.146.16.22     Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
10.0.10.122   Ready    node    9m53s   v1.27.2   10.0.10.122   129.146.109.180   Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
10.0.10.143   Ready    node    133m    v1.27.2   10.0.10.143   129.146.60.217    Oracle Linux Server 7.9   5.4.17-2136.320.7.el7uek.x86_64   cri-o://1.27.0-155.el7
```
pod:
```
NAME                 READY   STATUS    RESTARTS   AGE   IP            NODE          NOMINATED NODE   READINESS GATES
iperf-client         1/1     Running   0          9s    10.0.10.207   10.0.10.122   <none>           <none>
iperf-server-77jzq   1/1     Running   1          19h   10.0.10.245   10.0.10.122   <none>           <none>
iperf-server-k8m52   1/1     Running   1          19h   10.0.10.51    10.0.10.110   <none>           <none>
iperf-server-tzqkh   1/1     Running   1          19h   10.0.10.65    10.0.10.143   <none>           <none>
```

service:
```
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP                  PORT(S)             AGE    SELECTOR
iperf-nlb    LoadBalancer   10.96.182.15   10.0.20.158,129.146.60.184   5201:30157/TCP      10m    app=iperf-server
kubernetes   ClusterIP      10.96.0.1      <none>                       443/TCP,12250/TCP   140m   <none>
```


##### step 4.  测试机安装工具

```shell
sudo wget --no-check-certificate https://iperf.fr/download/fedora/iperf3-3.1.3-1.fc24.x86_64.rpm 
sudo rpm -ivh iperf3-3.1.3-1.fc24.x86_64.rpm

sudo su
# 使用域名测试更方便。注意更换下面nlb的IP
echo "10.0.20.158 nlb-oke-native" >> /etc/hosts
echo "10.0.20.220 nlb-oke-flannel" >> /etc/hosts
su opc

```





## 2. Flannel 与 VCN-Native 网络测试

2.1 集群内Pod相互通信是为了让大家了解不通的OKE CNI在性能和资源消耗方面的差异。 

2.2 与 2.3 从集群外访问，目的是为了让大家了解OKE(K8s)的网络运行机制，至于性能和资源消耗方面请看 2.1。

### 2.1 集群内 Pod --> 另一台Node上的Pod

直接把流量给到另一台Node上的Pod，流量100%经过在源Node上进行Flannel封包和在目的Node上进行Flannel解包，更方便测试性能。

排除iperf-client所在Node，从其他2台Node中任选一台作为服务端Node：

| CNI        | 客户端Node IP                  | 客户端Pod IP | 服务端Node IP                 | 服务端Pod IP |
| ---------- | ------------------------------ | ------------ | ----------------------------- | ------------ |
| Flannel    | 10.0.10.184（129.146.122.224） | 10.244.0.133 | 10.0.10.225（129.146.79.228） | 10.244.1.3   |
| VCN-Native | 10.0.10.122（129.146.109.180） | 10.0.10.207  | 10.0.10.143（129.146.60.217） | 10.0.10.65   |

测试结果：Flannel多用0.1 OCPU（5% CPU），内存几乎一样。

![image-20230818194640420](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818194640420.png)

##### Step 1. TCP 协议

**结论：转发TCP流量时，VCN-Native CNI的吞吐高0.51%，CPU多5%（为了处理8Gbps的流量，Flannel多使用0.1 OCPU），可见VCN-Native效率与Flannel几乎一致**

左边是Flannel结果7.92Gbps，右边是VCN-Native结果7.96Gbps, 差异不大(Flannel叠加头体积与TCP 1MByte/500Byte的数据窗口相比可以忽略不计）：

![image-20230817173423406](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230817173423406.png)

![image-20230818105117193](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818105117193.png)

![image-20230818185101054](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818185101054.png)

![image-20230818190509325](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818190509325.png)

下面iperf客户端所在的Node监控指标，左边是Flannel，右边是VCN-Native。因为客户端负责发送流量，所以左边的Flannel使用了额外的5%CPU用于Flannel封包（叠加VXLAN头）

![image-20230818185432992](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818185432992.png)

下面iperf服务端所在的Node监控指标，左边是Flannel，右边是VCN-Native。因为服务端负责接受流量，所以左边的Flannel使用了额外的5%CPU用于Flannel解封包（去除叠加VXLAN头）

![image-20230818185640864](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818185640864.png)

至于OCI对Instance的网络监控意义不大。 从监控上看，Flannel的网络流量是Native的2倍（VCN-Native有2张网卡，所以结果除以了2？正在与PM确认中。。）

![image-20230818190031649](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818190031649.png)

为了方便显示真实流量，我在上面的4台Node上都安装了iftop工具，可以看出网卡的流量与速率与iperf结果一致。

```shell
sudo yum install -y iftop

#Flannel流量经过ens3
sudo iftop -i ens3
#VCN-Native流量经过ens5
sudo iftop -i ens5
```

Flannel的iperf客户端所在Node的ens3网卡：

![image-20230818104820996](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818104820996.png)

Flannel的iperf服务端所在Node的ens3网卡：

![image-20230818104831900](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818104831900.png)

VCN-Native的iperf客户端所在Node的ens5网卡：

![image-20230818104842471](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818104842471.png)

VCN-Native的iperf服务端所在Node的ens5网卡：

![image-20230818104905243](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818104905243.png)

VCN-Native模式的ENS3网卡几乎没流量

![image-20230818104931345](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818104931345.png)



##### Step 2. UDP 协议(略超临界速率)

**结论： Flannel的封包多用5%CPU，解封包反而比VCN-Native少用2% CPU**

用8Gbps的UDP流量打满Flannel CNI与VCN-Native CNI。因为还有额外的头信息，所以实际打的流量会轻微超过网卡的8Gbps（出现小概率丢包）

![image-20230818192519791](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818192519791.png)

iperf客户端所在Node的CPU情况还是Flannel要高5%（发送流量时添加VXLAN头）

![image-20230818192853098](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818192853098.png)

iperf服务端所在Node的CPU情况反而是Flannel要低2%。

![image-20230818193045701](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818193045701.png)

##### Step 3. UDP 协议(正常速率)

**结论： Flannel的丢包与抖动更低**

用7.4Gbps的UDP流量压Flannel CNI与VCN-Native CNI。这时两种CNI处理能力都是7.4Gbps，这时可以分析丢包与抖动情况。结果显示Flannel性能更好（与PM的报告结果相反）

![image-20230818193741805](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818193741805.png)

iperf客户端所在Node的CPU情况还是Flannel要高5%（发送流量时添加VXLAN头）

![image-20230818194121209](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818194121209.png)

iperf服务端所在Node的CPU情况反而是Flannel要低2%。

![image-20230818200729275](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818200729275.png)

### 2.2 集群外测试VM --> NLB --> Kube-Proxy --> Flannel --> Pod

在本次测试中，NLB通过Hash算法选中了 WorkNode-0，流量转发到WorkNode-0上的NodePort端口。 这个K8s service的端口由Kube-Proxy（Iptables）维护，并通过Iptables的随机函数选中了WorkNode-2的Pod，通过Flannel转发给WorkNode-2。（如果Iptables随机到WorkNode-0自身的Pod，则不需要Flannel转发，这样也没了测试CNI的意义。但这样对生产环境有意义，因为带宽看起来扩大了1倍，实则带宽扩大2/3倍，因为只有2/3的概率会被Flannel转发）。

**注意：下图中红色的线是通过Flannel转发的。**

![image-20230818231749411](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818231749411.png)

此时，流量收WorkNode-0的总带宽限制（8Gbps = RX 4Gbps + TX 4Gbps)，最终流量只能有4Gbps 

```shell
#向NLB的内网IP打流量
iperf3 -c 10.0.20.220 --time=3600 --interval 10 w 1K


#在所有worknode上监听
sudo iftop -i ens3
```

![image-20230818223114102](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818223114102.png)



WorkNode-0有流入和流出的流量。这个流量是从NLB流进来， 并转发到WorkNode-2 上. （请忽略SSH标签页名称Flannel-0/1/2，看iftop正文中显示的主机名)

![image-20230818224742865](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818224742865.png)

![image-20230818230642198](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818230642198.png)

WorkNode-2 收到 WorkNode-0的流量：

![image-20230818222840794](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818222840794.png)

![image-20230818230854098](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818230854098.png)

### 2.2 集群外测试VM --> NLB --> Kube-Proxy --> VCN-Native --> Pod

在本次测试中，NLB通过Hash算法选中了 WorkNode-3，流量转发到WorkNode-0上的NodePort端口。 这个K8s service的端口由Kube-Proxy（Iptables）维护，并通过Iptables的随机函数选中了WorkNode-1的Pod，此时Kube-Proxy（Iptables）把数据包直接丢给VCN处理，VCN能正确找到所有Pod，因为所有Pod的IP都在Worknode的第二块网卡上挂有Pod IP。（与Flannel一样，如果Iptables随机到WorkNode-3自身的Pod，则不需要VCN转发，这样也没了测试CNI的意义。但这样对生产环境有意义，因为带宽看起来扩大了1倍，实则带宽扩大2/3倍，因为只有2/3的概率会被VCN转发）。

**注意：下图中红色的线是通过VCN云网络转发的。**

![image-20230818235856951](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818235856951.png)





此时，流量收WorkNode-3的总带宽限制（8Gbps = ens3 RX 4Gbps + ens3 TX 4Gbps)，最终流量只能有4Gbps 

```shell
#在Test VM上向NLB的内网IP打流量
iperf3 -c 10.0.20.158 --time=3600 --interval 10 w 1K

#在所有worknode上监听Node网卡
sudo iftop -i ens3
#在所有worknode上监听Pod网卡
sudo iftop -i ens5
```



![image-20230818233354878](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818233354878.png)



WorkNode-3的Kube-Proxy（Iptables）在ens3网卡上，收到了来自NLB的包。 然后Kubeproxy(Iptables)又把它转到了10.0.10.246这个Pod中(也是从ens3走的)：

![image-20230818235247337](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818235247337.png)

![image-20230819000711631](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230819000711631.png)

可以看到10.0.10.246这个pod在10.0.10.110这个Node上

![image-20230818232832352](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818232832352.png)

10.0.10.110对应的node是WorkNode-1

![image-20230818235722199](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818235722199.png)

WorkNode-1的ENS5网卡（Pods网卡）有流入流量，从WorkNode-3的ens3网卡（Node网卡）而来。

![image-20230818235103072](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230818235103072.png)

![image-20230819000801149](E:\Docs\GitDoc\tech-doc\云厂商\甲骨文\PaaS\OKE\OKE网络\OKE网络性能测试.assets\image-20230819000801149.png)















