# 通过K8s Cluster API创建和管理OKE集群

[适用于 Oracle 云基础设施 (CAPOCI) 的 Cluster API Provider](https://oracle.github.io/cluster-api-provider-oci/) 于 2022 年发布，允许用户在 Oracle 云基础设施 (OCI) 中部署自我管理的 Kubernetes 集群。本文介绍 Cluster API 和 CAPOCI。虽然自我管理的 Kubernetes 集群可能适合某些用例，但许多客户更喜欢使用 OCI 管理的 Kubernetes 解决方案，即 Oracle Container Engine for Kubernetes (OKE)。OKE 提供了完全托管的 Kubernetes 控制平面和 OCI 身份集成等优势，但客户仍然希望获得 Cluster API 提供的优势。

我们很高兴地宣布 CAPOCI 通过[v0.7.0](https://github.com/oracle/cluster-api-provider-oci/releases/tag/v0.7.0)版本开始支持 OKE。

来源：[英文版官方博文](https://blogs.oracle.com/cloud-infrastructure/post/create-manage-oke-clusters-api)

 Cluster API 是K8s官方定义的接口，用于创建新的集群（由K8s创建另一个K8s），不同于常规的通过登录云服务商的网页手工创建的方式。

这是一种高级的创建方式，普通的用户无需关心。市面上还没有一个比较完善的跨云管理K8s产品使用这个工具，若只通过原生K8s工具命令来创建，实际体验不如直接使用云服务商网页创建和管理。 只推荐有开发跨云运维平台的团队使用，甲骨文中国支持团队也欢迎开放的跨云SaaS平台/工具与我们合作。

[https://blogs.oracle.com/content/published/api/v1.1/assets/CONT1145630014CA4FC0B408D805E31B3000/Medium?cb=_cache_ae49&channelToken=f7814d202b7d468686f50574164024ec&format=jpg](https://blogs.oracle.com/content/published/api/v1.1/assets/CONT1145630014CA4FC0B408D805E31B3000/Medium?cb=_cache_ae49&channelToken=f7814d202b7d468686f50574164024ec&format=jpg)

## **使用Cluster API部署OKE集群的好处**

集群 API 消除了设置、配置和管理 Kubernetes 集群的复杂性，使您能够跨多个云提供商、本地和边缘基础设施以声明式和编程方式执行这些任务。它使您能够自动化该过程，从而简化了活动集群和备用集群的配置。此设置降低了配置漂移的风险，从而更容易一致地监视和管理集群。

Cluster API 还与一组标准化工具包集成，包括[Fluxcd](https://fluxcd.io/)。这种标准化确保了一致性并简化了使用这些工具来管理 Kubernetes 集群的管理。

## **使用CAPOCI部署OKE集群**

Cluster API 通常安装在管理多个 Kubernetes 集群的管理集群上。在本博客中，我们使用[kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)来管理集群。当管理集群设置完毕并在其上部署CAPOCI后，我们可以继续使用CAPOCI部署OKE集群。

### **先决条件**

- 笔记本电脑或 OCI 虚拟机 (VM) 上基于 Linux 的终端窗口
- [Docker](https://docs.docker.com/engine/install/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [clusterctl](https://cluster-api.sigs.k8s.io/user/quick-start.html#install-clusterctl)

在终端中部署以下命令。

### **部署kind集群**

```bash
kind create cluster
```

### **导出 OCI 用户主体凭据**

```bash
export OCI_TENANCY_ID=
export OCI_USER_ID=
export OCI_CREDENTIALS_FINGERPRINT=
export OCI_REGION=
# if Passphrase is present
export OCI_CREDENTIALS_PASSPHRASE=
export OCI_CREDENTIALS_KEY_B64=$(base64 <  | tr -d '\n')

# the following lines of code can be copy pasted as it is
export OCI_TENANCY_ID_B64="$(echo -n "$OCI_TENANCY_ID" | base64 | tr -d '\n')"
export OCI_CREDENTIALS_FINGERPRINT_B64="$(echo -n "$OCI_CREDENTIALS_FINGERPRINT" | base64 | tr -d '\n')"
export OCI_USER_ID_B64="$(echo -n "$OCI_USER_ID" | base64 | tr -d '\n')"
export OCI_REGION_B64="$(echo -n "$OCI_REGION" | base64 | tr -d '\n')"
export OCI_CREDENTIALS_PASSPHRASE_B64="$(echo -n "$OCI_CREDENTIALS_PASSPHRASE" | base64 | tr -d '\n')"

```

### **安装 CAPI 和 CAPOCI**

```bash
EXP_MACHINE_POOL=true EXP_OKE=true clusterctl init  --infrastructure oci
```

### **部署OKE集群**

```bash
NODE_MACHINE_COUNT=1 OCI_COMPARTMENT_ID= OCI_SSH_KEY="" clusterctl generate cluster oke-cluster-1 --kubernetes-version v1.25.4 --flavor managed| kubectl apply -f -
```

### **监控创建的集群**

```bash
$ kubectl get clusters -A
NAMESPACE   NAME            PHASE         AGE   VERSION
default     oke-cluster-1   Provisioned   43m
$ kubectl get machinepool -A
NAMESPACE   NAME                 CLUSTER         REPLICAS   PHASE     AGE   VERSION
default     oke-cluster-1-mp-0   oke-cluster-1   1          Running   43m   v1.25.4
```

## **在多个 OCI 区域部署和监控 OKE 集群**

使用 CAPOCI 的优势之一是能够在多个 OCI 区域部署和监控 OKE 集群。以下屏幕截图演示了此功能。我们已在 OCI 的 us-ashburn-1 和 us-phoenix-1 公共云区域中部署了 OKE 集群，并通过单个管理集群来管理和监控它们。

您还可以扩展此方法来监控跨多个云提供商运行的集群。

```bash
$ kubectl get clusters -A
NAMESPACE   NAME          PHASE         AGE   VERSION
default     iad-cluster   Provisioned   14d
default     phx-cluster   Provisioned   14d
```

## **结论**

CAPOCI 团队一直在逐步发布产品更新，加上 OKE 支持使其可供更广泛的用户使用。我们鼓励您尝试新功能并分享您的任何反馈。CAPOCI 团队可以在 Kubernetes Slack 频道 #cluster-api-oci 上找到。

最后，我们要向 Cluster API 社区表示感谢。我们与社区密切合作来验证我们的提案，他们的支持对于帮助我们实现目标非常宝贵。

有关更多信息，请参阅以下资源：

- [集群API文档](https://cluster-api.sigs.k8s.io/user/quick-start.html)
- [CAPOCI 文档](http://oracle.github.io/cluster-api-provider-oci/)