# OKE的不同LB安全策略注解效果测试

## 1. 注解

OKE LB的安全策略注解为

```yaml
service.beta.kubernetes.io/oci-load-balancer-security-list-management-mode: "All"
```

取值为：

- All: 默认值。 既添加LB入站策略，又添加Node策略
- Frontend: 只添加LB入站策略，不添加Node策略
- None: 既不添加LB入站策略，也不添加Node策略

其中Node的安全策略包括：

**kube-proxy health port**： **10256**

**health check port ranges**：使用默认的 NodePort range ：**30000-32768**

参考文档：https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengnetworkconfig.htm#securitylistconfig__security_rules_for_load_balancers

## 2. 基础环境

### 2.1 网络配置

VCN-Native 网络:

| Name | State | IPv4 CIDR Block | Subnet Access |
| --- | --- | --- | --- |
| https://cloud.oracle.com/networking/vcns/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/subnets/ocid1.subnet.oc1.ap-tokyo-1.aaaaaaaadhgidsdsqneqokx5txkyzxh3qcyt5b3wzfciv2dmhy5squna4skq | Available | 10.0.128.0/20 | Private (Regional) |
| https://cloud.oracle.com/networking/vcns/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/subnets/ocid1.subnet.oc1.ap-tokyo-1.aaaaaaaa7zsayca54jsxhygbvh2ilgf3duuq2wmi3mpvyrkggrq7ge22q4ka | Available | 10.0.20.0/24 | Public (Regional) |
| https://cloud.oracle.com/networking/vcns/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/subnets/ocid1.subnet.oc1.ap-tokyo-1.aaaaaaaajmckjdhmnf3lef2tpujmvbakkn4kzfb4fl5t5mn4pggphho77b7a | Available | 10.0.10.0/24 | Public (Regional) |
| https://cloud.oracle.com/networking/vcns/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/subnets/ocid1.subnet.oc1.ap-tokyo-1.aaaaaaaanefzrqqcuptubuno6ovvvirfvduavss5rlrgepx4kfrvt2msqbeq | Available | 10.0.0.0/28 | Public (Regional) |

K8s Api Security List - ingress:

| Stateless | Source | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 0.0.0.0/0 | TCP | All | 6443 |  | TCP traffic for ports: 6443 | External access to Kubernetes API
endpoint |  | Row with I.D. 0 |
| No | 10.0.10.0/24 | TCP | All | 6443 |  | TCP traffic for ports: 6443 | Kubernetes worker to Kubernetes API
endpoint communication |  | Row with I.D. 1 |
| No | 10.0.10.0/24 | TCP | All | 12250 |  | TCP traffic for ports: 12250 | Kubernetes worker to control plane
communication |  | Row with I.D. 2 |
| No | 10.0.128.0/20 | TCP | All | 6443 |  | TCP traffic for ports: 6443 |  |  | Row with I.D. 3 |
| No | 10.0.128.0/20 | TCP | All | 12250 |  | TCP traffic for ports: 12250 |  |  |  |

K8s Api Security List - egress:

| Stateless | Destination | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | https://cloud.oracle.com/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/security-lists/ocid1.securitylist.oc1.ap-tokyo-1.aaaaaaaaqxt7a7ztthlbjl5dffhfpii7a4cspgpt36clhhjfvkaksvppzpxa/egress-rules# | TCP | All | 443 |  | TCP traffic for ports: 443 HTTPS | Allow Kubernetes Control Plane to
communicate with OKE |  | Row with I.D. 0 |
| No | 10.0.10.0/24 | TCP | All | All |  | TCP traffic for ports: All | All traffic to worker nodes |  | Row with I.D. 1 |
| No | 10.0.128.0/20 | TCP | All | All |  | TCP traffic for ports: All |  |  |  |

Node Security List - ingress:

| Stateless | Source | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 10.0.10.0/24 | All Protocols |  |  |  | All traffic for all ports | Allow pods on one worker node to
communicate with pods on other worker nodes |  | Row with I.D. 0 |
| No | 10.0.0.0/24 | TCP | All | All |  | TCP traffic for ports: All | TCP access from Kubernetes Control
Plane |  | Row with I.D. 1 |
| No | 0.0.0.0/0 | TCP | All | 22 |  | TCP traffic for ports: 22 SSH Remote Login
Protocol | Inbound SSH traffic to worker nodes |  | Row with I.D. 2 |
| No | 0.0.0.0/0 | TCP | All | 81 |  | TCP traffic for ports: 81 |  |  | Row with I.D. 3 |
| No | 10.0.128.0/20 | All Protocols |  |  |  | All traffic for all ports |  |  | Row with I.D. 4 |

Node Security List - egress:

