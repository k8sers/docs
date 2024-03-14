# Kubernetes Workload Identity

提供精细的企业级标识和访问管理控制。它还允许您使用 OCI 身份和访问管理 （IAM） 授予 Kubernetes Pod 对 Oracle 云基础设施 （OCI） 资源的策略驱动访问权限。

当应用程序需要访问 OCI 资源时，工作负载身份使您能够编写范围限定为与应用程序 Pod 关联的 Kubernetes 服务帐户的 OCI IAM 策略。此功能使在这些容器中运行的应用程序能够根据策略提供的权限直接访问 OCI API。OCI 审核服务还会自动跟踪 Kubernetes 工作负载从您的集群进行的所有 API 调用。

![Untitled](Untitled%2079.png)

---

## 创建K8s账号

先在K8s中创建一个账号：

```bash
kubectl create namespace <namespace-name>
kubectl create serviceaccount **<service-account-name>** --namespace <namespace-name>
```

## 授权

因为要授权K8s账号调用OCI的API接口，所以需要云策略来授权：

![Untitled](Untitled%2080.png)

![Untitled](Untitled%2081.png)

```bash
# 请把下面的Policy内容缩成一行
Allow **any-user** to <verb> <resource> in <location> **where** all {
request.principal.type = 'workload',
request.principal.namespace = '<namespace-name>',
**request.principal.service_account** = '**<service-account-name>**',
request.principal.cluster_id = '<cluster-ocid>'}
```

## 使用Workload Identity

应用下面的nginx.yaml文件后，这个Pod就拥有了

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  serviceAccountName: **<service-account-name>**     
  automountServiceAccountToken: true
  containers:
   - name: nginx
     image: nginx:1.14.2
     ports:
      - containerPort: 80
```