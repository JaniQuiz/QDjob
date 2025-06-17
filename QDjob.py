# coding: utf-8
import os
import json
import requests
import time
import random
import re
from urllib.parse import urlencode
from typing import Dict, List, Optional, Any, Callable
from enctrypt_qidian import getQDInfo, getQDSign, getSDKSign, sort_query_string, getborgus
from push import PushService, FeiShu, ServerChan
from logger import LoggerManager
from logger import DEFAULT_LOG_RETENTION

# 配置常量
CONFIG_FILE = 'config.json'
COOKIES_DIR = 'cookies'
DEFAULT_USER_AGENT = "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading"
logger = LoggerManager().setup_basic_logger()

class QidianError(Exception):
    """自定义异常类"""
    def __init__(self, message: str, raw_data: Optional[Dict] = None):
        super().__init__(message)
        self.raw_data = raw_data

class UserConfig:
    """用户配置"""
    def __init__(self, username: str, cookies: Dict[str, str], 
                 tasks: Dict[str, bool], user_agent: str, 
                 push_services: List[PushService]):
        self.username = username
        self.cookies = cookies
        self.tasks = tasks
        self.user_agent = user_agent
        self.push_services = push_services

class ConfigManager:
    """配置管理类"""
    def __init__(self):
        self.config = self._load_config()
        self._validate_config()  # 新增：执行全局配置校验
        self.users = self._init_users()
        # logger.info("配置加载完成")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _init_users(self) -> List[UserConfig]:
        """初始化用户配置"""
        users = []
        for user_data in self.config['users']:
            if not self._validate_user_config(user_data):
                raise ValueError(f"用户 [{user_data.get('username', '未知')}] 配置错误，跳过该用户。")

            # 加载cookies文件
            cookies_path = user_data.get('cookies_file', f"{COOKIES_DIR}/{user_data['username']}.json")
            try:
                with open(cookies_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                # 如果 cookies 为空，跳过该用户
                if not cookies:
                    logger.error(f"用户 [{user_data['username']}] 的 cookies 文件为空，跳过该用户")
                    continue
            except FileNotFoundError:
                logger.error(f"未找到 cookies 文件: {cookies_path}，跳过用户 [{user_data['username']}]")
                continue

            # 初始化推送服务
            push_services = []
            for push_config in user_data.get('push_services', []):
                push_type = push_config.get('type')
                config_without_type = {k: v for k, v in push_config.items() if k != 'type'}

                if push_type == 'feishu':
                    push_service = FeiShu(**config_without_type)
                elif push_type == 'serverchan':
                    push_service = ServerChan(**config_without_type)
                else:
                    logger.warning(f"[推送配置] 用户[{user_data['username']}] 未知的推送类型: {push_type}")
                    continue

                push_services.append(push_service)
                
            # 创建用户配置对象
            user = UserConfig(
                username=user_data['username'],
                cookies=cookies,
                tasks=user_data.get('tasks', {}),
                user_agent=user_data.get('user_agent', self.config.get('default_user_agent')),
                push_services=push_services  # 添加缺失的参数
            )
            users.append(user)
            
        return users
    
    def save_cookies(self, username: str, cookies: Dict[str, str]) -> None:
        """保存用户cookies"""
        cookies_path = f"{COOKIES_DIR}/{username}.json"
        try:
            with open(cookies_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            logger.debug(f"保存cookies成功: {cookies_path}")
        except Exception as e:
            logger.error(f"保存cookies失败: {e}")

    def _validate_config(self):
        """全局配置校验"""
        # 校验日志级别
        if 'log_level' in self.config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.config['log_level'] not in valid_levels:
                logger.warning(f"日志级别配置错误，使用默认级别 INFO。有效值: {', '.join(valid_levels)}")
                self.config['log_level'] = 'INFO'
        
        # 校验日志保留天数
        if 'log_retention_days' in self.config:
            try:
                days = int(self.config['log_retention_days'])
                if days <= 0:
                    raise ValueError("日志保留天数必须为正整数")
                self.config['log_retention_days'] = days
            except (ValueError, TypeError):
                logger.warning("日志保留天数配置错误，使用默认值 7 天")
                self.config['log_retention_days'] = 7

        # 校验重试次数
        if 'retry_attempts' in self.config:
            try:
                attempts = int(self.config['retry_attempts'])
                if attempts <= 0:
                    raise ValueError("重试次数必须为正整数")
                self.config['retry_attempts'] = attempts
            except (ValueError, TypeError):
                logger.warning("重试次数配置错误，使用默认值 3 次")
                self.config['retry_attempts'] = 3
        else:
            self.config['retry_attempts'] = 3

        # 校验User-Agent 
        if "default_user_agent" in self.config:
            if not isinstance(self.config['default_user_agent'], str):
                logger.warning("默认User-Agent配置错误，使用默认值")
                self.config['default_user_agent'] = DEFAULT_USER_AGENT
        else:
            self.config['default_user_agent'] = DEFAULT_USER_AGENT
        
        # 校验用户配置
        if 'users' in self.config:
            for user_data in self.config['users']:
                self._validate_user_config(user_data)
    
    def _validate_user_config(self, user_data: dict) -> bool:
        """验证单个用户配置"""
        required_fields = ['username', 'cookies_file', 'tasks', 'user_agent', 'push_services']

        for field in required_fields:
            if field not in user_data:
                logger.error(f"用户[{user_data.get('username', '未知')}] 缺少必要字段: {field}")
                return False

        tasks = user_data.get('tasks', {})
        if not isinstance(tasks, dict):
            logger.error(f"用户[{user_data['username']}] 任务配置必须为字典类型")
            return False

        push_services = user_data.get('push_services', [])
        if not isinstance(push_services, list):
            logger.error(f"用户[{user_data['username']}] 推送服务配置必须为列表类型")
            return False

        valid_push_types = ['feishu', 'serverchan']
        for push_config in push_services:
            if not isinstance(push_config, dict):
                logger.warning(f"用户[{user_data['username']}] 推送配置项不是字典类型")
                return False

            push_type = push_config.get('type')
            if push_type not in valid_push_types:
                logger.warning(f"[配置错误] 用户[{user_data['username']}] 未知的推送类型: {push_type}")
                return False

            if push_type == 'feishu':
                if not push_config.get('webhook_url'):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] 飞书推送缺少必要字段: webhook_url")
                    return False
                if not isinstance(push_config.get('webhook_url', ''), str):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] 飞书推送 webhook_url 必须为字符串类型")
                    return False
                if not isinstance(push_config.get('havesign', False), bool):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] 飞书推送 havesign 必须为布尔类型")
                    return False
                if push_config.get('havesign', False) and not push_config.get('secret', ''):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] 飞书推送启用签名校验但 secret 为空")
                    return False
                if push_config.get('havesign', False) and not isinstance(push_config.get('secret', ''), str):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] 飞书推送 secret 必须为字符串类型")
                    return False

            elif push_type == 'serverchan':
                if not push_config.get('sckey'):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] Server酱推送缺少必要字段: sckey")
                    return False
                if not isinstance(push_config.get('sckey', ''), str):
                    logger.warning(f"[配置错误] 用户[{user_data['username']}] Server酱推送 sckey 必须为字符串类型")
                    return False

        return True

