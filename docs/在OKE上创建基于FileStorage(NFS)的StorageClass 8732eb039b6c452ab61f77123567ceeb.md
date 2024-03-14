# 在OKE上创建基于FileStorage(NFS)的StorageClass

1. 在OCI上创建File Systems和设置VCN安全规则，参考文档，
    - [Creating File Systems (oracle.com)](https://docs.oracle.com/en-us/iaas/Content/File/Tasks/creatingfilesystems.htm)
    - [Configuring VCN Security Rules for File Storage (oracle.com)](https://docs.oracle.com/en-us/iaas/Content/File/Tasks/securitylistsfilestorage.htm#Configuring_VCN_Security_Rules_for_File_Storage)
2. 安装`nfs-subdir-external-provisioner`，请将nfs.server和nfs.path改为自己的环境信息。
    
    ```bash
    helm repo add nfs-subdir-external-provisioner https://kubernetes-sigs.github.io/nfs-subdir-external-provisioner/
    helm repo update
    ```
    
    ```bash
    kubectl create namespace nfs-provisioner
    helm install -n nfs-provisioner nfs-subdir-external-provisioner nfs-subdir-external-provisioner/nfs-subdir-external-provisioner \
        --set nfs.server=xxx.xxx.xxx.xxx \
        --set nfs.path=<YOUR_NFS_PATH>
    ```
    
    确认，
    
    ```bash
    kubectl get storageclass
    ```
    
3. (Optional)将`nfs-client`设置为默认StorageClass，
    
    ```bash
    kubectl patch storageclass oci -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
    kubectl patch storageclass oci -p '{"metadata": {"annotations":{"storageclass.beta.kubernetes.io/is-default-class":"false"}}}'
    kubectl patch storageclass oci-bv -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
    kubectl patch storageclass oci-bv -p '{"metadata": {"annotations":{"storageclass.beta.kubernetes.io/is-default-class":"false"}}}'
    kubectl patch storageclass nfs-client -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'
    kubectl patch storageclass nfs-client -p '{"metadata": {"annotations":{"storageclass.beta.kubernetes.io/is-default-class":"true"}}}'
    ```
    
    确认，
    
    ```bash
    kubectl get storageclass
    ```
    
    nfs-client是默认(default)的StorageClass，
    
    ![k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%2588%259B%25E5%25BB%25BA%25E5%259F%25BA%25E4%25BA%258EFileStorage(NFS)%25E7%259A%2584StorageClassimagesimage-20221026120111184.png](k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%2588%259B%25E5%25BB%25BA%25E5%259F%25BA%25E4%25BA%258EFileStorage(NFS)%25E7%259A%2584StorageClassimagesimage-20221026120111184.png)
    
    image-20221026120111184
    
4. (Optional)创建pvc和pod进行测试
    
    ```yaml
    cat <<EOF | kubectl apply -f -
    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: oke-fsspvc
    spec:
      storageClassName: "nfs-client"
      accessModes:
        - ReadWriteMany
      resources:
        requests:
          storage: 100Mi
    ---
    apiVersion: v1
    kind: Pod
    metadata:
      name: oke-fsspod
    spec:
      containers:
      - name: web
        image: nginx
        volumeMounts:
         - name: nfs
           mountPath: "/usr/share/nginx/html/"
        ports:
          - containerPort: 80
            name: http
      volumes:
      - name: nfs
        persistentVolumeClaim:
          claimName: oke-fsspvc
          readOnly: false
    EOF
    ```
    
    确认，
    
    ```bash
    kubectl get pv,pvc
    ```
    
    pv和pvc的状态都是Bound，
    
    ![k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%2588%259B%25E5%25BB%25BA%25E5%259F%25BA%25E4%25BA%258EFileStorage(NFS)%25E7%259A%2584StorageClassimagesimage-20221026120306417.png](k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%2588%259B%25E5%25BB%25BA%25E5%259F%25BA%25E4%25BA%258EFileStorage(NFS)%25E7%259A%2584StorageClassimagesimage-20221026120306417.png)
    
    image-20221026120306417
    
5. (Optional)卸载nfs-subdir-external-provisioner，
    
    ```bash
    helm uninstall -n nfs-provisioner nfs-subdir-external-provisioner
    ```
    

参考文档：

- [Creating File Systems (oracle.com)](https://docs.oracle.com/en-us/iaas/Content/File/Tasks/creatingfilesystems.htm)
- [Configuring VCN Security Rules for File Storage (oracle.com)](https://docs.oracle.com/en-us/iaas/Content/File/Tasks/securitylistsfilestorage.htm#Configuring_VCN_Security_Rules_for_File_Storage)