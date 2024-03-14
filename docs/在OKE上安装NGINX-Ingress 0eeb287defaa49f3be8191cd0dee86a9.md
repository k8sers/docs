# 在OKE上安装NGINX-Ingress

1. 添加Helm库
    
    ```bash
    helm repo add nginx-stable https://helm.nginx.com/stable
    helm repo update
    ```
    
2. 安装NGINX Ingress Controller，
    
    ```bash
    kubectl create namespace nginx-ingress
    helm install -n nginx-ingress nginx-ingress nginx-stable/nginx-ingress
    ```
    
    (Optional)如果想启用设置Snippets功能
    
    ```bash
    helm install -n nginx-ingress nginx-ingress --set controller.enableSnippets=true nginx-stable/nginx-ingress
    ```
    
3. 确认是否创建了新的ingressclass，
    
    ```bash
    kubectl get ingressclass
    ```
    
    输出结果，
    
    ![k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%25AE%2589%25E8%25A3%2585NGINXIngressControllerimagesimage-20221026122910451.png](k8sers-dev2%25E5%259C%25A8OKE%25E4%25B8%258A%25E5%25AE%2589%25E8%25A3%2585NGINXIngressControllerimagesimage-20221026122910451.png)
    
4. (Optional)卸载NGINX Ingress Controller，
    
    ```
    helm uninstall -n nginx-ingress nginx-ingress
    ```
    

参考文档：

- [Installation with Helm | NGINX Ingress Controller](https://docs.nginx.com/nginx-ingress-controller/installation/installation-with-helm/)