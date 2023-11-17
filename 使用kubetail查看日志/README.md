[返回OKE中文文档集](../README.md)

# 使用kubetail查看日志

kubetail 是使你能够将多个pod的日志聚合（tail/follow）到一个流中的 Bash 脚本。这与运行 "kubectl logs -f" 是一样的，只是针对多个pod。

## github 地址

[https://github.com/johanhaleby/kubetail](https://github.com/johanhaleby/kubetail)

## 安装
执行下面命令安装，
```
wget https://raw.githubusercontent.com/johanhaleby/kubetail/master/kubetail
chmod +x kubetail
sudo cp kubetail /usr/local/bin
```

## 配置 completion

```
cd $HOME
wget https://raw.githubusercontent.com/johanhaleby/kubetail/master/completion/kubetail.bash
echo 'alias kt=kubetail' >> $HOME/.bashrc
echo '. kubetail.bash' >> $HOME/.bashrc
source $HOME/.bashrc
```

## 使用 kubetail

首先找到你所有 pods 的名字，

```
$ kubectl get pods

NAME                   READY     STATUS    RESTARTS   AGE
app1-v1-aba8y          1/1       Running   0          1d
app1-v1-gc4st          1/1       Running   0          1d
app1-v1-m8acl  	       1/1       Running   0          6d
app1-v1-s20d0  	       1/1       Running   0          1d
app2-v31-9pbpn         1/1       Running   0          1d
app2-v31-q74wg         1/1       Running   0          1d
my-demo-v5-0fa8o       1/1       Running   0          3h
my-demo-v5-yhren       1/1       Running   0          2h
```

要一次性跟踪两个 "app2" pods 的日志，只需执行下面命令，

```
$ kubetail app2
```

要从多个 pods 中只跟踪一个特定的容器，要像这样指定容器，

```
$ kubetail app2 -c container1
```

你可以重复 -c 来跟踪多个特定的容器，

```
$ kubetail app2 -c container1 -c container2
```

要同时跟踪多个应用程序，请用逗号将它们分开，

```
$ kubetail app1,app2
```

对于高级匹配，你可以使用正则表达式，

```
$ kubetail "^app1|.*my-demo.*" --regex
```

要在一个特定的命名空间内跟踪日志，请确保在你提供容器和应用程序的值后附加命名空间标志，

```
$ kubetail app2 -c container1 -n namespace1
```

提供-h以获得帮助和其他选项，

```
$ kubetail -h
```



[返回OKE中文文档集](../README.md)