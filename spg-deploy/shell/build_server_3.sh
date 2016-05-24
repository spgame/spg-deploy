# 必须参数：
# SERVER_DIR 指定分支的服务器代码目录。 master/staging/release
# SERVER_NAME 指定服务器名。 test/staging/release。
# 可选参数：
# CONFIG_NAME 覆盖product.properties为指定的版本
# TAG 指定镜像标签。可为空。指定了镜像标签将导致镜像保存在本地不会自动删除。
# 	如果指定为__AUTO__则自动生成一个标签
# DOCKER_FILE 指定Dockerfile的文件名
# DOCKER_FILE_APPEND 如果指定此值，值将会追加到Dockerfile末尾
# NEED_PUSH 如果指定为true则将其推送到本地仓库。
# NEED_RUN 如果指定为true则在本地运行镜像。
# 返回值：
# IMAGE_NAME

if [ ${SERVER_DIR}. == . ]; then
	echo 未指定 SERVER_DIR 服务器代码目录
	exit -1
fi
echo 服务器代码目录：${SERVER_DIR}

if [ ${SERVER_NAME}. == . ]; then
	echo 未指定 SERVER_NAME 服务器名
	exit -1
fi
echo 服务器名：${SERVER_NAME}

if [ ${CONFIG_NAME}. != . ]; then
	echo 覆盖product.properties为指定的版本 [${CONFIG_NAME}]
fi

if [ ${TAG}. != . ]; then
	echo 镜像标签指定为 [${TAG}]
fi

if [ ${NEED_PUSH}. == true. ]; then
	echo 指定了生成镜像后推送到仓库
fi

if [ ${NEED_RUN}. == true. ]; then
	echo 指定了生成镜像后运行镜像
fi

if [ ${DOCKER_FILE}. != . ]; then
	echo 使用Dockerfile [${DOCKER_FILE}]
else
	DOCKER_FILE=Dockerfile
fi

if [ "${DOCKER_FILE_APPEND}" != "" ]; then
	echo 将 [${DOCKER_FILE_APPEND}] 追加到Dockerfile尾部
fi

# 更新git tag
cd ${SERVER_DIR}
git tag -d $(git tag)
git fetch --tags

#覆盖product.properties
if [ ${CONFIG_NAME}. != . ]; then
	cd ${SERVER_DIR}/spg-web/src/main/resources/config
	cp -f product.${CONFIG_NAME}.properties product.properties
	if [ $? -ne 0 ]; then
		echo 覆盖配置文件失败
		exit -1
	fi
	echo 已覆盖配置文件${CONFIG_NAME}
	cd ${SERVER_DIR}
fi

#mvn打包
mvn clean package -f pom_web_build.xml
if [ $? -ne 0 ]; then
  echo MVN打包失败
  exit -1
fi

#构建diablo镜像
mkdir diablo
cp spg-web/target/ROOT.war diablo
cp $DEPLOY_DIR/shell/${DOCKER_FILE} diablo/Dockerfile
if [ "${DOCKER_FILE_APPEND}" != "" ]; then
	echo -n "${DOCKER_FILE_APPEND}" >> diablo/Dockerfile
fi

cp $DEPLOY_DIR/shell/docker-compose.yml diablo

cd diablo
sudo docker-compose stop ${SERVER_NAME}
sudo docker-compose rm -f ${SERVER_NAME}
sudo docker rmi -f diablo_${SERVER_NAME}
sudo docker-compose build ${SERVER_NAME}

#打标签
if [ ${TAG}. == __AUTO__. ]; then
	#如果未指定tag，则尝试使用git的tag
	if [ ${TAG}. == . ]; then
		export TAG=`git name-rev --tags --name-only $(git rev-parse HEAD)`
	fi
	#如果仍然没有tag，则使用git的版本哈希
	if [ ${TAG}. == undefined. ]; then
		export TAG=`git log --pretty=format:"%h" -1`
	fi
fi
if [ ${TAG}. != . ]; then
	sudo docker tag -f diablo_${SERVER_NAME} diablo_${SERVER_NAME}:${TAG}
fi

#推送到仓库
if [ ${NEED_PUSH}. == true. ]; then	
	if [ ${TAG}. != . ]; then
		sudo docker tag -f diablo_${SERVER_NAME} localhost:443/diablo_${SERVER_NAME}:${TAG}
		sudo docker push localhost:443/diablo_${SERVER_NAME}:${TAG}
		sudo docker rmi localhost:443/diablo_${SERVER_NAME}:${TAG}
	fi
	sudo docker tag -f diablo_${SERVER_NAME} localhost:443/diablo_${SERVER_NAME}
	sudo docker push localhost:443/diablo_${SERVER_NAME}
	sudo docker rmi localhost:443/diablo_${SERVER_NAME}
fi

if [ ${NEED_RUN}. == true. ]; then
	sudo docker-compose up -d ${SERVER_NAME}
fi

echo ${SERVER_NAME} 编译成功
if [ ${TAG}. != . ]; then
	IMAGE_NAME=diablo_${SERVER_NAME}:${TAG}
else
	IMAGE_NAME=diablo_${SERVER_NAME}
fi
echo 生成镜像 ${IMAGE_NAME}
