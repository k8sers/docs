# 在OKE中安装Apache APISIX

Apache APISIX 是一个动态、实时、高性能的云原生 API 网关，提供了负载均衡、动态上游、灰度发布、服务熔断、身份认证、可观测性等丰富的流量管理功能。

它构建于 NGINX + ngx_lua 的技术基础之上，充分利用了 LuaJIT 所提供的强大性能。 

![Untitled](Untitled%204.png)

## 默认安装命令

```
helm repo add apisix https://charts.apiseven.com
helm repo update
helm install apisix-aiot-us-sqa apisix/apisix --namespace apisix-eu-qa --set etcd.enabled=false --set apisix.kind=DaemonSet --create-namespace
helm install zh-test-apisix apisix/apisix --namespace ingress-apisix --create-namespace
```

## 定制安装

有时候我们需要修改LB的一些属性，比如LB类型、带宽大小等。

这时候我们修改安装参数:

```
helm pull apisix/apisix
tar xzcf apisix-1.3.1.tgz
vim apisix/values.yam
```

修改values.yaml第227~229行，你可以通过K8s注解添加各种各样的参数（详情见[https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer_topic-Summaryofannotations.htm](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer_topic-Summaryofannotations.htm)）:

```yaml
  type: LoadBalancer
  annotations:
    oci.oraclecloud.com/load-balancer-type: "nlb"
```

修改后安装

```bash
helm install apisix ./apisix
```

查看地址

```bash
  export NODE_PORT=$(kubectl get --namespace apisix-eu-qa -o jsonpath="{.spec.ports[0].nodePort}" services apisix-aiot-us-sqa-gateway)
  export NODE_IP=$(kubectl get nodes --namespace apisix-eu-qa -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
```

1. Get the application URL by running these commands:

```bash
export NODE_PORT=$(kubectl get --namespace apisix-eu-qa -o jsonpath="{.spec.ports[0].nodePort}" services apisix-aiot-us-sqa-gateway)
export NODE_IP=$(kubectl get nodes --namespace apisix-eu-qa -o jsonpath="{.items[0].status.addresses[0].address}")
echo http://$NODE_IP:$NODE_PORT
```