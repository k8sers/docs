[返回OKE中文文档集](../README.md)

# OKE启动盘磁盘容量自动扩容

OKE可以在创建Pool时自定义BootVolume（启动盘）的容量，默认情况下，超过50GB的容量是不会自动分配给启动盘使用。
这种情况，在创建Pool时，在"show advanced options"的"Initialization script"里面输入下面脚本内容，就可以将所有的容量默认分配给BootVolume了。

```
#!/bin/bash
curl --fail -H "Authorization: Bearer Oracle" -L0 http://169.254.169.254/opc/v2/instance/metadata/oke_init_script | base64 --decode >/var/run/oke-init.sh
bash /var/run/oke-init.sh

sudo dd iflag=direct if=/dev/sda of=/dev/null count=1
echo "1" | sudo tee /sys/class/block/sda/device/rescan
echo "y" | sudo /usr/libexec/oci-growfs
```

[返回OKE中文文档集](../README.md)