class QidianClient:
    """起点客户端"""
    def __init__(self, config: UserConfig):
        self.config = config
        self.session = requests.Session()
        self._init_headers()
        self._init_versions()
    
    def _init_headers(self) -> None:
        """初始化请求头"""
        self.headers_sdk = {
            'Host': 'h5.if.qidian.com',
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'helios': '1',
            'User-Agent': self.config.user_agent,
            'SDKSign': '',
            'tstamp': '',
            'X-Requested-With': 'com.qidian.QDReader',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://h5.if.qidian.com/h5/adv-develop/entry2?_viewmode=0&jump=zhanghu',
            'Accept-Language': 'zh-CN,zh-TW;q=0.9,zh;q=0.8,en-US;q=0.7,en;q=0.6',
        }
        
        self.headers_qd = {
            'Cache-Control': 'max-stale=0',
            'tstamp': '',
            'QDInfo': '',
            'User-Agent': self.config.user_agent,
            'QDSign': '',
            'Host': 'druidv6.if.qidian.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }
    
    def _init_versions(self) -> None:
        """初始化版本信息"""
        match = re.search(r'QDReaderAndroid/(\d+\.\d+\.\d+)/', self.config.user_agent)
        self.version = match.group(1) if match else "7.9.360"
        self.qid = self.config.cookies.get('qid', '')
    
    def _handle_response(self, response: requests.Response, 
                        error_msg: str = "请求失败") -> Dict[str, Any]:
        """处理响应并检测验证码"""
        try:
            result = response.json()
            logger.debug(f"响应数据: {result}")
            
            # 检测验证码
            risk_conf = result.get('Data', {}).get('RiskConf', {})
            ban_id = risk_conf.get('BanId', 0)  # 默认为0

            # 强制转换为整数并判断
            try:
                ban_id = int(ban_id)
            except (ValueError, TypeError):
                ban_id = 0

            # 非0即触发验证码
            if ban_id != 0:
                result['is_captcha'] = True
                result['captcha_data'] = risk_conf.copy()
                
            return result
        except json.JSONDecodeError:
            logger.error(f"{error_msg}: {response.text}")
            raise QidianError(f"{error_msg}: {response.text}")
        
    def _make_qd_request(self, url: str, params: dict = None, data: dict = None, method: str = 'POST') -> Dict[str, Any]:
        """创建qd类型请求"""
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))  # 随机延迟 1~3 秒

        ts = str(int(time.time() * 1000))
        params = params or {}
        data = data or {}
        
        # 生成加密参数
        query_string = sort_query_string(urlencode(data) if data else urlencode(params))
        QDSign = getQDSign(ts, query_string, self.version, self.qid)
        QDInfo = getQDInfo(ts, self.version, self.qid)
        borgus = getborgus(query_string)
        
        # 更新headers
        headers = self.headers_qd.copy()
        headers.update({
            'tstamp': ts,
            'QDInfo': QDInfo,
            'QDSign': QDSign,
            'borgus': borgus
        })

        # 更新 cookies
        self.config.cookies['QDInfo'] = QDInfo

        # 根据 method 显式选择请求方式
        if method.upper() == 'POST':
            response = self.session.post(url, params=params, data=data, headers=headers, cookies=self.config.cookies)
        else:
            response = self.session.get(url, params=params, headers=headers, cookies=self.config.cookies)

        return self._handle_response(response, "qd类型请求失败")

    def _make_sdk_request(self, url: str, params: dict = None, data: dict = None, method: str = 'POST') -> Dict[str, Any]:
        """创建sdk类型请求"""
        # 添加随机延迟
        time.sleep(random.uniform(1, 3))  # 随机延迟 1~3 秒

        ts = str(int(time.time() * 1000))
        params = params or {}
        data = data or {}
        
        # 生成加密参数
        query_string = sort_query_string(urlencode(data) if data else urlencode(params))
        SDKSign = getSDKSign(ts, query_string, self.version, self.qid)
        QDInfo = getQDInfo(ts, self.version, self.qid)
        borgus = getborgus(query_string)
        
        # 更新headers
        headers = self.headers_sdk.copy()
        headers.update({
            'tstamp': ts,
            'SDKSign': SDKSign,
            'borgus': borgus
        })

        # 更新 cookies
        self.config.cookies['QDInfo'] = QDInfo
        
         # 根据 method 显式选择请求方式
        if method.upper() == 'POST':
            if params=={} or params==None:
                response = self.session.post(url, data=data, headers=headers, cookies=self.config.cookies)
            else:
                response = self.session.post(url, params=params, data=data, headers=headers, cookies=self.config.cookies)
        else:
            if params=={} or params==None:
                response = self.session.get(url, headers=headers, cookies=self.config.cookies, data=data)
            else:
                response = self.session.get(url, params=params, headers=headers, cookies=self.config.cookies, data=data)
            
        return self._handle_response(response, "sdk类型请求失败")

    def check_login(self) -> Optional[str]:
        """检查登录状态"""
        ts = str(int(time.time() * 1000))
        url = "https://druidv6.if.qidian.com/argus/api/v1/user/getprofile"
        
        # 生成签名
        params = {}
        params_encrypt = sort_query_string('')
        QDSign = getQDSign(ts, params_encrypt, self.version, self.qid)
        QDInfo = getQDInfo(ts, self.version, self.qid)
        borgus = getborgus(params_encrypt)
        
        # 设置请求头
        headers = self.headers_qd.copy()
        headers.update({
            'tstamp': ts,
            'QDInfo': QDInfo,
            'QDSign': QDSign,
            'borgus': borgus
        })

        # 更新 cookies
        self.config.cookies['QDInfo'] = QDInfo
        
        try:
            response = self.session.get(url, params=params, cookies=self.config.cookies, headers=headers)
            result = self._handle_response(response, "登录检测失败")
            
            if result.get('Data', {}).get('Nickname'):
                return result['Data']['Nickname']
            return None
        except Exception as e:
            logger.error(f"登录检测异常: {e}")
            return None

    def qdsign(self) -> dict:
        """执行签到任务"""
        try:
            url = "https://druidv6.if.qidian.com/argus/api/v2/checkin/checkin"
            data = {
                'sessionKey': '',
                'banId': '0',
                'captchaTicket': '',
                'captchaRandStr': '',
                'challenge': '',
                'validate': '',
                'seccode': '',
            }
            
            result = self._make_qd_request(url, data=data, method='POST')
            
            if result.get('Result') == -91002:
                logger.info("签到成功")
                return {'status': 'success'}
                
            if result.get('is_captcha'):
                return {'status': 'captcha', 'captcha_data': result['captcha_data']}
                
            logger.error(f"签到失败: {result}")
            return {'status': 'failed'}
            
        except Exception as e:
            logger.error(f"签到任务异常: {e}")
            return {'status': 'error', 'error': str(e)}

    def get_adv_job(self) -> Dict[str, Any]:
        """获取激励任务列表"""
        url = "https://h5.if.qidian.com/argus/api/v1/video/adv/mainPage"
        result = self._make_sdk_request(url,method='GET')

        if not result.get('Data') or not result['Data'].get('VideoBenefitModule'):
            raise QidianError("获取激励任务列表失败")
            
        return result

    def do_adv_job(self, task_id: str) -> dict:
        """完成单个激励任务"""
        url = "https://h5.if.qidian.com/argus/api/v1/video/adv/finishWatch"
        data = {
            'taskId': task_id,
            'BanId': '0',
            'BanMessage': '',
            'CaptchaAId': '',
            'CaptchaType': '0',
            'CaptchaURL': '',
            'Challenge': '',
            'Gt': '',
            'NewCaptcha': '0',
            'Offline': '0',
            'PhoneNumber': '',
            'SessionKey': '',
        }
        
        result = self._make_sdk_request(url, data=data, method='POST')
        
        if result.get('is_captcha'):
            return {'status': 'captcha', 'captcha_data': result['captcha_data']}
        
        if result.get('Result') in (0, "0"):
            return {'status': 'success'}
        
        raise QidianError(f"激励任务执行失败: {result}")

    def advjob(self) -> dict:
        """执行激励碎片任务"""
        try:
            # 获取任务列表
            result = self.get_adv_job()
            task_list = result['Data']['VideoBenefitModule']['TaskList']
            
            # 如果所有任务已完成
            if task_list[-1]['IsFinished'] == 1:
                logger.info("激励碎片任务已经完成")
                return {'status': 'success'}
                
            # 执行未完成的任务
            for i, task in enumerate(task_list):
                if task['IsFinished'] == 0:
                    logger.info(f"正在执行第{i+1}个任务")
                    result = self.do_adv_job(task['TaskId'])
                    
                    if result.get('status') == 'success':
                        time.sleep(random.randint(1, 2))
                    elif result.get('status') == 'captcha':
                        logger.warning("遇到验证码")
                        return result  # 直接返回验证码信息
                    else:
                        logger.error("执行激励任务失败")
                        return {'status': 'failed'}
            
            # 验证任务是否全部完成
            check_result = self.get_adv_job()
            check_task_list = check_result['Data']['VideoBenefitModule']['TaskList']
            all_finished = all(task["IsFinished"] for task in check_task_list)
            
            if all_finished:
                logger.info("激励碎片任务完成")
                return {'status': 'success'}
                
            logger.error("激励碎片任务未完成")
            return {'status': 'failed', 'code': 10086}
            
        except Exception as e:
            logger.error(f"激励任务异常: {e}")
            return {'status': 'error', 'error': str(e)}
    def advjob_ex(self) -> dict:
        """执行额外激励碎片任务"""
        try:
            result = self.get_adv_job()
            task_result = self.do_adv_job("811164643405529088")
            
            if task_result.get('status') == 'success':
                reward_list = result.get('Data', {}).get('RewardList', [])
                if not reward_list:
                    logger.info("额外激励碎片任务完成")
                    return {'status': 'success'}
                    
                logger.error("额外激励碎片任务未完成")
                return {'status': 'failed', 'code': 10086}
                
            return task_result  # 返回原始结果
                
        except Exception as e:
            logger.error(f"额外激励任务异常: {e}")
            return {'status': 'error', 'error': str(e)}

    def exadvjob(self) -> dict:
        """执行额外章节卡任务"""
        try:
            # 获取任务列表
            result = self.get_adv_job()
            task_list = result['Data']['CountdownBenefitModule']['TaskList']
            
            for task in task_list:
                if task['Title'] == "额外看3次小视频得奖励":
                    if task['IsReceived'] == 1:
                        logger.info("额外章节卡任务已完成")
                        return {'status': 'success'}
                        
                    for i in range(3):
                        task_result = self.do_adv_job(task['TaskId'])
                        
                        if task_result.get('status') == 'success':
                            time.sleep(random.randint(1, 2))
                        elif task_result.get('status') == 'captcha':
                            logger.warning("遇到验证码")
                            return task_result
                        else:
                            logger.error("执行额外章节卡任务失败")
                            continue
                
            # 检查任务状态
            check_result = self.get_adv_job()
            check_task_list = check_result['Data']['CountdownBenefitModule']['TaskList']
            
            for task in check_task_list:
                if task['Title'] == "额外看3次小视频得奖励":
                    if task['IsReceived'] == 1:
                        logger.info("额外章节卡任务完成")
                        return {'status': 'success'}
                        
                    logger.error("额外章节卡任务未完成")
                    return {'status': 'failed', 'code': 10086}
                    
            return {'status': 'success'}
            
        except Exception as e:
            logger.error(f"额外章节卡任务异常: {e}")
            return {'status': 'error', 'error': str(e)}

    def lottery(self) -> dict:
        """执行每日抽奖任务"""
        try:
            url = "https://h5.if.qidian.com/argus/api/v2/checkin/detail"
            result = self._make_sdk_request(url, method='GET')
            
            video_chance = result['Data']['LotteryInfo']['HasVideoUrge']
            lottery_chance = result['Data']['LotteryInfo']['LotteryCount']
            
            if lottery_chance == 0 and video_chance == 0:
                logger.info("抽奖机会已用完")
                return {'status': 'success'}
                
            logger.info(f"观看视频机会: {video_chance}次, 抽奖机会: {lottery_chance}次")
            
            for i in range(video_chance):
                url_video = "https://h5.if.qidian.com/argus/api/v2/video/callback"
                data_video = {
                    'sessionKey': '',
                    'banId': '0',
                    'captchaTicket': '',
                    'captchaRandStr': '',
                    'challenge': '',
                    'validate': '',
                    'seccode': '',
                    'appId': '1002',
                    'adId': '6050165817126400',
                    'videoSucc': '1',
                }
                
                video_result = self._make_sdk_request(url_video, data=data_video, method='POST')
                
                if video_result.get('is_captcha'):
                    return {'status': 'captcha', 'captcha_data': video_result['captcha_data']}
                
                if video_result.get('Result') in (0, "0"):
                    logger.info(f"观看第{i+1}次视频成功")
                    time.sleep(random.randint(1, 2))
                else:
                    logger.error("观看抽奖视频失败")
                    return {'status': 'failed'}
            
            url_lottery = "https://h5.if.qidian.com/argus/api/v2/checkin/lottery"
            data_lottery = {
                'sessionKey': '',
                'banId': '0',
                'captchaTicket': '',
                'captchaRandStr': '',
                'challenge': '',
                'validate': '',
                'seccode': '',
            }
            
            total_chance = lottery_chance + video_chance
            for i in range(total_chance):
                lottery_result = self._make_sdk_request(url_lottery, data=data_lottery, method='POST')
                
                if lottery_result.get('is_captcha'):
                    return {'status': 'captcha', 'captcha_data': lottery_result['captcha_data']}
                
                if lottery_result.get('Result') == 0:
                    logger.info(f"第{i+1}次抽奖成功")
                    time.sleep(random.randint(1, 2))
                else:
                    logger.error("抽奖失败")
                    return {'status': 'failed'}
            
            check_result = self._make_sdk_request(url, method='GET')
            check_video = check_result['Data']['LotteryInfo']['HasVideoUrge']
            check_lottery = check_result['Data']['LotteryInfo']['LotteryCount']
            
            if check_video == 0 and check_lottery == 0:
                logger.info("抽奖任务完成")
                return {'status': 'success'}
                
            logger.error("抽奖任务未完成")
            return {'status': 'failed', 'code': 10086}
            
        except Exception as e:
            logger.error(f"抽奖任务异常: {e}")
            return {'status': 'error', 'error': str(e)}
    
    # 其他核心功能方法...

