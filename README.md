# 起点阅读自动化任务  

注意：ibex参数我抽空会逆向研究一下，这个参数跟时间戳有关，因此手动抓包获取只在短时间内有效。简单分析了一下，似乎是在borgus参数的基础上又加了一层加密，具体抽空会做出来的。

## 简介
本项目支持自动化完成起点的签到、激励任务、抽奖等日常操作，支持多用户和多种推送方式。每天50点章节卡，追一两本书不是问题。为避免恶意利用本程序，目前最大仅支持配置3个账号。

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
   - 飞书群聊机器人(`webhookurl`, `secret`)，创建一个群，然后就可以为群内添加机器人
   - Server酱(`SCKEY`)

3. **智能重试机制**  
   - 自动重试失败任务，默认最大重试3次（可配置重试次数）
   - 有一定概率遇到验证码，此时会停止执行并推送消息。后续会把找验证码识别的模型做进去，实现完全自动化

4. **完整日志系统**  
   - 支持按天分割日志
   - 可配置日志保留周期，默认是7天
   - 多级别日志记录（`DEBUG/INFO/ERROR`，默认`INFO`）

## 项目架构
```bash
├── cookies/           # 用户cookies存储目录
├── main.py            # 程序入口
├── enctrypt_qidian.py # 核心参数加密模块(不公开，以免项目寄掉)
├── QDjob.py           # 核心逻辑模块
├── push.py            # 推送服务基类及实现
├── logger.py          # 日志管理模块
└── config.json        # 用户配置文件
```

## 使用方法
由于本项目核心加密参数不公开，因此请下载release中的exe文件，并按照以下步骤使用。  
1. **下载release中的`QDjob.exe`和`QDjob_editor.exe`文件，放到同一个目录下**

2. **运行`QDjob_editor.exe`，软件会自动创建配置`config.json`文件，按照下面说明配置用户，目前最大支持3个账号，如果需要无限制版本，请联系我**  
   配置文件说明：
   - `log_level`: 日志级别，可选值：`DEBUG/INFO/ERROR`，默认`INFO`
   
   - `log_retention_days`: 日志保留天数，默认7天
   
   - `retry_attempts`: 失败重试次数，默认3次
   
   - `default_user_agent`: 默认用户代理，请以自己抓包获取的数据为准，其中末尾的7.9.384和1466代表起点版本
        
        ```bash
        Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading
        ```
        
   - `ibex`：非必填，该参数可能是验证码相关参数，不填会导致出验证码。目前先手动抓包获取吧，后续有时间了我会逆向看看这个到底是什么。
   
     ​         **获取方式**：抓包获取，需要手动执行一次任务才能抓到。抓包接口：`https://h5.if.qidian.com/argus/api/v1/video/adv/finishWatch`
   
   - `users`: 用户列表，每个用户包含以下字段
     
     - `username`: 用户名
     - `cookies_file`: 用户`cookies`文件名，默认为`cookies/{username}.json`
     - `user_agent`: 为每个用户单独配置UA，不填则默认使用`default_user_agent`
     - `tasks`: 任务列表，选中表示执行，不选中则不执行
     - `push_services`: 推送服务列表，按需配置，如果不需要，请直接删除。其中飞书推送时，如果你配置了签名验证，请选中`是否有签名验证`，并填写`秘钥`。
   
3. **每个用户都需要配置`cookies`文件，也就是你的账号，目前仅支持抓包获取，后续会添加登录功能。**  
   即便后面添加了登录功能，但还是更推荐你使用抓包获取`cookies`，可以有效防止账号遇到验证码。  
   起点并没有对抓包有什么限制，使用常用的抓包软件就行，这里放上[小黄鸟(过检测版)](https://wwqe.lanzouo.com/iImXX2y6ysje) 密码:`3bt2`  
   请将你抓包获取到的`cookies`放在`cookies`配置框，软件提供了字符串格式`cookies`的转换功能，参数`qid`、`QDInfo`必须包含，其他字段尽量包含，具体那些字段不能缺我也没测。最终格式如下：
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
    │   └── your_username.json
    ├── config.json
    ├── QDjob.exe
    └── QDjob_editor.exe
   ```
   
5. **运行`QDjob.exe`程序或在`QDjob_editor.exe`中点击执行任务**

6. **执行程序**
   * `windows`: 执行`QDjob.exe`或者在`QDjob_editor.exe`中点击执行任务
   * `linux`:
     * 分别打开两个程序的属性设置，设置`QDjob`和`QDjob_editor`程序可执行。
     * 执行`QDjob`或者在`QDjob_editor`中点击执行任务。

### 配置日常运行  
请在完成了上面的配置后，按照以下步骤实现每日自动托管运行。
1. **任务计划程序**  
将`QDjob.exe`程序放入计划任务中，并设置计划任务执行时间。  
2. **`ztasker`(推荐)**  
使用`ztasker`来配置每日执行，比任务计划程序更加稳定。点这里：[官网网址](https://www.everauto.net/cn/index.html)

## 关于`issue`
* 如果发现任何问题，欢迎在`issue`中提出来，在提`issue`时请将日志等级改为`DEBUG`，并在日志内容中包含你所遇到的问题。

## TODO
 *  添加登录功能，仍然建议使用抓包来获取`cookies`，能有效避免账号遇到验证码
 *  添加验证码识别功能
 *  添加更多推送服务  
 ······

## 叠甲
    本项目为个人项目，仅供学习交流使用，请勿用于非法用途，请于下载后24小时内删除。
    如有侵权，请联系删除。



