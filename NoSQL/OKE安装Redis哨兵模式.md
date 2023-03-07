# OKE安装Redis（哨兵模式）

```shell
helm repo add bitnami-repo https://charts.bitnami.com/bitnami
helm install redis-test --set sentinel.enabled=true --set sentinel.image.tag=7.0.8-debian-11-r12 --set sentinel.quorum=2 bitnami/redis -nsupport
```

