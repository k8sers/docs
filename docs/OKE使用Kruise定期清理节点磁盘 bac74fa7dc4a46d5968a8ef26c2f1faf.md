# OKE使用Kruise定期清理节点磁盘

节点磁盘存储可用空间在 Kubernetes原生体系中基本上处于一种单调递减的宿命，过大的磁盘压力可能导致该节点无法调度，甚至导致节点上的Pod 被驱逐等等一系列副作用，影响集群的稳定性。

相比于普通K8s Job不确定在什么node上运行，Kruise可以使用BroadcastJob + Advanced CronJob定期在每一台Worker Node上执行Job（运行清理磁盘的脚本），删除Pod的历史日志及不被运行的容器镜像。

前置任务：

[登录OCIR](%E7%99%BB%E5%BD%95OCIR%202cf9469d936a4bc188659bfcf915a210.md)

![Untitled](Untitled%2083.png)

---

## 1. 安装Kruise

使用helm进行安装

```
helm repo add openkruise https://openkruise.github.io/charts/
helm install kruise openkruise/kruise --version 1.5.1
```

检查安装结果

```
kubectl get pod -o wide -n kruise-system
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102202530977.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102202530977.png)

image-20240102202530977

## 2. 定期删除日志

新建或编辑 log-cleaner.yaml:

```yaml
apiVersion: apps.kruise.io/v1alpha1kind: AdvancedCronJobmetadata:  name: log-cleaner-jobspec:  schedule: "0 1 * * *"  template:    broadcastJobTemplate:      spec:        template:          spec:            containers:              - name: log-cleaner                image: alpine                imagePullPolicy: IfNotPresent                command: ["/bin/sh", "-c", "for log in $(find /var/log/pods -name *.log.*); do echo \"delete logs : $log\";  rm -rf $log; done"]                volumeMounts:                - name: podlog                  mountPath: /var/log/pods            volumes:            - name: podlog              hostPath:                path: /var/log/pods            restartPolicy: OnFailure        completionPolicy:          type: Always          ttlSecondsAfterFinished: 90        failurePolicy:          type: FailFast          restartLimit: 3
```

应用：

```
kubectl apply -f log-cleaner.yaml
```

登录到node上看看效果(前提需要配置好私钥~/.ssh/id_rsa)

```
ssh opc@10.0.10.106
find /var/log/pods -name *.log.*
```

## 3. 定期清理镜像

### 3.1 创建镜像仓库的登录密码

进入账户，创建一个认证令牌（如果已经创建过，可以复用现有的）

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210155612.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210155612.png)

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210412135.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210412135.png)

点击生成后，一定要记下密码：

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210513423.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102210513423.png)

### 3.2 新建镜像仓库（如有自己的仓库则可跳过本小节）

打开容器镜像仓库

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102205348736.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102205348736.png)

新建一个image-cleaner仓库:

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102205736783.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102205736783.png)

页面上被红色框住3个信息构成了登录仓库所需的信息：

```bash
docker login <region-key>.ocir.io
# 用户名 <tenancy-namespace>/<username>
# 密码
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102211337600.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102211337600.png)

### 3.3 创建镜像

下载cri-o最新客户端到本地， 后续用到:

```bash
wget https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.29.0/crictl-v1.29.0-linux-amd64.tar.gz
```

创建清理脚本 image-cleaner.sh ：

```bash
#!/bin/sh

echo "container runtime endpoint:" $CONTAINER_RUNTIME_ENDPOINT

# clean up docker resources if have
crictl ps > /dev/null
if [ $? -eq 0 ]
then
    # Implement your customized script here, such as
    # get the images that is used, these images cannot be deleted
    # crictl ps | awk '{if(NR>1){print $2}}' > used-images.txt
    crictl ps | awk '{if(NR>1){print $1}}'  | xargs crictl inspect | jq '."info"."runtimeSpec"."annotations"."io.kubernetes.cri-o.ImageRef"'  | awk '{print substr($0,2,13)}' > used-images.txt
    # @@ You can choose the images you want to clean according to your requirement @@
    # **      Here, we will clean all images from my docker.io/grafana repo!       **
    crictl images | grep -i "docker.io/grafana"| awk '{print $3}' > target-images.txt

    # filter out the used images and delete these unused images
    sort target-images.txt used-images.txt used-images.txt| uniq -u | xargs -r crictl rmi
else
    echo "crictl does not exist"
fi

exit 0
```

创建 Dockerfile：

```docker
FROM alpine
COPY crictl-v1.23.0-linux-amd64.tar.gz ./
RUN  tar zxvf crictl-v1.29.0-linux-amd64.tar.gz -C /bin && rm crictl-v1.29.0-linux-amd64.tar.gz
COPY image-cleaner.sh /bin/cleaner.sh
RUN chmod +x /bin/cleaner.sh
CMD ["/bin/sh", "/bin/cleaner.sh"]
```

编译镜像并上传到上一步骤中新建的镜像仓库中，仓库地址规则是

```bash
# 地址规则 <region-key>.ocir.io/<tenancy-namespace>/<repo-name>:<version>
docker build . -t bom.ocir.io/<你的租户名>/image-cleaner:v1 && docker push bom.ocir.io/<你的租户名>/image-cleaner:v1
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102212807912.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102212807912.png)

### 3.4 发布

先看看之前的镜像信息(前提需要配置好私钥~/.ssh/id_rsa)

```
ssh opc@10.0.10.106
sudo crictl pull grafana/mimir
sudo crictl images | grep -i "docker.io/grafana"
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102232100173.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102232100173.png)

新建或编辑 image-cleaner.yaml:

```yaml
apiVersion: apps.kruise.io/v1alpha1
kind: AdvancedCronJob
metadata:
  name: acj-test
spec:
  schedule: "30 1 * * *"
  startingDeadlineSeconds: 60
  template:
    broadcastJobTemplate:
      spec:
        template:
          spec:
            containers:
              - name: node-cleaner
                image: bom.ocir.io/bm0ik50fxnm7/image-cleaner:v1
                imagePullPolicy: IfNotPresent
                env:
                # crictl use this env to find container runtime socket
                # this value should consistent with the path of mounted 
                # container runtime socket file 
                - name: CONTAINER_RUNTIME_ENDPOINT
                  value: unix:///var/run/crio/crio.sock
                volumeMounts:
                  # mount container runtime socket file to this path
                - name: crio
                  mountPath: /var/run/crio
            volumes:
            - name: crio
              hostPath:
                path: /var/run/crio
            restartPolicy: OnFailure
        completionPolicy:
          type: Always
          ttlSecondsAfterFinished: 90
        failurePolicy:
          type: Continue
          restartLimit: 3
```

应用：

```bash
kubectl apply -f image-cleaner.yaml
```

登录到node上看看效果,
因为grafana/mimir没有被容器运行，所以镜像少了grafana/mimir：

```bash
ssh opc@10.0.10.106
sudo crictl images | grep -i "docker.io/grafana"
```

![tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102230049272.png](tech-doc-master%25E4%25BA%2591%25E5%258E%2582%25E5%2595%2586%25E7%2594%25B2%25E9%25AA%25A8%25E6%2596%2587PaaSOKE2Kruise%25E6%25B8%2585%25E7%2590%2586%25E7%25A3%2581%25E7%259B%2598.assetsimage-20240102230049272.png)

## 4. 参考文档

- 登录并推送镜像到OCIR
https://docs.oracle.com/en-us/iaas/Content/Registry/Tasks/registrypushingimagesusingthedockercli.htm#Pushing_Images_Using_the_Docker_CLI