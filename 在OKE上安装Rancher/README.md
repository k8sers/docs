[返回OKE中文文档集](../README.md)

# 在OKE上安装Rancher

安装Rancher有多种SSL配置方式，本指南事前安装了NGINX的IngressController，并且使用的是自签名证书，

1. 创建自签名证书，示例中使用的域名是`learnoke.com`，请根据实际情况修改，

   ```
   openssl genrsa -des3 -passout pass:123456 -out ca.key 2048
   openssl rsa -in ca.key -passin pass:123456 -out ca.key
   openssl req -x509 -new -nodes -key ca.key -sha256 -days 3650 -out ca.crt -subj "/CN=learnoke.com"
   openssl genrsa -out tls.key 2048
   openssl req -new -key tls.key -out tls.csr -subj "/CN=*.learnoke.com"
   cat > server.ext <<EOF
   authorityKeyIdentifier=keyid,issuer
   basicConstraints=CA:FALSE
   keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
   subjectAltName = @alt_names
   
   [alt_names]
   DNS.1 = *.learnoke.com
   DNS.2 = *.server.learnoke.com
   EOF
   
   openssl x509 -req -in tls.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out tls.crt -days 3650 -extfile server.ext
   ```

2. 添加Helm库，

   ```
   helm repo add rancher-stable https://releases.rancher.com/server-charts/stable
   helm repo update
   ```

3. 创建命名空间

   ```
   kubectl create namespace cattle-system
   ```

4. 创建自签名证书的Secret，

   ```
   kubectl create secret generic tls-ca-additional --from-file=ca-additional.pem=ca.crt -n cattle-system
   kubectl create secret generic tls-ca --from-file=cacerts.pem=ca.crt -n cattle-system
   kubectl create secret tls tls-rancher-ingress --cert=tls.crt --key=tls.key -n cattle-system
   ```

5. 安装Rancher，

   ```
   helm install rancher rancher-stable/rancher \
     --namespace cattle-system \
     --set rancherImageTag=v2.6.9 \
     --set hostname=rancher.server.learnoke.com \
     --set bootstrapPassword=admin \
     --set ingress.ingressClassName=nginx \
     --set ingress.tls.source=secret \
     --set additionalTrustedCAs=true \
     --set privateCA=true
   ```

   输出结果示例，

   ````
   NAME: rancher
   LAST DEPLOYED: Wed Oct 26 15:26:54 2022
   NAMESPACE: cattle-system
   STATUS: deployed
   REVISION: 1
   TEST SUITE: None
   NOTES:
   Rancher Server has been installed.
   
   NOTE: Rancher may take several minutes to fully initialize. Please standby while Certificates are being issued, Containers are started and the Ingress rule comes up.
   
   Check out our docs at https://rancher.com/docs/
   
   If you provided your own bootstrap password during installation, browse to https://rancher.server.learnoke.com to get started.
   
   If this is the first time you installed Rancher, get started by running this command and clicking the URL it generates:
   
   ```
   echo https://rancher.server.learnoke.com/dashboard/?setup=$(kubectl get secret --namespace cattle-system bootstrap-secret -o go-template='{{.data.bootstrapPassword|base64decode}}')
   ```
   
   To get just the bootstrap password on its own, run:
   
   ```
   kubectl get secret --namespace cattle-system bootstrap-secret -o go-template='{{.data.bootstrapPassword|base64decode}}{{ "\n" }}'
   ```
   
   
   Happy Containering!
   ````

6. 验证Rancher是否成功部署，

   ```
   kubectl -n cattle-system rollout status deploy/rancher
   ```

   ```
   kubectl -n cattle-system get deploy rancher
   ```

7. Rancher的Ingress里面没有Path定义，导致NGINX的IngressController无法正常配置Rancher的Ingress，通过执行下面命令，追加Path定义，

   ```
   kubectl patch ingress rancher --type='json' -p='[{"op": "replace", "path": "/spec/rules/0/http/paths/0", "value": {"backend": {"service": {"name": "rancher", "port": {"number": 80}}}, "path": "/", "pathType": "ImplementationSpecific" }}]'
   ```

8. (Optional)如果Rancher是通过Nginx Ingress Controller进行公开的情况，需要在ingress里面追加以下配置，

   ```
   kubectl -n cattle-system edit ingress rancher
   
   ---在annotations里追加 
       nginx.org/location-snippets: |
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
   ---
   ```

9. (Optional)卸载Rancher，

   ```
   git clone https://github.com/rancher/rancher-cleanup.git; cd rancher-cleanup
   kubectl create -f deploy/rancher-cleanup.yaml
   ```

   监控卸载日志，

   ```
   kubectl -n kube-system logs -l job-name=cleanup-job -f
   ```

   

参考文档：

- [Install/Upgrade Rancher on a Kubernetes Cluster | Rancher Manager](https://docs.ranchermanager.rancher.io/pages-for-subheaders/install-upgrade-on-a-kubernetes-cluster)
- [Adding TLS Secrets | Rancher Manager](https://docs.ranchermanager.rancher.io/getting-started/installation-and-upgrade/resources/add-tls-secrets)
- [rancher/rancher-cleanup (github.com)](https://github.com/rancher/rancher-cleanup)



[返回OKE中文文档集](../README.md)