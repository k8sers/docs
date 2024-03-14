# 在OKE上安装Ingress-NGINX

## 授权

因为要生成LB服务，所以给这个组件授权，注意`—user=`后面跟着你的用户或指定用户的OCID：

```
kubectl create clusterrolebinding jdoe_clst_adm --clusterrole=cluster-admin --user=ocid1.user.oc1..aaaaa...zutq
```

## 创建Ingress

注意选择与OKE（K8s）对应的版本，具体信息请看参考资料。

```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.4.0/deploy/static/provider/cloud/deploy.yaml
```

## 内网Ingress

关联内网LB需要在deploy.yaml的323行增加内网LB注释，不同版本位置可能有差别。

```yaml
annotations:
    oci.oraclecloud.com/load-balancer-type: "lb"
    service.beta.kubernetes.io/oci-load-balancer-internal: "true"
```

## **在K8s中使用Ingress**

如果有多个Ingress，通过Ingress Class来指定所使用的Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kuboard-ingress
  namespace: kuboard
  annotations:
    kubernetes.io/ingress.class: "nginx"
spec:
  ingressClassName: nginx
  rules:
  - host: kuboard.wilbur.com
    http:
      paths:
      - backend:
          service:
            name: kuboard-v3
            port:
              number: 80
        path: /
        pathType: Prefix
```

## 参考资料

LB配置参数：[https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer_topic-Summaryofannotations.htm](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingloadbalancer_topic-Summaryofannotations.htm)

K8s ingress-nginx的仓库：[https://github.com/kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx)

在上面的仓库中可以看到ingress版本和K8s（OKE）版本的对应关系。

![Untitled](Untitled%203.png)