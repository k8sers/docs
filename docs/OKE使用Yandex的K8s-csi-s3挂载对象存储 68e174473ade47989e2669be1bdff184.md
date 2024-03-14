# OKE使用Yandex的K8s-csi-s3挂载对象存储

## 使用CSI 支持 s3

使用 CSI for S3 开源插件, 将OCI OSS 通过S3兼容协议, 安装CSI driver,声明pvc 挂载到pod 上. https://github.com/yandex-cloud/k8s-csi-s3

## 1. Github 下载 k8s-csi-s3源代码

https://github.com/yandex-cloud/k8s-csi-s3

## 2.安装CSI S3 驱动到集群中

### 2.1 准备 OCI Object兼容AWS 兼容API 配置信息

2.1.1 获取tenancy ID ocichina001

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131121541590.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131121541590.png)

2.1.2 配置compartment

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180017744.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180017744.png)

2.1.3 生成 accessKeyID / secretAccessKey

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180429914.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180429914.png)

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180528374.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180528374.png)

生成 access id 和 access Key,
保存生存的文本,备用. 类似下面生成的key.

```
Access Key： ****ce537e8
Secret Key：9yBG446X******Hvcd+Lh/c=
```

## 2.2 安装k8s CSI S3 驱动到OKE集群中

2.2.1编辑 k8s-csi-s3 配置文件

```
helm repo add yandex-s3 https://yandex-cloud.github.io/k8s-csi-s3/charts
helm install csi-s3 yandex-s3/csi-s3
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180729337.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180729337.png)

OCI Object Storage 兼容AWS S3 API
配置参考下面链接
https://docs.oracle.com/en-us/iaas/Content/Object/Tasks/s3compatibleapi.htm

2.2.2 生成 secret

```
#进入github 上下载的文件目录
kubectl create -f examples/secret.yaml
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180805853.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180805853.png)

2.2.3 发布驱动

```
kubectl create -f provisioner.yaml
kubectl create -f driver.yaml
kubectl create -f csi-s3.yaml
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180959791.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131180959791.png)

image-20240131180959791

2.2.4创建 storage class

```
kubectl create -f examples/storageclass.yaml
```

2.2.5测试s3驱动 1.用新创建的storage class 创建pvc

```
kubectl create -f examples/pvc.yaml
```

2.查看pvc的绑定情况

```
kubectl get pvc csi-s3-pvc
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131181123341.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131181123341.png)

3.创建测试Pod

```
kubectl create -f examples/pod.yaml
kubectl exec -ti csi-s3-test-nginx bash
mount | grep fuse
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131181209345.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsimage-20240131181209345.png)

OCI OSS的S3秘钥

```yaml
apiVersion: v1
kind: Secret
metadata:
  namespace: kube-system
  name: csi-s3-secret
stringData:
  accessKeyID:  30*******c4e181
  secretAccessKey: Xd*******HLlgr0=
  endpoint: https://bmdyuvgpezgz.compat.objectstorage.ap-mumbai-1.oraclecloud.com
```

```yaml
# Statically provisioned PVC:
# An existing bucket or path inside bucket manually created
# by the administrator beforehand will be bound to the PVC,
# and it won't be removed when you remove the PV
apiVersion: v1
kind: PersistentVolume
metadata:
  name: manualbucket-with-path
spec:
  storageClassName: csi-s3
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  claimRef:
    namespace: default
    name: csi-s3-manual-pvc
  csi:
    driver: ru.yandex.s3.csi
    controllerPublishSecretRef:
      name: csi-s3-secret
      namespace: kube-system
    nodePublishSecretRef:
      name: csi-s3-secret
      namespace: kube-system
    nodeStageSecretRef:
      name: csi-s3-secret
      namespace: kube-system
    volumeAttributes:
      capacity: 10Gi
      mounter: s3fs
      # path : /ind-dump/dcr
      # options: --memory-limit 1000 --dir-mode 0777 --file-mode 0666
    volumeHandle: cnfs-oss-ind-paas-k8s
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: csi-s3-manual-pvc
spec:
  # Empty storage class disables dynamic provisioning
  storageClassName: ""
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

应用Demo：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: csi-s3-test-nginx-manual
  namespace: default
spec:
  containers:
   - name: csi-s3-test-nginx
     image: nginx
     volumeMounts:
       - mountPath: /usr/share/nginx/html/s3
         name: webroot
  volumes:
   - name: webroot
     persistentVolumeClaim:
       claimName: csi-s3-manual-pvc
       readOnly: false

```

## 已知 Bugs：只能用于OCI Home Region

已向作者提交了issue：https://github.com/yandex-cloud/k8s-csi-s3/issues/87

代码位置：https://github.com/yandex-cloud/k8s-csi-s3/blob/2f4814a07dd6da9fd5571222a6a06e23f81980bf/pkg/s3/client.go#L57

缺少下面这行：

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsde68077aa00c84ec2ebf4278cfbef24.jpg](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2OKE_%25E4%25B8%25AD%25E4%25BD%25BF%25E7%2594%25A8-_OCI_OSS_%25E5%25AF%25B9%25E8%25B1%25A1%25E5%25AD%2598%25E5%2582%25A82.assetsde68077aa00c84ec2ebf4278cfbef24.jpg)