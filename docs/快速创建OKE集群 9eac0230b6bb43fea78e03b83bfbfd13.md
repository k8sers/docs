# 快速创建OKE集群

[使用“快速创建”工作流程中的默认设置](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcreatingclusterusingoke_topic-Using_the_Console_to_create_a_Quick_Cluster_with_Default_Settings.htm#create-quick-cluster)根据需要创建具有新网络资源的集群。此方法是创建新集群的最快方法。如果您接受所有默认值，只需单击几下即可创建新集群。集群的新网络资源会自动创建，包括 Kubernetes API 端点、工作节点和负载均衡器的区域子网。负载均衡器的区域子网是公共的，但您可以指定 Kubernetes API 端点和工作线程节点的区域子网是公共的还是私有的。要在“快速创建”工作流程中创建集群，您必须属于一个组，该组的策略授予创建新网络资源所需的权限（请参阅[为组创建一个或多个附加策略](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengpolicyconfig.htm#policyforgroups)）

快速创建集群是非常适合新手的一个方案，因为它能自动配置所需的网络。强烈推荐新手或试用者试用这种方案。

需要注意的是，使用快速创建时，**节点所在子网应该为私有子网**，因为Pod默认跟Work Node的子网一致，而OKE不会为公共子网的Pod分配公网IP，导致Pod无法主动访问互联网（此时互联网通过LB Service访问Pod是没问题的）。 另外因为work node子网大小为/24, 只有254个IP可用，所以默认的网络配置可能导致Pod无法获取私网IP，甚至影响Node获得私网IP，所以快速创建的OKE作为**生产环境还需新建一个私有的Pod子网**。

![Untitled](Untitled%2045.png)

---

## **1. 授权**

以下为授权示例，你可以根据情况进行修改：

```
ALLOW any-user to use virtual-network-family in tenancy where request.principal.type = 'cluster'
Allow any-user to use private-ips in tenancy where request.principal.type = 'cluster'
ALLOW any-user to manage file-family in tenancy where request.principal.type = 'cluster'
```

<aside>
💡 如果网络在VCN与OKE不在同一区间，因OKE服务无权关联其他区间的资源，需要额外授权OKE拥有“分配私网IP”的权限，否则Worknode创建失败（部分Pod因无IP而启动失败）。

</aside>

## **2. 创建OKE集群**

![Untitled](Untitled%2046.png)

![Untitled](Untitled%2045.png)

注意前面提到的工作节点所在网络为专用子网，否则Pod无法主动访问互联网（也可以在创建好后重新调整Pod所在子网）。

![Untitled](Untitled%2047.png)

节点类型一般选AMD的Standard.E4.Flex或Intel的Standard3.Flex,  带有Flex的型号都支持灵活调整CPU及内存大小。镜像一般选默认的即可：

![Untitled](Untitled%2048.png)

强烈建议上传自己的SSH公钥（或保存自动生成的私钥），如果后续需要登录到work node上需要这个。如有需要可以指定启动盘的大小：

![Untitled](Untitled%2049.png)

在最后的复查页下方，有个是否创建基本集群的选项，选上后能省一点点费用，但无法管理附加组件（还记得吗，创建OKE的第一步我们已经管理过一次附加组件了）以及节点轮换功能，后续需要的时候可以再升级为增强型集群。基本集群适合开发、测试环境使用：

![Untitled](Untitled%2050.png)

点击创建，等待完成，完成后可以看到Kubernetes API Server 的端点地址：

![Untitled](Untitled%2051.png)

## **官方文档教程: 使用控制台在“快速创建”工作流程中创建具有默认设置的集群**

*了解如何使用“快速创建”工作流程，使用Kubernetes 容器引擎(OKE)创建具有默认设置和新网络资源的 Kubernetes 集群。*

要使用Kubernetes 容器引擎在“快速创建”工作流程中创建具有默认设置和新网络资源的集群：

1. 在控制台中，打开导航菜单并单击**开发人员服务**。在**Containers & Artifacts**下，单击**Kubernetes Clusters (OKE)**。
2. 选择您有权工作的**隔间。**
3. 在**集群列表**页面，单击**创建集群**。
4. 在**“创建集群”**对话框中，选择**“快速创建”**，然后单击**“提交”**。
5. 在**“创建集群”**页面上，要么仅接受新集群的默认配置详细信息，要么指定替代方案，如下所示：
    - **名称：**新集群的名称。接受默认名称或输入您选择的名称。避免输入机密信息。
    - **隔间：**用于创建新集群和关联网络资源的隔间。
    - **Kubernetes 版本：**在集群的控制平面节点和工作节点上运行的 Kubernetes 版本。接受默认版本或选择您选择的版本。除此之外，Kubernetes 版本决定了在创建的集群中打开的默认准入控制器集（请参阅[支持的准入控制器](https://docs.oracle.com/en-us/iaas/Content/ContEng/Reference/contengadmissioncontrollers.htm#Supported_Admission_Controllers)）。
    - **Kubernetes API 端点：**访问集群的 Kubernetes API 端点的类型。 Kubernetes API 端点可以是私有（可通过 VCN 中的其他子网访问）或公共（可直接从 Internet 访问）：
        - **私有端点：**创建私有区域子网，并且 Kubernetes API 端点托管在该子网中。 Kubernetes API 端点被分配了一个私有 IP 地址。
        - **公共端点：**创建公共区域子网，并且 Kubernetes API 端点托管在该子网中。 Kubernetes API 端点被分配了一个公共 IP 地址和一个私有 IP 地址。
        
        私有和公共端点被分配了一条安全规则（作为安全列表的一部分），该规则授予对 Kubernetes API 端点 (TCP/6443) 的访问权限。
        
        有关更多信息，请参阅[Kubernetes 集群控制平面和 Kubernetes API](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengclustersnodes.htm#processes)。
        
    - 节点类型：指定集群中第一个节点池中工作节点的类型（请参阅虚拟节点和受管节点）。选择以下选项之一：
        - **托管：**当您想要负责管理节点池中的工作节点时，请选择此选项。托管节点在租户中的计算实例（裸机或虚拟机）上运行。由于您负责管理受管节点，因此您可以灵活地配置它们以满足您的特定要求。您负责升级托管节点上的 Kubernetes 并管理集群容量。
        - **虚拟：**当您希望从“无服务器”Kubernetes 体验中受益时，请选择此选项。虚拟节点使您能够大规模运行 Kubernetes Pod，而无需升级数据平面基础设施和管理集群容量的运营开销。
        
        有关更多信息，请参阅[比较虚拟节点与受管节点](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengcomparingvirtualwithmanagednodes_topic.htm#contengusingvirtualormanagednodes_topic)。
        
6. 如果您选择**托管**作为**节点类型**：
    1. 指定受管节点详细信息：
        - **Kubernetes 工作节点：**对集群工作节点的访问类型。工作节点可以是私有（可通过其他 VCN 子网访问）或公共（可直接从 Internet 访问）：
            - **私有节点：**推荐。创建专用区域子网来托管工作节点。工作节点被分配一个私有IP地址。
            - **公共节点：**创建公共区域子网来托管工作人员节点。工作节点被分配一个公共IP地址和一个私有IP地址。
            
            请注意，无论您在此处如何选择，始终会创建公共区域子网来托管在“快速创建”工作流程中创建的集群中的负载均衡器。
            
        - **节点形状：**节点池中每个节点使用的形状。形状决定了分配给每个节点的 CPU 数量和内存量。如果选择灵活形状，则可以显式指定 CPU 数量和内存量。该列表仅显示您的租户中可用且受Kubernetes 容器引擎支持的形状。请参阅[工作节点支持的图像（包括自定义图像）和形状](https://docs.oracle.com/en-us/iaas/Content/ContEng/Reference/contengimagesshapes.htm#Supported_Images_Including_Custom_Images_and_Shapes_for_Worker_Nodes)。
        - **映像：**在受管节点池中的工作节点上使用的映像。映像是虚拟硬盘驱动器的模板，用于确定受管节点池的操作系统和其他软件。
            
            要更改默认图像，请单击**更改图像**。在**浏览所有图像**窗口中，选择**图像源**并选择图像，如下所示：
            
            - **OKE 工作节点镜像：**推荐。由 Oracle 提供并构建在平台映像之上。 OKE 映像经过优化，可用作工作节点的基础映像，并具有所有必要的配置和所需的软件。与平台映像和自定义映像相比，如果您希望最大限度地缩短运行时配置工作节点所需的时间，请选择 OKE 映像。
                
                OKE 镜像名称包含它们所包含的 Kubernetes 版本的版本号。请注意，如果您为节点池指定 Kubernetes 版本，则此处选择的 OKE 镜像必须与节点池的 Kubernetes 版本具有相同的版本号。
                
            - **平台镜像：**由Oracle提供，仅包含Oracle Linux操作系统。如果您希望Container Engine for Kubernetes在托管工作节点的计算实例首次启动时下载、安装和配置所需的软件，请选择平台映像。
            
            请参阅[工作节点支持的图像（包括自定义图像）和形状](https://docs.oracle.com/en-us/iaas/Content/ContEng/Reference/contengimagesshapes.htm#Supported_Images_Including_Custom_Images_and_Shapes_for_Worker_Nodes)。
            
        - **节点计数：** 要在节点池中创建的工作节点数量，放置在为集群创建的区域子网中。节点尽可能均匀地分布在区域中的可用性域中（或者在具有单个可用性域的区域的情况下，分布在该可用性域中的故障域中）。
    2. 接受高级集群选项的默认值，或者单击**显示高级选项**并指定替代方案，如下所示：
        - **启动卷**：配置工作节点启动卷的大小和加密选项：
            - 要指定启动卷的自定义大小，请选中**指定自定义启动卷大小**复选框。然后，输入 50 GB 到32 TB之间的自定义大小。指定的大小必须大于所选映像的默认启动卷大小。有关详细信息，请参阅[自定义启动卷大小](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/bootvolumes.htm#Custom)。如果增加启动卷大小，请扩展启动卷的分区以利用更大的大小（请参阅[扩展启动卷的分区](https://docs.oracle.com/en-us/iaas/Content/Block/Tasks/extendingbootpartition.htm#Extending_the_Partition_for_a_Boot_Volume)）。
            - 对于 VM 实例，您可以选择选中**使用传输中加密**复选框。对于支持传输中加密的[裸机实例](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/overview.htm#BlockVolumeEncryption__bm)，默认启用且不可配置。有关传输中加密的更多信息，请参阅[块卷加密](https://docs.oracle.com/en-us/iaas/Content/Block/Concepts/overview.htm#BlockVolumeEncryption)。如果您将自己的Vault服务加密密钥用于启动卷，则该密钥也可用于传输中加密。否则，将使用 Oracle 提供的加密密钥。
            - 默认情况下，启动卷已加密，但您可以选择使用自己的Vault服务加密密钥来加密该卷中的数据。要使用Vault服务来满您的加密需求，请选中“使用您管理的密钥加密此卷”复选框。选择包含要使用的主加密密钥的保管库隔间和保管库，然后选择主加密密钥隔间和主加密密钥。如果启用此选项，则此密钥将用于静态数据加密和传输中数据加密。
                
                > 重要信息
                > 
                > 
                > 块卷服务不支持使用使用 Rivest-Shamir-Adleman (RSA) 算法加密的密钥来加密卷。使用您自己的密钥时，您必须使用使用高级加密标准 (AES) 算法加密的密钥。这适用于块卷和启动卷。
                > 
            
            请注意，要使用您自己的Vault服务加密密钥来加密数据，IAM 策略必须授予对服务加密密钥的访问权限。请参阅[创建策略来访问用户管理的加密密钥以加密引导卷、块卷和/或文件系统](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengpolicyconfig.htm#contengpolicyconfig_topic_Create_Policies_for_User_Managed_Encryption)。
            
        - **在此集群上启用映像验证策略：（** 可选）是否仅允许部署来自Oracle Cloud Infrastructure Registry的已由特定主加密密钥签名的映像。指定加密密钥和包含它的保管库。请参阅[强制使用注册表中的签名图像](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengenforcingsignedimagesfromocir.htm#Enforcing_Use_of_Signed_Images_from_Registry)。
        - **公钥 SSH 密钥：（** 可选）要用于通过 SSH 访问节点池中每个节点的密钥对的公钥部分。公钥安装在集群中的所有工作节点上。请注意，如果您不指定 SSH 公钥，Kubernetes Container Engine将提供一个。但是，由于您没有相应的私钥，因此您将无法通过 SSH 访问工作节点。请注意，如果您指定希望集群中的工作线程节点托管在私有区域子网中，则无法使用 SSH 直接访问它们（请参阅使用[SSH 连接到私有子网中的受管节点](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengconnectingworkernodesusingssh.htm#connectprivatesubnets)）。
        - **Kubernetes 标签：（**可选）一个或多个标签（除了默认标签之外）添加到节点池中的工作节点，以实现在特定节点池中定位工作负载。例如，要从负载均衡器后端集中的后端服务器列表中排除节点池中的所有节点，请指定`node.kubernetes.io/exclude-from-external-load-balancers=true`（请参阅[node.kubernetes.io/exclude-from-external-load-balancers](https://docs.oracle.com/en-us/iaas/Content/ContEng/Reference/contengsupportedlabelsusecases.htm#exclude-from-external-load-balancers)）。
7. 如果您选择**虚拟**作为**节点类型**：
    1. 指定虚拟节点详细信息：
        - **节点计数：** 要在虚拟节点池中创建的虚拟节点的数量，放置在为集群创建的区域子网中。节点尽可能均匀地分布在区域中的可用性域中（或者在具有单个可用性域的区域的情况下，分布在该可用性域中的故障域中）。
        - **Pod 形状：**用于在虚拟节点池中的虚拟节点上运行的 Pod 的形状。形状决定了运行 Pod 的处理器类型。
            
            仅显示租户中可用且受Kubernetes 容器引擎支持的形状。请参阅[工作节点支持的图像（包括自定义图像）和形状](https://docs.oracle.com/en-us/iaas/Content/ContEng/Reference/contengimagesshapes.htm#Supported_Images_Including_Custom_Images_and_Shapes_for_Worker_Nodes)。
            
            请注意，您在 Pod 规范中明确指定虚拟节点的 CPU 和内存资源要求（请参阅Kubernetes 文档中[的为容器和 Pod 分配内存资源](https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/)和[为容器和 Pod 分配 CPU 资源）。](https://kubernetes.io/docs/tasks/configure-pod-container/assign-cpu-resource/)
            
    2. 接受高级集群选项的默认值，或者单击**显示高级选项**并指定替代方案，如下所示：
        - Kubernetes 标签和污点：（
            
            可选）通过向虚拟节点添加标签和污点来启用特定节点池的工作负载目标：
            
            - **标签：**添加到虚拟节点池中的虚拟节点的一个或多个标签（除了默认标签之外），以实现将工作负载定位到特定节点池。
            - **污点：**要添加到虚拟节点池中的虚拟节点的一个或多个污点。污点使虚拟节点能够排斥 pod，从而确保 pod 不会在特定虚拟节点池中的虚拟节点上运行。请注意，您只能将污点应用于虚拟节点。
            
            有关更多信息，请参阅Kubernetes 文档中的[将 Pod 分配给节点。](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/)
            
8. 单击**下一步**查看您为新集群输入的详细信息。
9. 如果您尚未选择任何增强集群功能，并且想要将新集群创建为基本集群而不是增强集群，请选择“**审核”**页面上的**“创建基本集群”**选项。请参阅[使用增强型集群和基本集群](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengworkingwithenhancedclusters.htm#contengworkingwithenhancedclusters)。
10. 单击**“创建集群”**立即创建新的网络资源和新集群。
    
    Container Engine for Kubernetes开始创建资源（如**创建集群和关联的网络资源**对话框所示）：
    
    - 网络资源（例如 VCN、互联网网关、NAT 网关、路由表、安全列表、工作节点的区域子网和负载均衡器的另一个区域子网），自动生成的名称格式如下`oke-<resource-type>-quick-<cluster-name>-<creation-date>`
    - 集群，具有您指定的名称
    - 节点池，名为 pool1
    - 工作节点，具有自动生成的名称（托管节点名称的格式为`oke-c<part-of-cluster-OCID>-n<part-of-node-pool-OCID>-s<part-of-subnet-OCID>-<slot>`，虚拟节点名称与节点的私有 IP 地址相同）
    
    请勿更改Container Engine for Kubernetes自动生成的资源名称。请注意，如果由于某种原因未能成功创建集群（例如，如果您没有足够的权限或超出了租户的集群限制），则在集群创建过程中创建的任何网络资源都不会自动删除。您必须手动删除任何此类未使用的网络资源。
    
    请注意，您可以稍后使用资源管理器和 Terraform创建新的网络资源和新集群，方法是单击**另存为堆栈**将资源定义保存为 Terraform 配置，而不是立即创建新的网络资源和新集群。有关从资源定义保存堆栈的更多信息，请参阅[从资源创建页面创建堆栈](https://docs.oracle.com/en-us/iaas/Content/ResourceManager/Tasks/create-stack-resource.htm#top)。
    
11. 单击**“关闭”**返回到控制台。

最初，新集群出现在控制台中，状态为“正在创建”。集群创建后，其状态为 Active。

Container Engine for Kubernetes还会创建一个 Kubernetes kubeconfig 配置文件，您可以使用该文件通过 kubectl 访问集群。