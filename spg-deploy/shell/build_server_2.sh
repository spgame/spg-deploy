# SERVER_BRANCH 服务器代码分支
# SERVER_DIR 指定分支的服务器代码目录。 master/staging/release
# SERVER_NAME 指定服务器名。 test/staging/release
# TAG 指定镜像标签。可为空。指定了镜像标签将导致镜像保存在本地不会自动删除。
# NEED_PUSH 如果指定为true则将其推送到本地仓库。
# NEED_RUN 如果指定为true则在本地运行镜像。

# 更新git tag
cd ${SERVER_DIR}
git tag -d $(git tag)
git fetch --tags

cd ${SERVER_DIR}/spg-web/src/main/resources/config
cp -f product.${SERVER_BRANCH}.properties product.properties
if [ $? -ne 0 ]; then
  echo 'FAILED mv'
  exit -1
fi
echo '#MV product.properties SUCCEEDED.'

cd ${SERVER_DIR}
mvn clean package #mvn打包
if [ $? -ne 0 ]; then
  echo 'MVN BUILDING FAILED'
  exit -1
fi

#构建diablo 镜像
mkdir diablo
cp spg-web/target/ROOT.war diablo
cp $DEPLOY_DIR/shell/Dockerfile diablo
cp $DEPLOY_DIR/shell/docker-compose.yml diablo

cd diablo
sudo docker-compose stop ${SERVER_NAME}
sudo docker-compose rm -f ${SERVER_NAME}
sudo docker rmi -f diablo_${SERVER_NAME}
sudo docker-compose build ${SERVER_NAME}

if [ ${TAG}. != . ]; then
	sudo docker tag -f diablo_${SERVER_NAME} diablo_${SERVER_NAME}:${TAG}
fi

if [ ${NEED_PUSH}. == true. ]; then
	#如果未指定tag，则尝试使用git的tag
	if [ ${TAG}. == . ]; then
		export TAG=`git name-rev --tags --name-only $(git rev-parse HEAD)`
	fi
	#如果仍然没有tag，则使用git的版本哈希
	if [ ${TAG}. == undefined. ]; then
		export TAG=`git log --pretty=format:"%h" -1`
	fi
	
	sudo docker tag -f diablo_${SERVER_NAME} localhost:443/diablo_${SERVER_NAME}:${TAG}
	sudo docker push localhost:443/diablo_${SERVER_NAME}:${TAG}
	sudo docker rmi localhost:443/diablo_${SERVER_NAME}:${TAG}
	
	sudo docker tag -f diablo_${SERVER_NAME} localhost:443/diablo_${SERVER_NAME}
	sudo docker push localhost:443/diablo_${SERVER_NAME}
	sudo docker rmi localhost:443/diablo_${SERVER_NAME}
fi

if [ ${NEED_RUN}. == true. ]; then
	sudo docker-compose up -d ${SERVER_NAME}
	if [ $? -ne 0 ]; then
        echo 'docker-compose FAILED'
    exit -1
fi
fi

echo ${SERVER_NAME}' BULDING SUCCESS!!!!!!'