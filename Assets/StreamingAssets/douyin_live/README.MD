# 抖音直播获取弹幕聊天、送礼、点赞、关注等 Python 实现，并转发到 Unity 游戏引擎
【最新写法】
    直接开 Unity 运行即可，无需安装任何依赖
    py 代码直接放在 StreamingAssets 目录下了（为了 pc 打包能找到路径）

    如果想要把 py 服务器和 Unity 分开的话，直接把代码挪出来，使用 start.bat 运行
    并把 Launcher 上的 PythonManager disable


Python 爬虫获取弹幕聊天、送礼、点赞、关注，然后转发到 Unity
相当于 Unity 获取弹幕聊天、送礼、点赞、关注
注意：也可以转发到其他平台，只要在那个平台启动 http 服务器，然后处理一下 post（参考本项目 Unity 写法）

## Python 环境

```
Python 3.9 
Unity 2019.3.0f6 
讲道理 Unity 5 以上都行，没有什么高级代码
```

## 安装 Python 依赖包

```shell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 生成Proto文件
进入 dy_proto 目录，执行以下代码（理论上我已经生成好了，如果有协议报错就执行一下）
```
protoc -I . --python_out=. ./douyin.proto

```

## 动态配置

```python
# 直播地址
ROOM_URL = "https://live.douyin.com/567789235524"
# 推送地址，live 可以随便填，可以在 Unity 根据 live 字段区别不同的 post
SEND_URL = "http://127.0.0.1:12366/live"
```

## 运行
```shell
python main.py
```
然后运行 Unity