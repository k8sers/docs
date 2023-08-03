# 使用Fluentd收集OKE日志到Fluentd



```shell
git clone https://github.com/mgxian/k8s-log.git
cd k8s-log
git checkout v1

kubectl label nodes --all beta.kubernetes.io/fluentd-ds-ready=true

# 部署
kubectl apply -f fluentd-es-configmap.yaml
kubectl apply -f fluentd-es-ds.yaml

# 查看状态
kubectl get pods,svc -n logging -o wide


kubectl port-forward -n logging pod/kibana-logging-7b74fff47c-lj29n 5601:5601
```



# 相关链接

https://baijiahao.baidu.com/s?id=1708784548148848643&wfr=spider&for=pc
