#构建处理程序
cd ${SERVER_DIR}
#mvn打包
mvn clean package -f pom_static_build.xml
if [ $? -ne 0 ]; then
  echo '数据处理程序构建失败'
  exit -1
fi




#更新静态资源目录
export STATIC_ORIGIN=git@git.coding.net:just4test/spg-static.git
export STATIC_DIR=/var/jenkins_home/git_home/spg-static
if [ ! -d $STATIC_DIR ]; then
    git clone $STATIC_ORIGIN $STATIC_DIR
    cd $STATIC_DIR
    git config user.email "yu.wang@17zuoye.com"
    git config user.name "bot"
else
    cd $STATIC_DIR
    git fetch --all
    git reset --hard origin/master
fi


cd static_xls
rm -f xls.zip
zip xls.zip *.xls
rm -f aes.zip

java -jar -Duser.timezone=GMT+8 "${SERVER_DIR}/spg-static-build/target/spg-static-build-1.0-SNAPSHOT-jar-with-dependencies.jar" xls.zip aes.zip

result=$?
if [ $result -eq 0 ]; then
	echo 以下是静态数据最近的两条更新： > aesLog
	git log --pretty=format:"%h - %an, %ad : %s" -2 -- . >> aesLog
else
	if [ $result -eq 2 ] && [ "$IGNORE_UNSUPPORT" == "true" ]; then
		echo 静态数据构建时发生了一些错误，但构建发起者选择忽略这些错误 > aesLog
		echo 以下是静态数据最近的两条更新： >> aesLog
		git log --pretty=format:"%h - %an, %ad : %s" -2 -- . >> aesLog
	else
		echo '数据处理程序执行失败'
		rm -f aes.zip
		exit -1
	fi
fi
