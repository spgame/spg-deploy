export CLIENT_DIR=/var/jenkins_home/git_home/spg-client
export STATIC_DIR=/var/jenkins_home/git_home/spg-static

export SOURCE_DIR=$STATIC_DIR/static_file
export TARGET_DIR=$DEPLOY_DIR/static
export CONFIG_FILE=config/`date +%Y_%m_%d_%H_%M_%S`.zip
export CONFIG_DIR=`dirname $CONFIG_FILE`

work(){
	cd $SOURCE_DIR
	filelist=`find $PWD -type f`
	
	cd $TARGET_DIR
	rm -rf temp
	mkdir temp
	
	if [ ! -d "$CONFIG_DIR" ]; then
		mkdir "$CONFIG_DIR"
	fi
	echo { >$CONFIG_DIR/last/data.json
	
	for filename in $filelist ; do
		#计算哈希值
		hash=`sha1sum $filename`
		hash=${hash:0:8}

		#防止源文件列表中有冲突
		newnamebase=`basename $filename`
		extensionname=${newnamebase##*.}
		newnamebase=${newnamebase%.*}
		
		
		if [ -f temp/$newnamebase ]; then
			echo 源文件列表冲突：`cat temp/$newnamebase` $filename
			touch $WORKSPACE/failedFlag
			exit 1
		fi
		echo $filename >temp/$newnamebase

		#拷贝文件并防止冲突
		newname=$newnamebase.$hash.$extensionname
		i=0
		until testAndCopy $filename $newname ; do
			let i=$i+1
			newname=$newnamebase.$hash.$i.$extensionname
		done
		
		#获得文件尺寸
		filesize=`ls -l $filename | awk '{ print $5 }'`

		#写入资源配置文件
		if [ "$nextline" != "" ] ; then
			echo -e "\t$nextline," >>$CONFIG_DIR/last/data.json
		fi
		nextline=\"$newnamebase\":[\"$newname\",\"$filesize\"]

	done

	rm -rf temp
	
	cd $CONFIG_DIR
	echo -e "\t$nextline" >>last/data.json
	echo } >>last/data.json
	
}

testAndCopy(){
	#$1是源文件名 $2是目标文件名
	if [ -f $2 ]; then
		diff $1 $2 > /dev/null
		if [ $? == 0 ]; then
			return 0
		else
			echo 发生了文件冲突： $1 $2 >&2
			touch $WORKSPACE/failedFlag
			return 1
		fi
	else
		echo 复制文件 $1 $2
		cp $1 $2
	fi
}

echo ===================更新并复制资源====================
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

cd $SOURCE_DIR

if [ ! -f $CLIENT_DIR/SpecialGame/bin-debug/SpecialGame.swf ]; then
    echo 尚未构建客户端
    exit 1
fi
rm -rf bin
mkdir bin
find $CLIENT_DIR/SpecialGame/bin-debug/ -name "*.swf" | xargs -i cp -f {} bin/

if [ ! -f $STATIC_DIR/static_xls/aes.zip ]; then
    echo 尚未生成静态数据
    exit 1
fi
rm -rf aes
unzip $STATIC_DIR/static_xls/aes.zip -d aes

if [ ! -f $CLIENT_DIR/SpecialGame/src/com/vox/games/specialGame/net/ProtocolHash.json ]; then
    echo 尚未生成协议
    exit 1
fi
rm -rf $TARGET_DIR/$CONFIG_DIR/last
mkdir -p $TARGET_DIR/$CONFIG_DIR/last
cp -f $CLIENT_DIR/SpecialGame/src/com/vox/games/specialGame/net/*.json $TARGET_DIR/$CONFIG_DIR/last

echo ======================处理资源=======================
echo _upd_HelloFantasy_提交资源文件 >$WORKSPACE/gitLog
rm -f $WORKSPACE/failedFlag
work 2>&1 | tee --append $WORKSPACE/gitLog
if [ -f $WORKSPACE/failedFlag ]; then
    echo 资源处理失败
    rm -rf $TARGET_DIR/temp
    exit -1
fi
echo ========================提交=========================
cd $TARGET_DIR
git add .
fileChangedNum=`git status -s -uno | wc -l`
if [ $fileChangedNum -eq 0 ]; then
    echo 版本未改变。
    exit
fi

cd $CONFIG_DIR/last
zip temp.zip *
cd $TARGET_DIR
mv -f $CONFIG_DIR/last/temp.zip $CONFIG_FILE
git add .
git commit -F $WORKSPACE/gitLog
git push origin master

echo ===拷贝静态文件、写入启动配置文件并重启Diablo======
mkdir -p /www/static
cp -a $TARGET_DIR/* /www/static
mkdir /www/internal
echo $CONFIG_FILE > /www/internal/test_config_path.txt
sudo docker restart diablo_test_1