#更新客户端代码目录
export CLIENT_ORIGIN=git@git.coding.net:just4test/spg-client.git
export CLIENT_DIR=/var/jenkins_home/git_home/spg-client
if [ ! -d $CLIENT_DIR ]; then
    git clone $CLIENT_ORIGIN $CLIENT_DIR
    cd $CLIENT_DIR
    git config user.email "yu.wang@17zuoye.com"
    git config user.name "bot"
else
    cd $CLIENT_DIR
    git fetch --all
    git reset --hard origin/master
    git clean -fd
fi

#更新服务端代码目录
export SERVER_BRANCH=master
export SERVER_ORIGIN=git@git.coding.net:wsd_spg/spg-server.git
export SERVER_DIR_BASE=/var/jenkins_home/git_home/spg-server
export SERVER_DIR=${SERVER_DIR_BASE}_$SERVER_BRANCH
if [ ! -d $SERVER_DIR ]; then
    git clone -b $SERVER_BRANCH $SERVER_ORIGIN $SERVER_DIR
    cd $SERVER_DIR
    git config user.email "yu.wang@17zuoye.com"
    git config user.name "bot"
else
    cd $SERVER_DIR
    git fetch --all
    git reset --hard origin/$SERVER_BRANCH
    git clean -fd
fi


#生成协议
as3OutputDir=$CLIENT_DIR/SpecialGame/src
javaOutputDir=$SERVER_DIR/spg-api/src/main/java/
protocolDirBase=$DEPLOY_DIR/protocol
dynamicProtocolDir=$protocolDirBase/SpecialGameDynamic
staticProtocolDir=$protocolDirBase/SpecialGameStatic

cd $WORKSPACE
rm rm -rf *

tempDir=`basename $dynamicProtocolDir`
cp -r $dynamicProtocolDir $tempDir
java -jar $DEPLOY_DIR/shell/TemplateGenerator.jar $tempDir as3 java
if [ $? -ne 0 ]; then
  echo '在生成动态协议时发生了错误'
  exit -1
fi
cp -a output/as3/* $as3OutputDir
cp -a output/java/* $javaOutputDir
rm -rf output

tempDir=`basename $staticProtocolDir`
cp -r $staticProtocolDir $tempDir
java -jar $DEPLOY_DIR/shell/TemplateGenerator.jar $tempDir as3 java
if [ $? -ne 0 ]; then
  echo '在生成静态协议时发生了错误'
  exit -1
fi
cp -a output/as3/* $as3OutputDir
cp -a output/java/* $javaOutputDir
rm -rf output


#提交文件
echo 自动生成了消息协议。以下是协议配置最近的两条更新： > $WORKSPACE/gitLog
cd $protocolDirBase
git log --pretty=format:"%h - %an, %ad : %s" -2 -- $protocolDirBase >> $WORKSPACE/gitLog
cd $as3OutputDir
git add .
fileChangedNum=`git status -s -uno | wc -l`
if [ $fileChangedNum -ne 0 ]; then
    git commit -F $WORKSPACE/gitLog
    git push origin master
else
    echo as3 代码未改变
fi

cd $javaOutputDir
git add .
fileChangedNum=`git status -s -uno | wc -l`
if [ $fileChangedNum -ne 0 ]; then
    git commit -F $WORKSPACE/gitLog
    git push origin $SERVER_BRANCH
else
    echo java 代码未改变
fi