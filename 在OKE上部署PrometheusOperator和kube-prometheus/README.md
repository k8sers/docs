[返回OKE中文文档集](../README.md)

# 在OKE上部署PrometheusOperator和kube-prometheus

1. 获取kube-prometheus项目，

   ```
   git clone https://github.com/prometheus-operator/kube-prometheus.git; cd kube-prometheus
   ```

2. 部署kube-prometheus，

   ```
   # Create the namespace and CRDs, and then wait for them to be availble before creating the remaining resources
   kubectl create -f manifests/setup
   
   # Wait until the "servicemonitors" CRD is created. The message "No resources found" means success in this context.
   until kubectl get servicemonitors --all-namespaces ; do date; sleep 1; echo ""; done
   
   kubectl create -f manifests/
   ```

3. 访问Prometheus，

   通过运行以下命令，可以使用Prometheus、Alertmanager、Grafana dashboards。

   ```
   kubectl --namespace monitoring port-forward svc/prometheus-k8s 9090
   ```

   在浏览器中的[localhost:9090](http://localhost:9090/)上打开Prometheus。

4. 访问Alertmanager，

   ```
   kubectl --namespace monitoring port-forward svc/alertmanager-main 9093
   ```

   在浏览器中的[localhost:9093](http://localhost:9093/)上打开Alertmanager。

5. 访问Grafana，默认用户名和密码是`admin/admin`，

   ```
   kubectl --namespace monitoring port-forward svc/grafana 3000
   ```

   在浏览器中的[localhost:3000](http://localhost:3000/)上打开Grafana。

6. (Optional)移除kube-prometheus，

   ```
   kubectl delete --ignore-not-found=true -f manifests/ -f manifests/setup
   ```

   

参考文档：

- [Quick Start - Prometheus Operator (prometheus-operator.dev)](https://prometheus-operator.dev/docs/prologue/quick-start/)

[返回OKE中文文档集](../README.md)