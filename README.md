# 起点阅读自动化任务

## 简介
本项目支持自动化完成某点的签到、激励任务、抽奖等日常操作，支持多用户和多种推送方式。每天50点章节卡，追一两本书不是问题。

## 主要功能
1. **主要实现的功能**  
   目前实现以下功能
   - 自动签到（每日签到）
   - 激励视频任务 10点+10点+20点=40点章节卡
   - 额外激励视频任务 (似乎现在起点取消了这个任务，但接口没删)
   - 额外章节卡任务 (额外3次小视频) 10点章节卡
   - 每日抽奖任务

2. **多平台推送支持**  
   目前仅支持以下推送服务，如果有想要更多支持的推送服务，欢迎提issue。
   - 飞书机器人(webhookurl, secret)
   - Server酱(SCKEY)

3. **智能重试机制**  
   - 自动重试失败任务，默认最大重试3次（可配置重试次数）
   - 有一定概率遇到验证码，此时会停止执行并推送消息。后续会把找验证码识别的模型做进去，实现完全自动化

4. **完整日志系统**  
   - 支持按天分割日志
   - 可配置日志保留周期，默认是7天
   - 多级别日志记录（DEBUG/INFO/ERROR，默认INFO）

## 项目架构
```bash
├── main.py            # 程序入口
├── enctrypt_qidian.py # 核心参数加密模块(不公开，以免项目寄掉)
├── QDjob.py           # 核心逻辑模块
├── push.py            # 推送服务基类及实现
├── logger.py          # 日志管理模块
├── config.json        # 用户配置文件
└── cookies/           # 用户cookies存储目录
```

## 使用方法
由于本项目核心加密参数不公开，因此请下载release中的exe文件，并按照以下步骤使用。  
1. **下载release中的exe文件**
2. **创建配置config.json文件**  
<span style="color:red; font-size:small;">关于配置文件，我后续会做一个GUI来辅助配置config，敬请期待。</span>    
   配置文件说明：
   - log_level: 日志级别，可选值：DEBUG/INFO/ERROR，默认INFO
   - log_retention_days: 日志保留天数，默认7天
   - retry_attempts: 失败重试次数，默认3次
   - default_user_agent: 默认用户代理，请以自己抓包获取的数据为准，其中末尾的7.9.384和1466代表起点版本
        ```bash
        Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading
        ```
   - users: 用户列表，每个用户包含以下字段
     - username: 用户名
     - cookies_file: 用户cookies文件名，默认为cookies/{username}.json
     - user_agent: 为每个用户单独配置UA
     - tasks: 任务列表，true表示执行，false表示不执行
     - push_services: 推送服务列表，按需配置，如果不需要，请直接删除。其中飞书推送时，如果你配置了secret，请设置havesign为true，并填写secret。
 
   配置文件示例如下：  
   ```json
   {
        "log_level": "INFO",
        "log_retention_days": 7,
        "retry_attempts": 3,
        "default_user_agent": "QDReaderAndroid/7.9.360",
        "users": [
            {
            "username": "your_username",
            "cookies_file": "cookies/your_username.json",
            "user_agent": "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading",
            "tasks": {
                "签到任务": true,
                "激励碎片任务": true,
                "额外激励任务": true,
                "章节卡任务": true,
                "每日抽奖任务": true
            },
            "push_services": [
                {
                    "type": "feishu",
                    "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/xxxx",
                    "havesign": true,
                    "secret": "your_secret"
                },
                {
                    "type": "serverchan",
                    "sckey": "SCUxxxxxx"
                }
            ]
            }
        ]
    }
    ```
3. **创建cookies文件夹，并创建用户cookies文件**  
   请将你抓包获取到的cookies放在your_username.json文件中，QDInfo可以为空，其他字段尽量包含，具体那些字段不能缺我也没测。格式如下：
   ```json
   {
        "appId": "",
        "areaId": "",
        "lang": "",
        "mode": "",
        "bar": "",
        "qidth": "",
        "qid": "",
        "ywkey": "",
        "ywguid": "",
        "uuid": "",
        "cmfuToken": "",
        "QDInfo": ""
   }
   ```

4. **目录树**  
   当你配置完毕后，目录树结构应当如下：
   ```bash
   .
   ├── cookies/
   ├──|── your_username.json
   ├── config.json
   └── QidianApp.exe
   ```
5. **运行QidianApp.exe程序**

## 叠甲
    本项目为个人项目，仅供学习交流使用，请勿用于非法用途，请于下载后24小时内删除。
    如有侵权，请联系删除。
