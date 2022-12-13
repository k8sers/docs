[返回OKE中文文档集](../README.md)

# 在OKE上最小化安装KubeSphere

除了在Linux机器上安装KubeSphere之外，您还可以将其直接部署在现有的OKE集群上。本指南将引导您完成在OKE上最小化安装KubeSphere的一般性步骤。

1. 执行以下命令开始安装，以v3.3.0版本为例：

   ```
   kubectl apply -f https://github.com/kubesphere/ks-installer/releases/download/v3.3.0/kubesphere-installer.yaml
   wget https://github.com/kubesphere/ks-installer/releases/download/v3.3.0/cluster-configuration.yaml
   sed -i 's/type: NodePort/type: LoadBalancer/g' cluster-configuration.yaml
   kubectl apply -f cluster-configuration.yaml
   ```

2. 检查安装日志：

   ```
   kubectl logs -n kubesphere-system $(kubectl get pod -n kubesphere-system -l 'app in (ks-install, ks-installer)' -o jsonpath='{.items[0].metadata.name}') -f
   ```

3. 使用 `kubectl get pod --all-namespaces` 查看所有Pod是否在KubeSphere的相关命名空间中正常运行。如果是，请通过以下命令获取LoadBalancer的IP：

   ```
   kubectl get svc/ks-console -n kubesphere-system
   ```

4. 通过LoadBalancer的IP使用默认帐户和密码 `(admin/P@88w0rd)` 访问Web控制台。为了安全起见，请及时修改默认的密码。

5. 登录控制台后，您可以在**系统组件**中检查不同组件的状态。如果要使用相关服务，可能需要等待某些组件启动并运行。

6. (Optional)卸载KubeSphere，您可以使用 [kubesphere-delete.sh](https://github.com/kubesphere/ks-installer/blob/release-3.1/scripts/kubesphere-delete.sh) 将KubeSphere从您现有的OKE集群中卸载。复制[GitHub 源文件](https://raw.githubusercontent.com/kubesphere/ks-installer/release-3.1/scripts/kubesphere-delete.sh)并在本地机器上执行此脚本。

   ```
   wget https://raw.githubusercontent.com/kubesphere/ks-installer/release-3.1/scripts/kubesphere-delete.sh
   bash kubesphere-delete.sh
   ```

   



参考文档：

- [在 Oracle OKE 上部署 KubeSphere](https://kubesphere.io/zh/docs/v3.3/installing-on-kubernetes/hosted-kubernetes/install-kubesphere-on-oke/)

- [从 Kubernetes 上卸载 KubeSphere](https://kubesphere.io/zh/docs/v3.3/installing-on-kubernetes/uninstall-kubesphere-from-k8s/)



[返回OKE中文文档集](../README.md)