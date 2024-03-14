# OKE+Jenkins+ArgoCD+Harbor实现国内CI国外CD模式

## 准备工作

- OKE 集群
- OCIR 镜像仓库
- OCI Devops的Code Repository
- 最新kubectl工具
- helm
- Jenkins，需具有公网IP或者与OKE打通了内网

## 安装ArgoCD

### a) 下载客户端

```
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x argocd-linux-amd64
mkdir ~/bin/
mv argocd-linux-amd64 ~/bin/argocd
vi .bash_profile
```

在文件中加入

```bash
PATH=$PATH:$HOME/bin
export PATH
```

使生效

```bash
source ~/.bash_profile
```

### b) 安装ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

等pod都启动后

```bash
argocd login --core

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
argocd admin initial-password -n argocd
#记下密码
kubectl get svc argocd-server -n argocd
#记下External-IP地址，用浏览器打开，用户名 admin 密码 为上面输出的密码

```

## 安装ArgoRollouts

### a) 安装

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml

curl -LO https://github.com/argoproj/argo-rollouts/releases/download/v1.4.1/kubectl-argo-rollouts-linux-amd64
chmod +x kubectl-argo-rollouts-linux-amd64
mv kubectl-argo-rollouts-linux-amd64 ~/bin/kubectl-argo-rollouts
source ~/.bash_profile
kubectl argo rollouts version

```

basic-rollout.yaml

```yaml
apiVersion: argoproj.io/v1alpha1kind: Rolloutmetadata:  name: rollouts-demospec:  replicas: 5 # 定义5个副本  strategy: # 定义升级策略    canary: # 金丝雀发布      steps: # 发布的节奏        - setWeight: 20        - pause: {} # 会一直暂停        - setWeight: 40        - pause: { duration: 10 } # 暂停10s        - setWeight: 60        - pause: { duration: 10 }        - setWeight: 80        - pause: { duration: 10 }  revisionHistoryLimit: 2 # 下面部分其实是和 Deployment 兼容的  selector:    matchLabels:      app: rollouts-demo  template:    metadata:      labels:        app: rollouts-demo    spec:      containers:        - name: rollouts-demo          image: argoproj/rollouts-demo:blue          ports:            - name: http              containerPort: 8080              protocol: TCP          resources:            requests:              memory: 32Mi              cpu: 5m
```

```bash
vi basic-service.yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: rollouts-demo
spec:
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
  selector:
    app: rollouts-demo
```

```bash
kubectl delete -f basic-rollout.yaml
kubectl delete -f basic-service.yaml

kubectl apply -f basic-rollout.yaml
kubectl apply -f basic-service.yaml

kubectl get pods -l app=rollouts-demo
kubectl argo rollouts get rollout rollouts-demo --watch
```