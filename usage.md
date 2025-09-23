## 使用方法
由于本项目核心加密参数不公开，因此请下载release中的exe文件，并按照以下步骤使用。  
1. **下载release中的`QDjob.exe`和`QDjob_editor.exe`文件，放到同一个目录下**

2. **运行`QDjob_editor.exe`，软件会自动创建配置`config.json`文件，按照下面说明配置用户，目前最大支持3个账号**  
   配置文件说明：
   - `log_level`: 日志级别，可选值：`DEBUG/INFO/ERROR`，默认`INFO`
   
   - `log_retention_days`: 日志保留天数，默认7天
   
   - `retry_attempts`: 失败重试次数，默认3次
   
   - `default_user_agent`: 默认用户代理，请以自己抓包获取的数据为准，其中末尾的7.9.384和1466代表起点版本
     
        ```bash
        Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading
        ```
        
   - `ibex`：必填，该参数可能是验证码相关参数，不填会导致出验证码，已修改脚本为不填无法运行。需要抓包获取一次，此后理论上永久有效。
   
              **获取方式**：抓包获取。推荐抓包接口(福利中心页面)：`https://h5.if.qidian.com/argus/api/v2/video/adv/mainPage`  
                            如果上面接口没有ibex参数，请手动完成一次激励任务，抓包：`https://h5.if.qidian.com/argus/api/v1/video/adv/finishWatch`
   
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