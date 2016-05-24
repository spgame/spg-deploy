sudo docker build -t 'spg-log' ../spg-log

if [ $? -ne 0 ]; then
	echo 镜像构建失败
	exit -1
fi

python shell/deploy_image_remote.py type slave shell/create_staging_remote.json \
  --name diablo_release --remove_current \
  --pull --image spgmaster.just4test.net/diablo_release --registry spgmaster \
  --env "JAVA_OPTS=-Duser.timezone=GMT+8 -Xms8192m -Xmx8192m"
  
if [ $? -ne 0 ]; then
	echo 远程部署失败
	exit -1
fi