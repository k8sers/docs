# AWS命令行读取OCI Buckets

下载工具：

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
cd aws/dist/
./aws --help
```

配置：

```bash
export AWS_ACCESS_KEY_ID=xxxx
export AWS_SECRET_ACCESS_KEY=xxxxx
export AWS_DEFAULT_REGION=xx-xxx-1
export AWS_ENDPOINT_URL=https://<oss-namespace>.compat.objectstorage.xx-xxxx-1.oraclecloud.com

```

读写测试：

```bash
aws s3api  list-buckets --endpoint-url=https://<oss-namespace>.compat.objectstorage.xx-xxxx-1.oraclecloud.com
./aws s3api  list-buckets --endpoint-url=https://<oss-namespace>.compat.objectstorage.xx-xxxx-1.oraclecloud.com
echo 'your string' | ./aws s3 cp - s3://<bucket-name>/w.txt --endpoint-url=https://<oss-namespace>.compat.objectstorage.xx-xxxx-1.oraclecloud.com
./aws s3api  list-objects --bucket <bucket-name>  --endpoint-url=https://<oss-namespace>.compat.objectstorage.xx-xxxx-1.oraclecloud.com
```