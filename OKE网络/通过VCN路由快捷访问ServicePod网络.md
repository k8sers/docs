# 通过VCN路由表快捷访问K8s的Service/Pod网络

本文介绍在OCI中如何让非OKE的子网直接访问Flannel OKE的服务和Pod的Cluster IP, 也就是下表中的test-subnet直接访问k8s-service-subnet和

| 子网名称               | CIDR           | 说明 |
| ---------------------- | -------------- | ---- |
| node-subnet            | 192.168.0.0/24 |      |
| lb-subnet              | 192.168.1.0/24 |      |
| test-subnet            | 192.168.2.0/24 |      |
| k8s-service-subnet     | 10.96.0.0/16   |      |
| k8s-flannel-pod-subnet | 10.244.0.0/16  |      |



## 创建VCN

VCN网络 192.168.0.0,  OKE的K8s和Node子网都是192.168.0.0, LB子网是192.168.1.0.

##### Step 1. 创建VCN

![image-20230319213722149](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319213722149.png)

##### Step 2. 跳调整网络策略

为了测试，将默认SecurityList的流量全部放行（真实环境严禁如此）

![image-20230319214412709](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319214412709.png)

##### Step 2. 创建Internet Gateway

![image-20230319214621798](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319214621798.png)

##### Step 4. 调整路由表

![image-20230319215408050](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319215408050.png)

##### Step 5. 创建子网

![image-20230319221308886](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319221308886.png)

## 创建测试VM 

创建一台Linux的Instance，放到test-subnet中

![image-20230319224658636](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319224658636.png)

## 创建OKE 

##### Step 1. 创建OKE

OKE 的服务网络 10.96.0.0/16 和Flannel 叠加Pod网络是10.244.0.0/16

用自定义方式创建OKE

![image-20230319221951498](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319221951498.png)

##### Step 2. 创建节点池

放到node-subnet中 

![image-20230319222030650](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319222030650.png)

创建好后，拿到其中一台WorkNode的作为K8s网络的网关，记下其内网IP地址，后续配置路由时用到（下图Not ready是work node还在初始化，稍等一会就会正常）

![image-20230319233105958](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319233105958.png)

进入这台WorkNode，编辑虚拟网卡，允许目的地址不是自己的包

![image-20230319233504526](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319233504526.png)

![image-20230319233557444](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319233557444.png)

##### Step 3.  添加K8s路由规则

到VCN路由表中，添加2条规则

![image-20230319234646856](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319234646856.png)

![image-20230319233658381](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319233658381.png)



##### Step 2. 部署测试应用

```shell
kubectl apply -f https://raw.githubusercontent.com/gregvers/nginx-with-svc/main/nginx-with-svc.yaml
kubectl get pod -o wide
kubectl get svc -o wide
```

选择svc的Cluster IP非K8s网关的那台Work Node 上的Pod的Cluster IP，后续测试时会用到

![image-20230319234257377](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319234257377.png)

## 测试

在测试级上执行

```shell
curl 10.244.1.132
curl 10.96.191.0
```

如果成功，说明VCN中其他的子网是可以通过路由表规则直接访问K8s Flannel Pod叠加网络和 K8s Service网络：

![image-20230319234518100](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319234518100.png)

![image-20230319234729656](%E9%80%9A%E8%BF%87VCN%E8%B7%AF%E7%94%B1%E5%BF%AB%E6%8D%B7%E8%AE%BF%E9%97%AEFlannel%E7%BD%91%E7%BB%9C.assets/image-20230319234729656.png)