class TaskProcessor:
    """任务处理器"""
    def __init__(self, client: QidianClient, user: UserConfig, retry_attempts: int = 3):
        self.client = client
        self.user = user
        self.task_results = {}
        self.retry_attempts = retry_attempts  # 从全局配置中获取
    
    def run_task(self, task_name: str, task_func: Callable) -> None:
        """运行单个任务"""
        if not self.user.tasks.get(task_name, False):
            logger.info(f"任务[{task_name}]已禁用，跳过执行")
            return
            
        logger.info(f"开始执行任务: {task_name}")
        for attempt in range(1, self.retry_attempts + 1):
            logger.info(f"开始第{attempt}次尝试")
            try:
                result = task_func()

                if isinstance(result, dict):
                    status = result.get('status')
                    if status == 'success':
                        logger.info(f"任务[{task_name}]执行完成: 成功")
                        self.task_results[task_name] = result
                        break
                    elif status == 'captcha':
                        logger.warning(f"任务[{task_name}]因验证码中断")
                        self.task_results[task_name] = result
                        break
                    else:
                        if attempt < self.retry_attempts:
                            logger.warning(f"任务[{task_name}]第{attempt}次执行失败，正在重试...")
                            time.sleep(random.uniform(1, 2))
                        else:
                            logger.error(f"任务[{task_name}]执行失败，已达到最大重试次数")
                            self.task_results[task_name] = result
                else:
                    logger.error(f"任务[{task_name}]返回格式错误")
                    self.task_results[task_name] = {'status': 'failed', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
                    break

            except Exception as e:
                if attempt < self.retry_attempts:
                    logger.warning(f"任务[{task_name}]第{attempt}次执行异常: {e}，正在重试...")
                    time.sleep(random.uniform(1, 2))
                else:
                    logger.error(f"任务[{task_name}]执行异常: {e}")
                    self.task_results[task_name] = {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
    
    def process_all_tasks(self) -> Dict[str, Any]:
        """处理所有任务"""
        tasks = [
            ('签到任务', self.client.qdsign),
            ('激励碎片任务', self.client.advjob),
            ('额外激励任务', self.client.advjob_ex),
            ('章节卡任务', self.client.exadvjob),
            ('每日抽奖任务', self.client.lottery)
            # ('其他任务', self.other_task_func),
            # 添加其他任务...
        ]
        
        for task_name, task_func in tasks:
            self.run_task(task_name, task_func)
        
        return self.task_results

class MainApp:
    """主程序"""
    def __init__(self):
        self.config_manager = None  # 延迟初始化

    def pre_check(self) -> bool:
        """运行前的文件存在性检查"""
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"配置文件 {CONFIG_FILE} 不存在，请检查路径是否正确")
            return False

        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for user_data in config.get('users', []):
                username = user_data.get('username', '未知')
                cookies_file = user_data.get('cookies_file', f"{COOKIES_DIR}/{username}.json")
                if not os.path.exists(cookies_file):
                    logger.error(f"用户 [{username}] 的 cookies 文件 {cookies_file} 不存在")
                    return False

        except Exception as e:
            logger.error(f"读取配置文件失败: {e}")
            return False

        return True
    
    def handle_captcha(self, user: UserConfig, captcha_data: dict) -> None:
        """验证码处理钩子（预留）"""
        logger.warning(f"用户[{user.username}] 触发验证码拦截")
        logger.info(f"验证码参数: {json.dumps(captcha_data, ensure_ascii=False)}")
        # TODO: 后续在此实现验证码处理逻辑

    def run(self) -> None:
        """运行程序"""
        global logger
        # 获取基础日志系统（已初始化）
        logger = LoggerManager().logger

        if not self.pre_check():
            logger.error("预检查失败，程序终止")
            return
        
        # 初始化 ConfigManager
        self.config_manager = ConfigManager()
        config = self.config_manager.config

        # 初始化日志系统
        log_level = config.get('log_level', 'INFO')
        log_retention_days = config.get('log_retention_days', DEFAULT_LOG_RETENTION)
        logger = LoggerManager().reconfigure_logger(log_level, log_retention_days)

        # 继续执行主流程
        for user in self.config_manager.users:
            logger.info(f"开始处理用户: {user.username}")
            try:
                # 初始化客户端
                client = QidianClient(user)
                
                # 检查登录状态
                nickname = client.check_login()
                if not nickname:
                    logger.warning(f"用户[{user.username}]未登录")
                    continue
                
                logger.info(f"用户[{nickname}]登录成功")

                retry_attempts = self.config_manager.config.get('retry_attempts', 3)
                
                # 处理任务
                processor = TaskProcessor(client, user, retry_attempts)
                results = processor.process_all_tasks()

                # 检测验证码并处理
                for task_name, result in results.items():
                    if isinstance(result, dict) and result.get('status') == 'captcha':
                        self.handle_captcha(user, result.get('captcha_data', {}))
                        break  # 遇到验证码后停止后续任务
                
                # 发送通知
                self._send_notification(user, results)
                
                # 保存cookies
                # self.config_manager.save_cookies(user.username, client.session.cookies.get_dict())
                
            except Exception as e:
                logger.error(f"处理用户[{user.username}]时发生错误: {e}")
    
    def _send_notification(self, user: UserConfig, results: Dict[str, Any]) -> None:
        """发送通知"""
        if not user.push_services:
            logger.debug(f"用户[{user.username}]未配置推送服务")
            return
            
        # 构造消息内容
        msg = f"用户[{user.username}]任务完成情况:\n"
        success_count = 0
        total_count = len(results)
        has_captcha = False

        for task_name, result in results.items():
            if isinstance(result, dict):
                status = result.get('status')
                if status == 'success':
                    emoji = '✅'
                elif status == 'captcha':
                    emoji = '⚠️'
                    has_captcha = True
                else:
                    emoji = '❌'
                msg += f"{task_name}: {emoji}\n"
                if status == 'success':
                    success_count += 1
            else:
                msg += f"{task_name}: ❌\n"

        if has_captcha:
            msg += "\n⚠️ 注意：任务因遇到验证码被中断，后续任务未执行\n      手动执行一次任务后可解除风控"

        title = f"任务完成报告 - {success_count}/{total_count}"
        
        # 发送所有推送服务
        for push_service in user.push_services:
            service_name = push_service.__class__.__name__
            try:
                result = push_service.send(title, msg)
                if result.get('success'):
                    logger.info(f"[{service_name}] 推送成功")
                else:
                    logger.info(f"[{service_name}] 推送失败")
                    logger.debug(f"[{service_name}] 原始返回: {result.get('raw')}")
            except Exception as e:
                logger.error(f"[{service_name}] 推送异常: {str(e)}")

if __name__ == "__main__":
    app = MainApp()
    app.run()