| Stateless | Destination | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 10.0.10.0/24 | All Protocols |  |  |  | All traffic for all ports | Allow pods on one worker node to
communicate with pods on other worker nodes |  | Row with I.D. 0 |
| No | 10.0.0.0/24 | TCP | All | 6443 |  | TCP traffic for ports: 6443 | Access to Kubernetes API Endpoint |  | Row with I.D. 1 |
| No | 10.0.0.0/24 | TCP | All | 12250 |  | TCP traffic for ports: 12250 | Kubernetes worker to control plane
communication |  | Row with I.D. 2 |
| No | https://cloud.oracle.com/ocid1.vcn.oc1.ap-tokyo-1.amaaaaaaak7gbriadt7roaob4ilfn6b6d73lo3evjpoknbowflzarrzn345q/security-lists/ocid1.securitylist.oc1.ap-tokyo-1.aaaaaaaahtvmrummqzzmlenykhr5zhjxkh3ubhryqc3lth5q73yueenencoa/egress-rules# | TCP | All | 443 |  | TCP traffic for ports: 443 HTTPS | Allow nodes to communicate with OKE to
ensure correct start-up and continued functioning |  | Row with I.D. 3 |
| No | 0.0.0.0/0 | TCP | All | All |  | TCP traffic for ports: All | Worker Nodes access to Internet |  | Row with I.D. 4 |
| No | 10.0.128.0/20 | All Protocols |  |  |  | All traffic for all ports |  |  | Row with I.D. 5 |
| No | 0.0.0.0/0 | UDP | All | All |  | UDP traffic for ports: All |  |  | Row with I.D. 6 |

SvcLB Security List Ingress和Egress 均为空

### 2.2 待测应用

当前有一个nginx的业务负载

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 8
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 80
```

## 3. 测试

### 3.1 创建security-list-management-mode: “None”类型的LB

```yaml
kind: Service
apiVersion: v1
metadata:
  name: nginx-service-none
  annotations:
    oci.oraclecloud.com/load-balancer-type: "lb"
    service.beta.kubernetes.io/oci-load-balancer-security-list-management-mode: "None"
spec:
  selector:
    app: nginx
  type: LoadBalancer
  ports:
  - name: http
    port: 92
    targetPort: 80
```

```
NAME                 TYPE           CLUSTER-IP    EXTERNAL-IP       PORT(S)        AGE     SELECTOR
kubernetes           ClusterIP      10.96.0.1     <none>            443/TCP        5m53s   <none>
nginx-service-none   LoadBalancer   10.96.68.44   141.147.187.195   92:30924/TCP   67s     app=nginx
```

创建后SvcLB Security List 的还是空， Node Security List没变， 还是5条
Ingress策略， 7条Egress策略 。

进入LB backendSet会发现Node的状态是异常的。

访问141.147.187.195:92 也是失败的。

### 3.2 创建security-list-management-mode: “Frontend”类型的LB

```yaml
kind: Service
apiVersion: v1
metadata:
  name: nginx-service-frontend
  annotations:
    oci.oraclecloud.com/load-balancer-type: "lb"
    service.beta.kubernetes.io/oci-load-balancer-security-list-management-mode: "Frontend"
spec:
  selector:
    app: nginx
  type: LoadBalancer
  ports:
  - name: http
    port: 91
    targetPort: 80
```

```
NAME                     TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)        AGE     SELECTOR
kubernetes               ClusterIP      10.96.0.1       <none>            443/TCP        13m     <none>
nginx-service-frontend   LoadBalancer   10.96.182.248   141.147.182.198   91:30601/TCP   52s     app=nginx
nginx-service-none       LoadBalancer   10.96.68.44     141.147.187.195   92:30924/TCP   9m12s   app=nginx
```

创建后SvcLB Security List 多了一条 91的Ingress规则，其他没变

| Stateless | Source | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 0.0.0.0/0 | TCP | All | 91 |  | TCP traffic for ports: 91 |  |  |  |

进入LB backendSet会发现Node的状态还是异常的。

访问 141.147.182.198:91失败。

### 3.3 创建security-list-management-mode: “All”类型的LB

```yaml
kind: Service
apiVersion: v1
metadata:
  name: nginx-service-frontend
  annotations:
    oci.oraclecloud.com/load-balancer-type: "lb"
    service.beta.kubernetes.io/oci-load-balancer-security-list-management-mode: "All"
spec:
  selector:
    app: nginx
  type: LoadBalancer
  ports:
  - name: http
    port: 90
    targetPort: 80
```

```
NAME                     TYPE           CLUSTER-IP      EXTERNAL-IP       PORT(S)        AGE     SELECTOR
kubernetes               ClusterIP      10.96.0.1       <none>            443/TCP        21m     <none>
nginx-service            LoadBalancer   10.96.67.142    168.138.220.36    90:31592/TCP   28s     app=nginx
nginx-service-frontend   LoadBalancer   10.96.182.248   141.147.182.198   91:30601/TCP   8m15s   app=nginx
nginx-service-none       LoadBalancer   10.96.68.44     141.147.187.195   92:30924/TCP   16m     app=nginx
```

创建后SvcLB Security List 多了一条 91的Ingress规则，其他没变

| Stateless | Source | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 0.0.0.0/0 | TCP | All | 90 |  | TCP traffic for ports: 90 |  |  |  |

Node Security List 的Ingress多了2条规则：

| Stateless | Source | IP Protocol | Source Port Range | Destination Port Range | Type and Code | Allows | Description | Actions | Row header |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No | 10.0.20.0/24 | TCP | All | 31592 |  | TCP traffic for ports: 31592 |  |  |  |
| No | 10.0.20.0/24 | TCP | All | 10256 |  | TCP traffic for ports: 10256 |  |  |  |

此时，All对应的LB的BackendSet中Node状态是正常的，连带之前2个LB的BackendSet状态也正常了。

最终访问 168.138.220.36:90 成功