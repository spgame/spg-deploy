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
sudo docker-compose stop ${SERVER_BRANCH}
sudo docker-compose rm -f ${SERVER_BRANCH}
sudo docker rmi -f diablo_${SERVER_BRANCH}
sudo docker-compose build ${SERVER_BRANCH}
sudo docker-compose up -d ${SERVER_BRANCH}

echo ${SERVER_BRANCH}' BULDING SUCCESS!!!!!!'