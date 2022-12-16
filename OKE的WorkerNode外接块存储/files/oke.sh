#!/bin/bash

curl --fail -H "Authorization: Bearer Oracle" -L0 http://169.254.169.254/opc/v2/instance/metadata/oke_init_script | base64 --decode >/var/run/oke-init.sh

python3 /usr/local/bin/oke_attachbv.py 100 20

while :
do
    if [ -b /dev/sdb ]; 
    then
	sleep 3
        mkfs.xfs /dev/sdb
	mkdir /u01
        mount /dev/sdb /u01
        mkdir -p /u01/var/lib/kubelet
        mkdir -p /u01/var/lib/containers
        ln -s /u01/var/lib/containers  /var/lib/containers
        ln -s /u01/var/lib/kubelet /var/lib/kubelet
        echo '/dev/sdb /u01 xfs defaults,_netdev,nofail 0 2' >> /etc/fstab
        break
    fi
    sleep 1
done

bash /var/run/oke-init.sh
