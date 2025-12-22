import tkinter as tk
from tkinter import ttk, messagebox
import os, re
import json
import time
import webbrowser, threading
from Login import QDLogin_PhoneCode, QDLogin_Password, get_random_phone, check_login_status, check_login_risk, check_user_status

import sys
import os
import platform

system = platform.system()
if system == "Windows":
    sys_run = 1
elif system == "Linux":
    sys_run = 2
else:
    sys_run = 3


def resource_path(relative_path):
    """ 获取资源的绝对路径。适用于开发环境和PyInstaller打包后 """
    try:
        # PyInstaller创建的临时文件夹
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ConfigEditor:

    MAX_USERS = 3  # 类级常量，限制最大用户数
    DEFAULT_COOKIES_TEMPLATE = {
        "appId": "",
        "areaId": "",
        "lang": "",
        "mode": "",
        "bar": "",
        "qidth": "",
        "qid": "",
        "ywkey": "",
        "ywguid": "",
        "cmfuToken": "",
        "QDInfo": ""
    }

    def __init__(self, root):
        # 用于保存登录状态
        self.login_instance = None
        self.session_key = None

        self.root = root
        self.root.title("QDjob配置编辑器")

        # 设置窗口图标和初始尺寸
        self.root.geometry("1000x800")

        # 设置统一字体
        self.default_font = ("微软雅黑", 12)
        self.root.option_add("*Font", self.default_font)
        self.root.option_add("*Menu.font", self.default_font)  
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # 启用DPI感知（Windows系统）
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

        # 初始化主题样式
        self.init_styles()
        
        # 初始化配置数据
        self.config_data = self.load_config()
        self.users_data = self.config_data.get("users", [])
        for user in self.users_data:
            user.setdefault("ibex", "")
        
        # 创建主界面
        self.create_ui()

    def init_styles(self):
        """初始化主题样式"""
        style = ttk.Style()
        
        if sys_run == 1:  # Windows系统
            style.theme_use('vista')
        elif sys_run == 2:  # Linux系统
            style.theme_use('clam')
        else:  # macOS系统
            style.theme_use('default')
        # # 设置主题
        # style.theme_use('vista')
        
        # 配置Treeview样式
        style.configure("Treeview", 
                    rowheight=30, 
                    borderwidth=0,
                    font=self.default_font)
        style.configure("Treeview.Heading", 
                    font=(self.default_font[0], self.default_font[1], "bold"),
                    padding=(5, 5, 5, 5))
        
        # 配置按钮样式
        style.configure("Accent.TButton", 
                    padding=6,
                    relief="flat",
                    background="#4a90e2",
                    font=self.default_font)
        style.map("Accent.TButton",
                background=[('active', '#357abd')])
        
        # 配置输入框样式
        style.configure("Custom.TEntry", 
                    padding=5,
                    relief="flat",
                    borderwidth=1,
                    font=self.default_font)
        
        # 配置标签样式
        style.configure("Help.TLabel",
                    foreground="gray",
                    font=(self.default_font[0], self.default_font[1] - 1))
        
        # 配置复选框样式
        style.configure("TCheckbutton",
                    font=self.default_font)
        
        # 配置标签框架样式
        style.configure("TLabelFrame",
                    font=self.default_font)
        
        # 配置标签框架内部标签样式
        style.configure("TLabelFrame.Label",
                    font=self.default_font)
        
        # 配置Combobox样式
        style.configure("TCombobox", 
                    font=self.default_font,
                    padding=5)
        style.map("TCombobox",
                fieldbackground=[('readonly', 'white')])  # 固定背景色

    
    def load_config(self):
        """加载或初始化配置文件"""
        if not os.path.exists("config.json"):
            # 创建默认配置
            default_config = {
                "default_user_agent": "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0  QDNightStyle_1  QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading",
                "log_level": "INFO",
                "log_retention_days": 7,
                "retry_attempts": 3,
                "users": []
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2)
            os.makedirs("cookies", exist_ok=True)
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def create_ui(self):
        """创建主界面"""
        # 配置区域
        config_frame = ttk.LabelFrame(self.root, text="全局配置")
        config_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # 配置网格权重
        config_frame.grid_rowconfigure(0, weight=1)
        config_frame.grid_rowconfigure(1, weight=1)
        config_frame.grid_rowconfigure(2, weight=1)
        config_frame.grid_columnconfigure(1, weight=1)

        # default_user_agent
        ttk.Label(config_frame, text="默认User Agent:").grid(row=0, column=0, sticky="w", pady=10)
        self.ua_var = tk.StringVar(value=self.config_data["default_user_agent"])
        ua_entry = ttk.Entry(config_frame, 
                            textvariable=self.ua_var,
                            style="Custom.TEntry")
        ua_entry.grid(row=0, column=1, sticky="ew", pady=10)
        ttk.Label(config_frame, text="💡", style="Help.TLabel").grid(row=0, column=2, sticky="w", pady=10)
        ttk.Label(config_frame, text="浏览器标识字符串", style="Help.TLabel").grid(row=0, column=3, sticky="w", pady=10)

        # log_level
        ttk.Label(config_frame, text="日志等级:").grid(row=1, column=0, sticky="w", pady=10)
        self.log_level_var = tk.StringVar(value=self.config_data["log_level"])
        log_level_combo = ttk.Combobox(config_frame,
                                    textvariable=self.log_level_var,
                                    values=["INFO", "DEBUG", "ERROR"],
                                    state="readonly",
                                    width=10)
        log_level_combo.grid(row=1, column=1, sticky="w", pady=10)

        ttk.Label(config_frame, text="💡", style="Help.TLabel").grid(row=1, column=2, sticky="w", pady=10)
        ttk.Label(config_frame, text="日志输出等级", style="Help.TLabel").grid(
                    row=1, column=3, sticky="w", pady=10)

        # 数值配置
        num_frame = ttk.Frame(config_frame)
        num_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=10)
        
        # 配置网格权重
        num_frame.grid_columnconfigure(0, weight=0)  # 日志保留天数标签列
        num_frame.grid_columnconfigure(1, weight=1)  # Spinbox列
        num_frame.grid_columnconfigure(2, weight=0)  # 单位列
        num_frame.grid_columnconfigure(3, weight=0)  # 重试次数标签列
        num_frame.grid_columnconfigure(4, weight=1)  # Spinbox列
        num_frame.grid_columnconfigure(5, weight=0)  # 单位列

        # 日志保留天数
        ttk.Label(num_frame, text="日志保留天数:").grid(row=0, column=0, sticky="w", padx=0)
        self.log_days_var = tk.IntVar(value=self.config_data["log_retention_days"])

        # 使用 Frame 包裹 Spinbox 和单位标签
        days_container = ttk.Frame(num_frame)
        days_container.grid(row=0, column=1, sticky="w")
        ttk.Spinbox(days_container, from_=1, to=30, 
                    textvariable=self.log_days_var, width=5).pack(side="left")
        ttk.Label(days_container, text="天", style="Help.TLabel").pack(side="left", padx=2)

        # 重试次数
        ttk.Label(num_frame, text="失败重试次数:").grid(row=0, column=2, sticky="w", padx=0)
        self.retry_var = tk.IntVar(value=self.config_data["retry_attempts"])

        # 使用 Frame 包裹 Spinbox 和单位标签
        retries_container = ttk.Frame(num_frame)
        retries_container.grid(row=0, column=3, sticky="w")
        ttk.Spinbox(retries_container, from_=1, to=10, 
                    textvariable=self.retry_var, width=5).pack(side="left")
        ttk.Label(retries_container, text="次", style="Help.TLabel").pack(side="left", padx=2)
        
        # 用户管理
        user_frame = ttk.LabelFrame(self.root, text="用户管理")
        user_frame.pack(padx=10, pady=5, fill="both", expand=True)
        
        # 配置网格权重
        user_frame.grid_columnconfigure(0, weight=1)
        user_frame.grid_rowconfigure(0, weight=1)

        # 用户列表
        columns = ("username", "user_agent", "cookies_status")
        self.user_list = ttk.Treeview(user_frame, columns=columns, show="headings")
        self.user_list.heading("username", text="用户名", anchor="center")
        self.user_list.heading("user_agent", text="User Agent", anchor="center")
        self.user_list.heading("cookies_status", text="Cookies状态", anchor="center")
        self.user_list.column("username", width=150, anchor="center")
        self.user_list.column("user_agent", width=200, anchor="center")
        self.user_list.column("cookies_status", width=150, anchor="center")
        self.user_list.pack(side="left", fill="both", expand=True)

        # 滚动条
        scrollbar = ttk.Scrollbar(user_frame, orient="vertical", command=self.user_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.user_list.configure(yscrollcommand=scrollbar.set)

        # 按钮区域
        btn_frame = ttk.Frame(user_frame)
        btn_frame.pack(side="bottom", fill="x", pady=5)

        ttk.Button(btn_frame, text="添加用户", style="Accent.TButton", 
                command=self.add_user).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="编辑用户", style="Accent.TButton",
                command=self.edit_user).pack(fill="x", pady=2)
        ttk.Button(btn_frame, text="删除用户", style="Accent.TButton",
                command=self.remove_user).pack(fill="x", pady=2)
        
        ttk.Button(btn_frame, text="tokenid状态", style="Accent.TButton",
            command=self.check_user_status_for_selected_user).pack(fill="x", pady=2)
        
        ttk.Button(btn_frame, text="检测登录状态", style="Accent.TButton",
            command=self.check_login_status_for_selected_user).pack(fill="x", pady=2)
        
        ttk.Button(btn_frame, text="检测风险状态", style="Accent.TButton",
            command=self.check_login_risk_for_selected_user).pack(fill="x", pady=2)

        # 初始化用户列表显示
        self.refresh_user_list()

        # 创建按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10, fill="x")

        # 保存配置按钮（保持与添加用户按钮相同的宽度）
        save_button = ttk.Button(
            button_frame,
            text="保存配置",
            style="Accent.TButton",
            command=self.save_config,
            width=20  # 固定宽度，与添加用户按钮一致
        )
        save_button.pack(side="left", padx=5, expand=True, fill="x")

        # 执行任务按钮
        execute_button = ttk.Button(
            button_frame,
            text="执行任务",
            style="Accent.TButton",
            command=self.execute_task,
            width=20  # 保持相同宽度
        )
        execute_button.pack(side="right", padx=5, expand=True, fill="x")

        # 创建作者信息框架
        author_frame = ttk.LabelFrame(self.root, text="项目信息")
        author_frame.pack(padx=10, pady=5, fill="x", expand=False)

        # 使用grid布局排列信息
        ttk.Label(author_frame, text="作者: JaniQuiz      项目: QDjob", font=("微软雅黑", 10)).grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(author_frame, text="本项目为个人项目，仅供学习交流使用，请勿用于非法用途，如有侵权，请联系删除。", font=("微软雅黑", 10)).grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        
        # 添加声明文本
        ttk.Label(author_frame, text="图形验证码自动处理功能需要获取tokenid，您可以在我的咸鱼上购买", font=("微软雅黑", 10), ).grid(
            row=2, column=0, sticky="w", padx=5, pady=2)

        # 创建超链接标签
        github_link = ttk.Label(author_frame, text="GitHub: https://github.com/JaniQuiz/QDjob",
                            foreground="blue", cursor="hand2", font=("微软雅黑", 10))
        github_link.grid(row=3, column=0, sticky="w", padx=5, pady=2)
        
        telegram_link = ttk.Label(author_frame, text="Telegram: https://t.me/+6xMW_7YK0o1jMDE1",
                            foreground="blue", cursor="hand2", font=("微软雅黑", 10))
        telegram_link.grid(row=3, column=1, sticky="w", padx=5, pady=2)

        xianyu_link = ttk.Label(author_frame, text="咸鱼: https://www.goofish.com/item?id=1000811249803",
                            foreground="blue", cursor="hand2", font=("微软雅黑", 10))
        xianyu_link.grid(row=5, column=0, sticky="w", padx=5, pady=2)

        # 绑定超链接点击事件
        def callback(event):
            webbrowser.open_new(r"https://github.com/JaniQuiz/QDjob")

        github_link.bind("<Button-1>", callback)

    def refresh_user_list(self):
        """刷新用户列表显示"""
        # 清空现有列表
        for item in self.user_list.get_children():
            self.user_list.delete(item)
        
        # 重新加载用户数据
        for user in self.users_data:
            # 检查Cookies文件状态
            cookies_path = user.get("cookies_file", "")
            
            if cookies_path and os.path.exists(cookies_path):
                try:
                    with open(cookies_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析JSON
                    try:
                        cookies_data = json.loads(content)
                        
                        # 检查是否所有字段都为空
                        if isinstance(cookies_data, dict) and all(
                            isinstance(v, str) and v.strip() == "" 
                            for v in cookies_data.values()
                        ):
                            cookies_status = "账号未配置"
                        else:
                            cookies_status = "账号已配置"
                    except json.JSONDecodeError:
                        cookies_status = "格式错误"
                except Exception as e:
                    cookies_status = "读取失败"
            else:
                cookies_status = "账号未配置"
                
            # Token状态检查
            token_status = "未验证" if not user.get("token") else "已验证"
            
            self.user_list.insert("", "end", values=(
                user["username"],
                # user["user_agent"] or "默认User Agent",
                user.get("user_agent", "默认User Agent"),
                cookies_status,
                token_status  # 新增Token状态
            ))

    def check_user_status_for_selected_user(self):
        """检查用户状态"""
        selected = self.user_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        index = self.user_list.index(selected[0])
        user = self.users_data[index]
        username = user["username"]
        
        # 检查tokenid状态
        tokenid = user.get("tokenid", "")
        if not tokenid:
            messagebox.showwarning("警告", f"用户 '{username}' 的tokenid未配置")
            return
        
        # 检测usertype状态
        usertype = user.get("usertype", "")
        if not usertype:
            messagebox.showwarning("警告", f"用户 '{username}' 的usertype未配置")
            return
        try:
            data = check_user_status(tokenid, usertype)
            if not data:
                messagebox.showwarning("警告", f"用户 '{username}' 的tokenid验证失败\n请检查日志")
                return
            expire_time = data.get("expire_time", "")
            remaining_calls = data.get("remaining_calls", "")
            if expire_time == "2099-01-01 00:00:00":
                expire_time = "无限制"
            if remaining_calls == -1:
                remaining_calls = "无限制"
            messagebox.showinfo("用户信息", f"用户 '{username}' 的tokenid已验证成功\n有效期: {expire_time}\n剩余调用次数: {remaining_calls}")
            return
        except Exception as e:
            messagebox.showwarning("警告", f"用户 '{username}' 的usertype验证失败: {e}")
            return
        


    def check_login_status_for_selected_user(self):
        """检测选中用户的登录状态"""
        selected = self.user_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        index = self.user_list.index(selected[0])
        user = self.users_data[index]
        username = user["username"]
        
        # 检查cookies状态
        cookies_file = user.get("cookies_file", "")
        if not cookies_file or not os.path.exists(cookies_file):
            messagebox.showwarning("警告", f"用户 '{username}' 的cookies未配置")
            return
        
        # 获取cookies
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查内容是否为空
            if not content.strip():
                messagebox.showwarning("警告", f"用户 '{username}' 的cookies文件为空")
                return
            
            cookies = json.loads(content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"cookies文件格式错误: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror("错误", f"无法读取cookies文件: {str(e)}")
            return
        
        # 获取user_agent
        user_agent = user.get("user_agent", "")
        if not user_agent:
            # 使用config.json中的默认UA
            user_agent = self.config_data["default_user_agent"]
            if not user_agent:
                # 如果config.json中也没有配置，默认使用一个基本格式
                user_agent = "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0 QDNightStyle_1 QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading"
        
        # 调用check_login_status函数
        try:
            is_logged_in = check_login_status(user_agent, cookies)
            if is_logged_in:
                messagebox.showinfo("登录状态", f"用户 '{username}' 已登录✅", icon='info')
            else:
                messagebox.showwarning("登录状态", f"用户 '{username}' 未登录或登录已过期⚠️", icon='warning')
        except Exception as e:
            messagebox.showerror("错误", f"检测登录状态时出错: {str(e)}", icon='error')

    def check_login_risk_for_selected_user(self):
        """检测选中用户的登录风险状态"""
        selected = self.user_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        index = self.user_list.index(selected[0])
        user = self.users_data[index]
        username = user["username"]
        
        # 检查cookies状态
        cookies_file = user.get("cookies_file", "")
        if not cookies_file or not os.path.exists(cookies_file):
            messagebox.showwarning("警告", f"用户 '{username}' 的cookies未配置")
            return
        
        # 获取cookies
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查内容是否为空
            if not content.strip():
                messagebox.showwarning("警告", f"用户 '{username}' 的cookies文件为空")
                return
            
            cookies = json.loads(content)
        except json.JSONDecodeError as e:
            messagebox.showerror("错误", f"cookies文件格式错误: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror("错误", f"无法读取cookies文件: {str(e)}")
            return
        
        # 获取user_agent
        user_agent = user.get("user_agent", "")
        if not user_agent:
            # 使用config.json中的默认UA
            user_agent = self.config_data["default_user_agent"]
            if not user_agent:
                # 如果config.json中也没有配置，默认使用一个基本格式
                user_agent = "Mozilla/5.0 (Linux; Android 13; PDEM10 Build/TP1A.220905.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/109.0.5414.86 MQQBrowser/6.2 TBS/047601 Mobile Safari/537.36 QDJSSDK/1.0 QDNightStyle_1 QDReaderAndroid/7.9.384/1466/1000032/OPPO/QDShowNativeLoading"
        
        ibex = user.get("ibex", "")
        if not ibex:
            messagebox.showwarning("警告", f"用户 '{username}' 的ibex未配置")
            return

        # 调用check_login_status函数
        try:
            is_logged_in = check_login_risk(user_agent, cookies, ibex)
            if is_logged_in==True:
                messagebox.showinfo("风险状态", f"用户 '{username}' 无风险情况", icon='info')
            elif is_logged_in==False:
                messagebox.showwarning("风险状态", f"用户 '{username}' 获取风险情况失败", icon='warning')
            else:
                messagebox.showwarning("风险状态", f"用户 '{username}' 有风险情况⚠️\n {str(is_logged_in)}", icon='warning')
        except Exception as e:
            messagebox.showerror("错误", f"检测风险状态时出错: {str(e)}", icon='error')

    def validate_username(self, username):
        """验证用户名是否符合格式要求"""
        if not username:
            return False, "用户名不能为空"
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$', username):
            return False, "用户名格式错误！\n要求：\n1. 2-20个字符\n2. 仅支持中文、字母、数字和下划线"
        return True, ""
    
    def get_user_cookies(self, username):
        """获取指定用户的cookies内容"""
        # 查找用户
        user = next((u for u in self.users_data if u["username"] == username), None)
        if not user:
            return None
        
        cookies_file = user.get("cookies_file", "")
        if not cookies_file or not os.path.exists(cookies_file):
            return None
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                content = f.read()
            cookies_data = json.loads(content)
            return cookies_data
        except Exception:
            return None
        
    def save_user_to_config(self, username, ua, ibex, cookies_file):
        """
        保存用户信息到config.json
        如果用户不存在则添加，存在则更新
        """
        # 检查用户是否存在
        user_exists = False
        for user in self.users_data:
            if user["username"] == username:
                user_exists = True
                # 更新现有用户
                user.update({
                    "user_agent": ua,
                    "ibex": ibex,
                    "cookies_file": cookies_file
                })
                break
        
        # 如果不存在，创建新用户
        if not user_exists:
            new_user = {
                "username": username,
                "cookies_file": cookies_file,
                "user_agent": ua,
                "ibex": ibex,
                "usertype": "captcha",  # 默认值
                "tokenid": "",  # 可能需要从其他地方获取
                "tasks": {
                    "签到任务": True,
                    "激励碎片任务": True,
                    "章节卡任务": True,
                    "游戏中心任务": True,
                    "每日抽奖任务": True
                },
                "push_services": []
            }
            self.users_data.append(new_user)
        
        # 保存配置
        self.save_users_config()
    
    def getdevice(self):
        """获取随机设备信息函数"""
        login_phone = get_random_phone()
        if not login_phone:
            return None
        return login_phone
    
    def show_phone_login_dialog(self, parent, username):
        """显示手机验证码登录对话框"""
        # 验证用户名
        is_valid, message = self.validate_username(username)
        if not is_valid:
            messagebox.showerror("错误", message)
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("手机验证码登录")
        dialog.geometry("800x650")

        # 关键设置：确保对话框是模态的
        dialog.transient(parent)  # 设置为临时窗口（关联到父窗口）
        dialog.grab_set()         # 捕获所有事件，使对话框成为模态
        dialog.focus_set()        # 将焦点设置到对话框
        dialog.lift()             # 确保对话框显示在最上层
        
        form_frame = ttk.Frame(dialog, padding="20 15 20 15")
        form_frame.pack(fill="both", expand=True)

        # 在创建对话框的底部添加状态提示区域（在原有代码基础上添加）
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        self.status_label = ttk.Label(status_frame, text="", font=self.default_font)
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)
        self.status_label.pack(side="left", padx=5)
        
        # 手机号输入
        ttk.Label(form_frame, text="手机号:").grid(row=0, column=0, sticky="w", pady=5)
        phone_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=phone_var, style="Custom.TEntry", width=20).grid(row=0, column=1, sticky="w", pady=5)
        
        # 获取设备信息按钮
        def get_device_info():
            # 调用getdevice函数
            device_data = self.getdevice()
            if device_data:
                device_text.config(state="normal")
                device_text.delete("1.0", "end")
                device_text.insert("1.0", json.dumps(device_data, indent=2, ensure_ascii=False))
                device_text.config(state="disabled")
        
        ttk.Button(form_frame, text="获取随机设备信息", style="Accent.TButton",
                command=get_device_info).grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # 获取验证码按钮
        def get_verification_code(phone_var, device_text):
            phone = phone_var.get().strip()
            if not phone:
                messagebox.showerror("错误", "请输入手机号")
                return
            
            # 检查设备信息输入框是否为空
            device_info = device_text.get("1.0", "end-1c").strip()
            if not device_info:
                messagebox.showerror("错误", "请先点击'获取随机设备信息'按钮获取设备信息")
                return
            
            # 尝试解析设备信息JSON
            try:
                login_phone = json.loads(device_info)
            except json.JSONDecodeError:
                messagebox.showerror("错误", "设备信息格式错误，请重新获取设备信息")
                return
            
            # 创建登录实例
            self.login_instance = QDLogin_PhoneCode(phonenum=phone)
            
            # 直接使用设备信息内容初始化
            if not self.login_instance.init_device_info(login_phone):
                messagebox.showerror("错误", "设备信息初始化失败")
                return
            
            # 显示加载状态
            self.status_label.config(text="获取验证码中……", foreground="blue")
            
            # 1. 先在主线程尝试发送验证码（可能不需要图形验证码）
            try:
                # 发送手机验证码
                status, data = self.login_instance.send_phonecode()
                
                # 2. 如果需要图形验证码，在主线程中处理
                if status == 'captcha':
                    self.session_key = data
                    self.status_label.config(text="需要图形验证码，请稍候...", foreground="blue")
                    
                    # 关键：在主线程中调用get_captcha（确保pywebview正常工作）
                    captcha_data = self.login_instance.get_captcha()
                    if not captcha_data:
                        self.status_label.config(text="获取图形验证码失败", foreground="red")
                        return
                        
                    # 使用图形验证码重新发送（仍在主线程）
                    status, data = self.login_instance.send_phonecode(
                        self.session_key, 
                        captcha_data['randstr'], 
                        captcha_data['ticket']
                    )
                    if status == 'captcha':
                        self.status_label.config(text="图形验证码验证失败", foreground="red")
                        return
                        
                    if status in [True, 'True']:
                        self.session_key = data
                        self.status_label.config(text="验证码已发送", foreground="green")
                    else:
                        self.status_label.config(text=f"验证码发送失败: {data}", foreground="red")
                elif status in [True, 'True']:
                    self.session_key = data
                    self.status_label.config(text="验证码已发送", foreground="green")
                else:
                    self.status_label.config(text=f"验证码发送失败: {data}", foreground="red")
            except Exception as e:
                self.status_label.config(text=f"验证码发送过程中出错: {str(e)}", foreground="red")
        
        # 获取验证码按钮
        ttk.Button(form_frame, text="获取验证码", style="Accent.TButton",
                command=lambda: get_verification_code(phone_var, device_text)
        ).grid(row=1, column=2, sticky="w", padx=5, pady=5)
    
        
        # 验证码输入
        ttk.Label(form_frame, text="验证码:").grid(row=1, column=0, sticky="w", pady=5)
        code_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=code_var, style="Custom.TEntry", width=20).grid(row=1, column=1, sticky="w", pady=5)
        
        # 登录按钮
        def login(phone_var, code_var, cookies_text, ua_var, ibex_var):
            phone = phone_var.get().strip()
            code = code_var.get().strip()
            if not phone or not code:
                messagebox.showerror("错误", "手机号和验证码不能为空")
                return
            
            # 显示加载状态
            self.status_label.config(text="登录中……", foreground="blue")
            
            # 在新线程中执行网络请求（不需要pywebview的部分）
            def login_thread():
                try:
                    # 验证手机验证码
                    status = self.login_instance.check_phonecode(self.session_key, code)
                    if not status:
                        self.root.after(0, lambda: self.status_label.config(
                            text="手机验证码验证失败", foreground="red"))
                        return
                    
                    # 完成登录
                    status = self.login_instance.login_druidv6()
                    if not status:
                        self.root.after(0, lambda: self.status_label.config(
                            text="登录druidv6.if.qidian.com失败", foreground="red"))
                        return
                    
                    # 获取cookies
                    cookies = self.login_instance.cookies
                    
                    # 通过主线程更新UI
                    self.root.after(0, lambda: _update_login_success(
                        cookies, cookies_text, ua_var, ibex_var))
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"登录过程中出错: {str(e)}", foreground="red"))
            
            threading.Thread(target=login_thread, daemon=True).start()

        def _update_login_success(cookies, cookies_text, ua_var, ibex_var):
            """在主线程中更新登录成功的UI"""
            # 更新cookies显示框
            cookies_text.config(state="normal")
            cookies_text.delete("1.0", "end")
            cookies_text.insert("1.0", json.dumps(cookies, indent=2, ensure_ascii=False))
            cookies_text.config(state="disabled")

            self.login_instance.gener_user_agent()
            
            # 更新User Agent和ibex显示
            ua_var.set(self.login_instance.user_agent)
            ibex_var.set(self.login_instance.gener_ibex_over(str(int(time.time() * 1000))))
            
            self.status_label.config(text="登录成功", foreground="green")
        
        # 修改登录按钮的绑定
        ttk.Button(form_frame, text="登录", style="Accent.TButton",
                command=lambda: login(phone_var, code_var, cookies_text, ua_var, ibex_var)
        ).grid(row=2, column=0, columnspan=3, pady=10)
        
        # 配置网格布局
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)
        form_frame.grid_rowconfigure(4, weight=1)
        
        # Cookies和设备信息显示区域（同一行）
        info_frame = ttk.LabelFrame(form_frame, text="Cookies和设备信息:")
        info_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # 左侧Cookies显示区域
        cookies_label = ttk.Label(info_frame, text="Cookies:")
        cookies_label.grid(row=0, column=0, sticky="w")
        
        cookies_text = tk.Text(info_frame, height=5, font=self.default_font, state="disabled")
        cookies_text.grid(row=1, column=0, sticky="nsew", padx=5)
        
        # 右侧设备信息显示区域
        device_label = ttk.Label(info_frame, text="设备信息:")
        device_label.grid(row=0, column=1, sticky="w")
        
        device_text = tk.Text(info_frame, height=10, font=self.default_font, state="disabled")
        device_text.grid(row=1, column=1, sticky="nsew", padx=5)

        # User Agent显示
        ttk.Label(form_frame, text="User Agent:").grid(row=4, column=0, sticky="w", pady=5)
        ua_var = tk.StringVar()
        ua_entry = ttk.Entry(form_frame, textvariable=ua_var, style="Custom.TEntry", state="readonly")
        ua_entry.grid(row=4, column=1, sticky="w", pady=5)

        # ibex显示
        ttk.Label(form_frame, text="ibex:").grid(row=5, column=0, sticky="w", pady=5)
        ibex_var = tk.StringVar()
        ibex_entry = ttk.Entry(form_frame, textvariable=ibex_var, style="Custom.TEntry", state="readonly")
        ibex_entry.grid(row=5, column=1, sticky="w", pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, sticky="e", pady=10)

        def load_existing_data():
            # 加载cookies
            cookies_data = self.get_user_cookies(username)
            if cookies_data:
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(cookies_data, indent=2, ensure_ascii=False))
                cookies_text.config(state="disabled")
            else:
                # 使用默认模板
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(self.__class__.DEFAULT_COOKIES_TEMPLATE, indent=2, ensure_ascii=False))
                cookies_text.config(state="disabled")
            
            # 加载设备信息
            device_file = f"login_phone_{username}.json"
            if os.path.exists(device_file):
                try:
                    with open(device_file, 'r', encoding='utf-8') as f:
                        device_data = json.load(f)
                    device_text.config(state="normal")
                    device_text.delete("1.0", "end")
                    device_text.insert("1.0", json.dumps(device_data, indent=2, ensure_ascii=False))
                    device_text.config(state="disabled")
                except Exception:
                    pass

            # 加载UA和ibex
            user = next((u for u in self.users_data if u["username"] == username), None)
            if user:
                ua_var.set(user.get("user_agent", ""))
                ibex_var.set(user.get("ibex", ""))

        # 在创建对话框后立即加载数据
        dialog.after(100, load_existing_data)
        
        def save_login_data():
            # 保存cookies和设备信息
            cookies_str = cookies_text.get("1.0", "end-1c")
            device_str = device_text.get("1.0", "end-1c")
            
            # 处理Cookies - 为空时使用默认模板
            if not cookies_str:
                cookies_data = self.__class__.DEFAULT_COOKIES_TEMPLATE
            else:
                try:
                    cookies_data = json.loads(cookies_str)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"JSON格式错误：{str(e)}")
                    return
            
            # 保存cookies到cookies/用户名.json
            cookies_file = f"cookies/{username}.json"
            try:
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("错误", f"无法保存Cookies文件：{str(e)}")
                return
            
            # 仅当设备信息非空时保存
            if device_str:
                try:
                    device_data = json.loads(device_str)
                    with open(f"login_phone_{username}.json", 'w', encoding='utf-8') as f:
                        json.dump(device_data, f, indent=2, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"设备信息JSON格式错误：{str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("错误", f"无法保存设备信息：{str(e)}")
                    return
            
            # 保存用户信息到config
            cookies_file = f"cookies/{username}.json"
            self.save_user_to_config(username, ua_var.get(), ibex_var.get(), cookies_file)
            
            messagebox.showinfo("成功", "数据保存成功")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="保存", style="Accent.TButton",
                command=save_login_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", style="Accent.TButton",
                command=dialog.destroy).pack(side="left", padx=5)
        
    def login_password(self, account, password):
        """账号密码登录函数（待实现）"""
        # TODO: 实现登录逻辑
        # 返回False表示失败，返回cookies的JSON数据表示成功
        return False

    def show_password_login_dialog(self, parent, username):
        """显示账号密码登录对话框"""
        # 验证用户名
        is_valid, message = self.validate_username(username)
        if not is_valid:
            messagebox.showerror("错误", message)
            return
        
        # 新增：检查设备信息文件是否存在
        device_file = f"login_phone_{username}.json"
        if not os.path.exists(device_file):
            messagebox.showerror("错误", f"login_phone_{username}.json不存在\n本功能用于便捷更新过期cookies，需要先进行手机验证码成功登录后才能使用")
            return
        
        # 检测设备信息文件是否为空
        if os.path.getsize(device_file) == 0:
            messagebox.showerror("错误", f"login_phone_{username}.json内容为空\n本功能用于便捷更新过期cookies，需要先进行手机验证码成功登录后才能使用")
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("账号密码登录")
        dialog.geometry("800x650")

        # 关键模态设置
        dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()
        
        form_frame = ttk.Frame(dialog, padding="20 15 20 15")
        form_frame.pack(fill="both", expand=True)
        
        # 账号输入
        ttk.Label(form_frame, text="账号:").grid(row=0, column=0, sticky="w", pady=5)
        account_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=account_var, style="Custom.TEntry", width=20).grid(row=0, column=1, sticky="w", pady=5)
        
        # 密码输入
        ttk.Label(form_frame, text="密码:").grid(row=1, column=0, sticky="w", pady=5)
        password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=password_var, style="Custom.TEntry", show="*", width=20).grid(row=1, column=1, sticky="w", pady=5)

        # 在创建对话框的底部添加状态提示区域（在原有代码基础上添加）
        status_frame = ttk.Frame(form_frame)
        status_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        self.status_label = ttk.Label(status_frame, text="", font=self.default_font)
        status_frame.grid_columnconfigure(0, weight=1)
        status_frame.grid_rowconfigure(0, weight=1)
        self.status_label.pack(side="left", padx=5)

        # # 获取设备信息按钮
        # def get_device_info():
        #     # 调用getdevice函数
        #     device_data = self.getdevice()
        #     if device_data:
        #         # 更新设备信息显示框
        #         device_text.config(state="normal")
        #         device_text.delete("1.0", "end")
        #         device_text.insert("1.0", json.dumps(device_data, indent=2, ensure_ascii=False))
        #         device_text.config(state="disabled")
        
        # ttk.Button(form_frame, text="获取随机设备信息", style="Accent.TButton",
        #         command=get_device_info).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # 登录按钮
        def login():
            device_info = device_text.get("1.0", "end-1c").strip()
            if not device_info:
                messagebox.showerror("错误", "设备信息为空，请先使用手机验证码登录成功并保存设备信息")
                return

            account = account_var.get().strip()
            password = password_var.get().strip()
            if not account or not password:
                messagebox.showerror("错误", "账号和密码不能为空")
                return
            
            # 尝试解析设备信息JSON
            try:
                login_phone = json.loads(device_info)
            except json.JSONDecodeError:
                messagebox.showerror("错误", "设备信息格式错误，请重新获取设备信息")
                return
            
            self.login_instance = QDLogin_Password(account=account, password=password)

            if not self.login_instance.init_device_info(login_phone):
                messagebox.showerror("错误", "设备信息初始化失败")
                return
            
            # 显示加载状态
            self.status_label.config(text="登录中……", foreground="blue")

            # 在新线程中执行网络请求
            def login_thread():
                try:
                    # 创建登录实例
                    self.login_instance = QDLogin_Password(account=account, password=password)
                    
                    # 检查设备信息文件
                    device_file = f"login_phone_{username}.json"
                    if not os.path.exists(device_file) or os.path.getsize(device_file) == 0:
                        self.root.after(0, lambda: messagebox.showerror("错误", "设备信息文件不存在或为空"))
                        return
                    
                    # 读取设备信息
                    with open(device_file, 'r') as f:
                        login_phone = json.load(f)
                    
                    if not self.login_instance.init_device_info(login_phone):
                        self.root.after(0, lambda: messagebox.showerror("错误", "设备信息初始化失败"))
                        return
                    
                    # 尝试静态登录
                    status, data = self.login_instance.static_login()
                    
                    # 处理需要图形验证码的情况
                    if status == 'captcha':
                        self.session_key = data
                        self.root.after(0, lambda: self.status_label.config(
                            text="需要图形验证码，请稍候...", foreground="blue"))
                        
                        # 关键：在主线程中调用get_captcha
                        captcha_data = None
                        event = threading.Event()
                        
                        def get_captcha_in_main_thread():
                            nonlocal captcha_data
                            captcha_data = self.login_instance.get_captcha()
                            event.set()  # 通知子线程继续
                        
                        self.root.after(0, get_captcha_in_main_thread)
                        
                        # 等待主线程完成get_captcha
                        event.wait()
                        
                        if not captcha_data:
                            self.root.after(0, lambda: self.status_label.config(
                                text="获取图形验证码失败", foreground="red"))
                            return
                        
                        # 使用图形验证码重新登录
                        status, data = self.login_instance.login_with_captcha(
                            self.session_key,
                            captcha_data['randstr'],
                            captcha_data['ticket']
                        )
                        
                        if status in [True, 'True']:
                            self.session_key = data
                            self.root.after(0, lambda: self.status_label.config(
                                text="登录成功", foreground="green"))
                        else:
                            self.root.after(0, lambda: self.status_label.config(
                                text=f"图形验证码校验失败: {data}", foreground="red"))
                            return
                    
                    elif status in [True, 'True']:
                        self.session_key = data
                        self.root.after(0, lambda: self.status_label.config(
                            text="登录成功", foreground="green"))
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"登录失败: {data}", foreground="red"))
                        return
                    
                    # 完成登录
                    status = self.login_instance.login_druidv6()
                    if not status:
                        self.root.after(0, lambda: self.status_label.config(
                            text="登录druidv6.if.qidian.com失败", foreground="red"))
                        return
                    
                    # 获取cookies
                    cookies = self.login_instance.cookies
                    
                    # 通过主线程更新UI
                    def update_ui():
                        # 更新cookies显示框
                        cookies_text.config(state="normal")
                        cookies_text.delete("1.0", "end")
                        cookies_text.insert("1.0", json.dumps(cookies, indent=2, ensure_ascii=False))
                        cookies_text.config(state="disabled")
                        
                        self.login_instance.gener_user_agent()
                        
                        # 更新User Agent和ibex显示
                        ua_var.set(self.login_instance.user_agent)
                        ibex_var.set(self.login_instance.gener_ibex_over(str(int(time.time() * 1000))))
                        
                        self.status_label.config(text="登录成功", foreground="green")
                    
                    self.root.after(0, update_ui)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"登录过程中出错: {str(e)}", foreground="red"))
            
            # 启动子线程
            threading.Thread(target=login_thread, daemon=True).start()
        
        ttk.Button(form_frame, text="登录", style="Accent.TButton",
                command=login).grid(row=2, column=0, columnspan=3, pady=10)
        
        # 配置网格布局
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)
        form_frame.grid_rowconfigure(4, weight=1)
        
        # Cookies和设备信息显示区域（同一行）
        info_frame = ttk.LabelFrame(form_frame, text="Cookies和设备信息:")
        info_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        
        # 左侧Cookies显示区域
        cookies_label = ttk.Label(info_frame, text="Cookies:")
        cookies_label.grid(row=0, column=0, sticky="w")
        
        cookies_text = tk.Text(info_frame, height=5, font=self.default_font, state="disabled")
        cookies_text.grid(row=1, column=0, sticky="nsew", padx=5)
        
        # 右侧设备信息显示区域
        device_label = ttk.Label(info_frame, text="设备信息:")
        device_label.grid(row=0, column=1, sticky="w")
        
        device_text = tk.Text(info_frame, height=10, font=self.default_font, state="disabled")
        device_text.grid(row=1, column=1, sticky="nsew", padx=5)

        # User Agent输入
        ttk.Label(form_frame, text="User Agent:").grid(row=4, column=0, sticky="w", pady=5)
        ua_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=ua_var, style="Custom.TEntry", state="readonly").grid(
            row=4, column=1, sticky="ew", pady=5)

        # ibex输入
        ttk.Label(form_frame, text="ibex:").grid(row=5, column=0, sticky="w", pady=5)
        ibex_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=ibex_var, style="Custom.TEntry", state="readonly").grid(
            row=5, column=1, sticky="ew", pady=5)
        
        # 按钮框架
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, sticky="e", pady=10)

        def load_existing_data():
            # 加载cookies
            cookies_data = self.get_user_cookies(username)
            if cookies_data:
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(cookies_data, indent=2, ensure_ascii=False))
                cookies_text.config(state="disabled")
            else:
                # 使用默认模板
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(self.__class__.DEFAULT_COOKIES_TEMPLATE, indent=2, ensure_ascii=False))
                cookies_text.config(state="disabled")
            
            # 加载设备信息
            device_file = f"login_phone_{username}.json"
            if os.path.exists(device_file):
                try:
                    with open(device_file, 'r', encoding='utf-8') as f:
                        device_data = json.load(f)
                    device_text.config(state="normal")
                    device_text.delete("1.0", "end")
                    device_text.insert("1.0", json.dumps(device_data, indent=2, ensure_ascii=False))
                    device_text.config(state="disabled")
                except Exception:
                    pass

            # 加载UA和ibex
            user = next((u for u in self.users_data if u["username"] == username), None)
            if user:
                ua_var.set(user.get("user_agent", ""))
                ibex_var.set(user.get("ibex", ""))

        # 在创建对话框后立即加载数据
        dialog.after(100, load_existing_data)
        
        def save_login_data():
            # 保存cookies和设备信息
            cookies_str = cookies_text.get("1.0", "end-1c")
            device_str = device_text.get("1.0", "end-1c")
            
            # 处理Cookies - 为空时使用默认模板
            if not cookies_str:
                cookies_data = self.__class__.DEFAULT_COOKIES_TEMPLATE
            else:
                try:
                    cookies_data = json.loads(cookies_str)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"JSON格式错误：{str(e)}")
                    return
            
            # 保存cookies到cookies/用户名.json
            cookies_file = f"cookies/{username}.json"
            try:
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("错误", f"无法保存Cookies文件：{str(e)}")
                return
            
            # 仅当设备信息非空时保存
            if device_str:
                try:
                    device_data = json.loads(device_str)
                    with open(f"login_phone_{username}.json", 'w', encoding='utf-8') as f:
                        json.dump(device_data, f, indent=2, ensure_ascii=False)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"设备信息JSON格式错误：{str(e)}")
                    return
                except Exception as e:
                    messagebox.showerror("错误", f"无法保存设备信息：{str(e)}")
                    return
                
            # 保存用户信息到config
            cookies_file = f"cookies/{username}.json"
            self.save_user_to_config(username, ua_var.get(), ibex_var.get(), cookies_file)
            
            messagebox.showinfo("成功", "数据保存成功")
            dialog.destroy()
        
        ttk.Button(btn_frame, text="保存", style="Accent.TButton",
                command=save_login_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", style="Accent.TButton",
                command=dialog.destroy).pack(side="left", padx=5)
    
    def show_manual_cookies_dialog(self, parent, username):
        """显示手动输入cookies对话框"""
        # 验证用户名
        is_valid, message = self.validate_username(username)
        if not is_valid:
            messagebox.showerror("错误", message)
            return
        
        dialog = tk.Toplevel(parent)
        dialog.title("手动输入Cookies")
        dialog.geometry("800x500")

        # 关键模态设置
        dialog.transient(parent)
        dialog.grab_set()
        dialog.focus_set()
        dialog.lift()
        
        # 创建主框架并使用grid布局
        form_frame = ttk.Frame(dialog, padding="20 15 20 15")
        form_frame.grid(row=0, column=0, sticky="nsew")
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # 配置网格权重 - 关键修改
        form_frame.grid_rowconfigure(2, weight=1)  # cookies区域可拉伸
        form_frame.grid_columnconfigure(0, weight=0)  # 标签列不拉伸
        form_frame.grid_columnconfigure(1, weight=1)  # 输入框列可拉伸

         # User Agent输入
        ttk.Label(form_frame, text="User Agent:").grid(row=0, column=0, sticky="w", pady=5)
        ua_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=ua_var, style="Custom.TEntry").grid(
            row=0, column=1, sticky="ew", pady=5, padx=(5, 0))  # 修复间距问题
        
        # ibex输入
        ttk.Label(form_frame, text="ibex:").grid(row=1, column=0, sticky="w", pady=5)
        ibex_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=ibex_var, style="Custom.TEntry").grid(
            row=1, column=1, sticky="ew", pady=5, padx=(5, 0))  # 修复间距问题
        
        # 获取已有cookies
        cookies_data = self.get_user_cookies(username)
        if not cookies_data:
            cookies_data = self.__class__.DEFAULT_COOKIES_TEMPLATE
        
        # 创建带转换功能的Cookies配置区域
        converter_frame, cookies_text = self.create_cookies_converter(
            form_frame, 
            default_content= self.__class__.DEFAULT_COOKIES_TEMPLATE
        )
        converter_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        # 按钮框架 - 使用grid布局
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, sticky="e", pady=10)

        def load_existing_data():
            # 加载cookies
            cookies_data = self.get_user_cookies(username)
            if cookies_data:
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(cookies_data, indent=2, ensure_ascii=False))
                # cookies_text.config(state="disabled")
            else:
                # 使用默认模板
                cookies_text.config(state="normal")
                cookies_text.delete("1.0", "end")
                cookies_text.insert("1.0", json.dumps(self.__class__.DEFAULT_COOKIES_TEMPLATE, indent=2, ensure_ascii=False))
                # cookies_text.config(state="disabled")
            
            # 加载UA和ibex
            user = next((u for u in self.users_data if u["username"] == username), None)
            if user:
                ua_var.set(user.get("user_agent", ""))
                ibex_var.set(user.get("ibex", ""))

        # 在创建对话框后立即加载数据
        dialog.after(100, load_existing_data)
    
        def save_cookies():
            """保存cookies"""
            cookies_str = cookies_text.get("1.0", "end-1c")
            
            # 处理Cookies - 为空时使用默认模板
            if not cookies_str:
                cookies_data = self.__class__.DEFAULT_COOKIES_TEMPLATE
            else:
                try:
                    cookies_data = json.loads(cookies_str)
                except json.JSONDecodeError as e:
                    messagebox.showerror("错误", f"JSON格式错误：{str(e)}")
                    return
            
            # 保存cookies到cookies/用户名.json
            cookies_file = f"cookies/{username}.json"
            try:
                with open(cookies_file, 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("错误", f"无法保存Cookies文件：{str(e)}")
                return
            
            # 保存用户信息到config
            cookies_file = f"cookies/{username}.json"
            self.save_user_to_config(username, ua_var.get(), ibex_var.get(), cookies_file)
                    
            messagebox.showinfo("成功", "Cookies保存成功")
            dialog.destroy()
        
        # 使用grid布局放置按钮
        ttk.Button(btn_frame, text="保存", style="Accent.TButton",
                command=save_cookies).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="取消", style="Accent.TButton",
                command=dialog.destroy).grid(row=0, column=1, padx=5)

    def add_user(self):
        """添加用户对话框"""
        if len(self.users_data) >= self.__class__.MAX_USERS:
            messagebox.showerror("错误", f"最多只能添加{self.__class__.MAX_USERS}个用户")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("添加用户")
        dialog.geometry("800x780")
        dialog.transient(self.root)  # 新增：设置为临时窗口
        dialog.grab_set()  # 新增：模态对话框
        
        form_frame = ttk.Frame(dialog, padding="20 15 20 15")
        form_frame.grid_columnconfigure(1, weight=1)  # 主内容列扩展
        form_frame.grid_columnconfigure(2, weight=0)  # 帮助提示列不扩展
        form_frame.pack(fill="both", expand=True)
        
        # ====用户名输入====
        ttk.Label(form_frame, text="用户名:").grid(row=0, column=0, sticky="w")
        username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=username_var, style="Custom.TEntry").grid(
            row=0, column=1, sticky="ew", padx=5)
        
        # 用户名格式提示
        ttk.Label(form_frame, text="* 2-20位，仅支持中文、字母、数字和下划线", 
                style="Help.TLabel").grid(row=0, column=2, sticky="w")
        
        # ====usertype输入====
        ttk.Label(form_frame, text="用户类型:").grid(row=3, column=0, sticky="w")
        usertype_var = tk.StringVar(value="captcha")
        ttk.Combobox(form_frame, textvariable=usertype_var, 
                    values=["captcha"],
                    state="readonly", width=15).grid(
            row=3, column=1, sticky="w", padx=5)
        ttk.Label(form_frame, text="* 用户类型，固定为captcha", 
                style="Help.TLabel").grid(row=3, column=2, sticky="w")

        # ====tokenid输入====
        ttk.Label(form_frame, text="tokenid:").grid(row=4, column=0, sticky="w")
        tokenid_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=tokenid_var, style="Custom.TEntry").grid(
            row=4, column=1, sticky="ew", padx=5)
        ttk.Label(form_frame, text="* 用于自动过图形验证，可在我的网站或者咸鱼上获取", 
                style="Help.TLabel").grid(row=4, column=2, sticky="w")
        
        # ====登录方式选择====
        login_frame = ttk.LabelFrame(form_frame, text="登录方式")
        login_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(login_frame, text="手机验证码登录", style="Accent.TButton",
                command=lambda: self.show_phone_login_dialog(dialog, username_var.get())).pack(fill="x", pady=2)
        ttk.Button(login_frame, text="账号密码登录", style="Accent.TButton",
                command=lambda: self.show_password_login_dialog(dialog, username_var.get())).pack(fill="x", pady=2)
        ttk.Button(login_frame, text="手动输入cookies", style="Accent.TButton",
                command=lambda: self.show_manual_cookies_dialog(dialog, username_var.get())).pack(fill="x", pady=2)


        # ====任务配置====
        task_frame = ttk.LabelFrame(form_frame, text="默认任务配置")
        task_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)
        
        task_vars = {}
        tasks = ["签到任务", "激励碎片任务", "章节卡任务", "游戏中心任务", "每日抽奖任务"]
        for i, task in enumerate(tasks):
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(task_frame, text=task, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=10, pady=5)
            task_vars[task] = var

        # ====推送服务配置====
        push_frame = ttk.LabelFrame(form_frame, text="推送服务")
        push_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 推送服务列表
        push_columns = ("type", "title")
        push_list = ttk.Treeview(push_frame, columns=push_columns, show="headings", height=5)
        push_list.heading("type", text="类型")
        push_list.heading("title", text="配置名称")
        push_list.column("type", width=100)
        push_list.column("title", width=300)
        push_list.pack(side="left", fill="both", expand=True)

        # 推送服务操作按钮
        push_btn_frame = ttk.Frame(push_frame)
        push_btn_frame.pack(side="right", fill="y", padx=5)
        
        push_services = []

        def add_push_service():
            """添加推送服务配置"""
            push_dialog = tk.Toplevel(dialog)
            push_dialog.title("添加推送服务")
            push_dialog.geometry("400x250")
            
            push_form = ttk.Frame(push_dialog, padding="15 10 15 10")
            push_form.pack(fill="both", expand=True)
            push_form.grid_rowconfigure(1, weight=1)  # 第1行可扩展
            push_form.grid_columnconfigure(1, weight=1)  # 第1列可扩展
            
            # 类型选择
            ttk.Label(push_form, text="类型:").grid(row=0, column=0, sticky="w")
            service_type = tk.StringVar()
            ttk.Combobox(push_form, textvariable=service_type,values=["feishu", "serverchan", "qiwei"],
                        state="readonly",width=15, font=self.default_font).grid(row=0, column=1, sticky="w")

            # 飞书配置区域
            feishu_frame = ttk.Frame(push_form)
            feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
            
            # Webhook URL行（可扩展）
            ttk.Label(feishu_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            feishu_url = ttk.Entry(feishu_frame)
            feishu_url.grid(row=0, column=1, sticky="ew", padx=5)
            feishu_frame.grid_columnconfigure(1, weight=1)
            
            ttk.Label(feishu_frame, text="是否有签名校验:").grid(row=1, column=0, sticky="w")
            has_sign = tk.BooleanVar()
            ttk.Checkbutton(feishu_frame, variable=has_sign, 
                        command=lambda: toggle_secret(secret_frame, has_sign.get())).grid(
                        row=1, column=1, sticky="w")
            
            # Secret行
            secret_frame = ttk.Frame(feishu_frame)
            ttk.Label(secret_frame, text="密钥:").grid(row=0, column=0, sticky="w")
            secret_entry = ttk.Entry(secret_frame)
            secret_entry.grid(row=0, column=1, sticky="ew", padx=5)
            secret_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
            secret_frame.grid_columnconfigure(1, weight=1)  # 允许Secret输入框扩展
            secret_frame.grid_remove()

            # ServerChan配置区域
            server_frame = ttk.Frame(push_form)
            ttk.Label(server_frame, text="SCKEY:").grid(row=0, column=0, sticky="w")
            sckey_entry = ttk.Entry(server_frame)
            sckey_entry.grid(row=0, column=1, sticky="ew")
            server_frame.grid_columnconfigure(1, weight=1)

            # Qiwei配置区域
            qiwei_frame = ttk.Frame(push_form)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url = ttk.Entry(qiwei_frame)
            qiwei_url.grid(row=0, column=1, sticky="ew")
            qiwei_frame.grid_columnconfigure(1, weight=1)

            # 类型切换处理
            def update_config_fields(*args):
                if service_type.get() == "feishu":
                    feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                    server_frame.grid_remove()
                    qiwei_frame.grid_remove()
                elif service_type.get() == "serverchan":
                    feishu_frame.grid_remove()
                    server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                    qiwei_frame.grid_remove()
                elif service_type.get() == "qiwei":
                    feishu_frame.grid_remove()
                    server_frame.grid_remove()
                    qiwei_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            
            service_type.trace_add("write", update_config_fields)
            update_config_fields()  # 初始化显示

            def save_push_service():
                """保存推送服务配置"""
                service_type_val = service_type.get()
                
                if service_type_val == "feishu":
                    url = feishu_url.get()
                    if not url:
                        messagebox.showerror("错误", "飞书Webhook URL不能为空")
                        return
                    
                    service = {
                        "type": "feishu",
                        "webhook_url": url,
                        "havesign": has_sign.get(),
                        "title": f"飞书推送 - {url[-20:]}"  # 简短显示
                    }
                    
                    if has_sign.get():
                        secret = secret_entry.get()
                        if not secret:
                            messagebox.showerror("错误", "签名模式必须填写密钥")
                            return
                        service["secret"] = secret
                        
                elif service_type_val == "serverchan":  # serverchan
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                        
                    service = {
                        "type": "serverchan",
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    }
                
                elif service_type_val == "qiwei":
                    url = qiwei_url.get()
                    if not url:
                        messagebox.showerror("错误", "QiWei Webhook URL不能为空")
                        return
                    
                    service = {
                        "type": "qiwei",
                        "webhook_url": url,
                        "title": f"企业微信 - {url[-20:]}"
                    }
                
                else: 
                    messagebox.showerror("错误", "未知的推送服务类型")
                    return
                    
                push_services.append(service)
                push_list.insert("", "end", values=(service["type"], service["title"]))
                push_dialog.destroy()
            
            # 创建按钮框架并使用grid布局
            btn_frame = ttk.Frame(push_dialog)
            btn_frame.pack(side="bottom", fill="x", padx=15, pady=10)  # 固定在底部

            # 保存按钮
            ttk.Button(btn_frame, 
                    text="保存", 
                    style="Accent.TButton",
                    command=save_push_service).pack(side="left", expand=True, fill="x", padx=5)

            # 取消按钮
            ttk.Button(btn_frame, 
                    text="取消", 
                    style="Accent.TButton",
                    command=push_dialog.destroy).pack(side="right", expand=True, fill="x", padx=5)
        def toggle_secret(frame, show):
            """控制Secret输入框显示"""
            if show:
                frame.grid(row=2, column=0, columnspan=2, sticky="ew")  # 固定行号和跨列
            else:
                frame.grid_remove()

        # 推送服务列表滚动条
        push_scrollbar = ttk.Scrollbar(push_frame, orient="vertical", command=push_list.yview)
        push_scrollbar.pack(side="right", fill="y")
        push_list.configure(yscrollcommand=push_scrollbar.set)

        # 推送服务操作按钮
        ttk.Button(push_btn_frame, text="添加", style="Accent.TButton",
                command=add_push_service).pack(fill="x", pady=2)
        ttk.Button(push_btn_frame, text="编辑", style="Accent.TButton",
                command=lambda: edit_push_service(push_list)).pack(fill="x", pady=2)
        ttk.Button(push_btn_frame, text="删除", style="Accent.TButton",
                command=lambda: delete_push_service(push_list)).pack(fill="x", pady=2)

        def edit_push_service(listbox):
            """编辑推送服务配置"""
            selected = listbox.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个推送服务")
                return
            
            if not push_services:
                messagebox.showwarning("警告", "推送服务列表为空")
                return
                
            index = listbox.index(selected[0])
            service = push_services[index]
            
            # 创建新的配置对话框进行编辑
            push_dialog = tk.Toplevel(dialog)
            push_dialog.title(f"编辑推送服务 - {service['type']}")
            push_dialog.geometry("400x250")
            
            push_form = ttk.Frame(push_dialog, padding="15 10 15 10")
            push_form.pack(fill="both", expand=True)
            push_form.grid_rowconfigure(1, weight=1)  # 第1行可扩展
            push_form.grid_columnconfigure(1, weight=1)  # 第1列可扩展
            
            # 类型选择（禁用修改）
            ttk.Label(push_form, text="类型:").grid(row=0, column=0, sticky="w")
            ttk.Label(push_form, text=service["type"]).grid(row=0, column=1, sticky="w")
            
            # 飞书配置区域
            feishu_frame = ttk.Frame(push_form)
            ttk.Label(feishu_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            feishu_url = ttk.Entry(feishu_frame)
            feishu_url.insert(0, service.get("webhook_url", ""))
            feishu_url.grid(row=0, column=1, sticky="ew")
            
            ttk.Label(feishu_frame, text="是否有签名校验:").grid(row=1, column=0, sticky="w")
            has_sign = tk.BooleanVar(value=service.get("havesign", False))
            ttk.Checkbutton(feishu_frame, variable=has_sign, 
                        command=lambda: toggle_secret(secret_frame, has_sign.get())).grid(
                        row=1, column=1, sticky="w")
            
            secret_frame = ttk.Frame(feishu_frame)
            ttk.Label(secret_frame, text="密钥:").grid(row=0, column=0, sticky="w")
            secret_entry = ttk.Entry(secret_frame)
            secret_entry.insert(0, service.get("secret", ""))
            secret_entry.grid(row=0, column=1, sticky="ew")
            if service.get("havesign", False):
                secret_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
            else:
                secret_frame.grid_remove()

            # ServerChan配置区域
            server_frame = ttk.Frame(push_form)
            ttk.Label(server_frame, text="SCKEY:").grid(row=0, column=0, sticky="w")
            sckey_entry = ttk.Entry(server_frame)
            sckey_entry.insert(0, service.get("sckey", ""))
            sckey_entry.grid(row=0, column=1, sticky="ew")

            # Qiwei配置区域
            qiwei_frame = ttk.Frame(push_form)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url = ttk.Entry(qiwei_frame)
            qiwei_url.insert(0, service.get("webhook_url", ""))
            qiwei_url.grid(row=0, column=1, sticky="ew")

            # 根据类型显示对应配置
            if service["type"] == "feishu":
                feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                server_frame.grid_remove()
                qiwei_frame.grid_remove()
            elif service["type"] == "serverchan":
                feishu_frame.grid_remove()
                server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                qiwei_frame.grid_remove()
            elif service["type"] == "qiwei":
                feishu_frame.grid_remove()
                server_frame.grid_remove()
                qiwei_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            else:
                feishu_frame.grid_remove()
                server_frame.grid_remove()
                qiwei_frame.grid_remove()
                messagebox.showerror("错误", "未知推送服务类型")

            def update_push_service():
                """更新推送服务配置"""
                if service["type"] == "feishu":
                    url = feishu_url.get()
                    if not url:
                        messagebox.showerror("错误", "飞书Webhook URL不能为空")
                        return
                    
                    service.update({
                        "webhook_url": url,
                        "havesign": has_sign.get()
                    })
                    
                    if has_sign.get():
                        secret = secret_entry.get()
                        if not secret:
                            messagebox.showerror("错误", "签名模式必须填写秘钥")
                            return
                        service["secret"] = secret
                    else:
                        service.pop("secret", None)
                        
                    service["title"] = f"飞书推送 - {url[-20:]}"
                elif service["type"] == "serverchan":
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                        
                    service.update({
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    })
                elif service["type"] == "qiwei":
                    url = qiwei_url.get()
                    if not url:
                        messagebox.showerror("错误", "企微Webhook URL不能为空")
                        return
                    
                    service.update({
                        "webhook_url": url,
                        "title": f"企微推送 - {url[-20:]}"
                    })
                else:
                    messagebox.showerror("错误", "未知推送服务类型")
                    return
                    
                # 更新列表显示
                item = listbox.selection()[0]
                listbox.item(item, values=(service["type"], service["title"]))
                push_dialog.destroy()

            # 创建底部按钮框架
            btn_frame = ttk.Frame(push_dialog)
            btn_frame.pack(side="bottom", fill="x", padx=15, pady=10)

            # 保存按钮
            ttk.Button(btn_frame, 
                    text="保存", 
                    style="Accent.TButton",
                    command=update_push_service).pack(
                side="left", expand=True, fill="x", padx=5)

            # 取消按钮
            ttk.Button(btn_frame, 
                    text="取消", 
                    style="Accent.TButton",
                    command=push_dialog.destroy).pack(
                side="right", expand=True, fill="x", padx=5)

        def delete_push_service(listbox):
            """删除推送服务"""
            selected = listbox.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个推送服务")
                return
                
            index = listbox.index(selected[0])
            del push_services[index]
            listbox.delete(selected[0])

        # 按钮容器
        # 修改位置：add_user 和 edit_user 中的按钮容器
        btn_container = ttk.Frame(form_frame)
        btn_container.grid(row=9, column=0, columnspan=3, sticky="e", pady=10)

        # 取消按钮
        # 左侧保存按钮
        ttk.Button(btn_container, text="保存", style="Accent.TButton", 
                command=lambda: save_new_user(push_services)).grid(
            row=0, column=0, sticky="e", padx=5)

        # 右侧取消按钮
        ttk.Button(btn_container, text="取消", style="Accent.TButton", command=dialog.destroy).grid(
            row=0, column=1, sticky="e", padx=5)

        def save_new_user(push_services):
            """保存新用户配置"""
            if len(self.users_data) >= self.__class__.MAX_USERS:
                messagebox.showerror("错误", f"最多只能添加{self.__class__.MAX_USERS}个用户")
                return

            username = username_var.get().strip()
            if not username:
                messagebox.showerror("错误", "用户名不能为空")
                return
            
            # 用户名格式验证
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$', username):
                messagebox.showerror("错误", "用户名格式错误！\n要求：\n1. 2-20个字符\n2. 仅支持中文、字母、数字和下划线")
                return
            
            # 检查用户是否已存在（通过登录界面创建）
            existing_user = next((u for u in self.users_data if u["username"] == username), None)
            
            # 创建基本用户数据
            user_data = {
                "username": username,
                "cookies_file": f"cookies/{username}.json",
                "usertype": usertype_var.get(),
                "tokenid": tokenid_var.get(),
                "tasks": {task: var.get() for task, var in task_vars.items()},
                "push_services": [
                    {k: v for k, v in service.items() if k != "title"}
                    for service in push_services
                ]
            }
            
            if existing_user:
                # 用户已存在，更新其他配置（保留已通过登录获取的信息）
                existing_user.update({
                    "usertype": user_data["usertype"],
                    "tokenid": user_data["tokenid"],
                    "tasks": user_data["tasks"],
                    "push_services": user_data["push_services"]
                })
                message = "用户配置已更新（登录信息已保留）"
            else:
                # 用户不存在，创建新用户
                self.users_data.append(user_data)
                message = "用户保存成功"
            
            self.refresh_user_list()
            dialog.destroy()
            self.save_users_config()
            messagebox.showinfo("成功", message)

    def edit_user(self):
        """编辑用户配置"""
        selected = self.user_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return

        index = self.user_list.index(selected[0])
        user = self.users_data[index]

        dialog = tk.Toplevel(self.root)
        dialog.title(f"编辑用户 - {user['username']}")
        dialog.geometry("800x780")
        dialog.transient(self.root)  # 新增：设置为临时窗口
        dialog.grab_set()  # 新增：模态对话框

        form_frame = ttk.Frame(dialog, padding="20 15 20 15")
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=0)
        form_frame.pack(fill="both", expand=True)

        # ====用户名输入====
        ttk.Label(form_frame, text="用户名:").grid(row=0, column=0, sticky="w")
        self.username_var = tk.StringVar(value=user["username"])
        ttk.Entry(form_frame, textvariable=self.username_var, style="Custom.TEntry").grid(
            row=0, column=1, sticky="ew", padx=5)

        # 用户名格式提示
        ttk.Label(form_frame, text="* 2-20位，仅支持中文、字母、数字和下划线", 
                style="Help.TLabel").grid(row=0, column=2, sticky="w")

        # ====usertype输入====
        ttk.Label(form_frame, text="用户类型:").grid(row=3, column=0, sticky="w")
        self.usertype_var = tk.StringVar(value=user.get("usertype", "captcha"))
        ttk.Combobox(form_frame, textvariable=self.usertype_var, 
                    values=["captcha"],
                    state="readonly", width=15).grid(
            row=3, column=1, sticky="w", padx=5)
        ttk.Label(form_frame, text="* 用户类型，固定为captcha", 
                style="Help.TLabel").grid(row=3, column=2, sticky="w")

        # ====tokenid输入====
        ttk.Label(form_frame, text="tokenid:").grid(row=4, column=0, sticky="w")
        self.tokenid_var = tk.StringVar(value=user.get("tokenid", ""))
        ttk.Entry(form_frame, textvariable=self.tokenid_var, style="Custom.TEntry").grid(
            row=4, column=1, sticky="ew", padx=5)
        ttk.Label(form_frame, text="* 用于自动过图形验证，可在我的网站或者咸鱼上获取", 
                style="Help.TLabel").grid(row=4, column=2, sticky="w")
        
        # ====登录方式选择====
        login_frame = ttk.LabelFrame(form_frame, text="登录方式")
        login_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        ttk.Button(login_frame, text="手机验证码登录", style="Accent.TButton",
                command=lambda: self.show_phone_login_dialog(dialog, self.username_var.get())).pack(fill="x", pady=2)
        ttk.Button(login_frame, text="账号密码登录", style="Accent.TButton",
                command=lambda: self.show_password_login_dialog(dialog, self.username_var.get())).pack(fill="x", pady=2)
        ttk.Button(login_frame, text="手动输入cookies", style="Accent.TButton",
                command=lambda: self.show_manual_cookies_dialog(dialog, self.username_var.get())).pack(fill="x", pady=2)

        # ====任务配置====
        task_frame = ttk.LabelFrame(form_frame, text="任务配置")
        task_frame.grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)

        task_vars = {}
        tasks = ["签到任务", "激励碎片任务", "章节卡任务", "游戏中心任务", "每日抽奖任务"]
        for i, task in enumerate(tasks):
            var = tk.BooleanVar(value=user["tasks"].get(task, True))
            ttk.Checkbutton(task_frame, text=task, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=10, pady=5)
            task_vars[task] = var

        # ====推送服务配置====
        push_frame = ttk.LabelFrame(form_frame, text="推送服务")
        push_frame.grid(row=7, column=0, columnspan=3, sticky="ew", pady=10)

        # 推送服务列表
        push_columns = ("type", "title")
        push_list = ttk.Treeview(push_frame, columns=push_columns, show="headings", height=5)
        push_list.heading("type", text="类型")
        push_list.heading("title", text="配置名称")
        push_list.column("type", width=100)
        push_list.column("title", width=300)
        push_list.pack(side="left", fill="both", expand=True)

        # 推送服务操作按钮
        push_btn_frame = ttk.Frame(push_frame)
        push_btn_frame.pack(side="right", fill="y", padx=5)

        # 初始化推送服务数据
        push_services = user.get("push_services", []).copy()

        def refresh_push_list():
            """刷新推送服务列表"""
            for item in push_list.get_children():
                push_list.delete(item)
            for service in push_services:
                title = service.get("title", f"{service.get('type')}配置")
                push_list.insert("", "end", values=(service["type"], title))

        refresh_push_list()

        # 推送服务列表滚动条
        push_scrollbar = ttk.Scrollbar(push_frame, orient="vertical", command=push_list.yview)
        push_scrollbar.pack(side="right", fill="y")
        push_list.configure(yscrollcommand=push_scrollbar.set)

        def add_push_service():
            """添加推送服务配置"""
            push_dialog = tk.Toplevel(dialog)
            push_dialog.title("添加推送服务")
            push_dialog.geometry("400x250")

            push_form = ttk.Frame(push_dialog, padding="15 10 15 10")
            push_form.pack(fill="both", expand=True)
            push_form.grid_rowconfigure(1, weight=1)  # 第1行可扩展
            push_form.grid_columnconfigure(1, weight=1)  # 第1列可扩展

            # 类型选择
            ttk.Label(push_form, text="类型:").grid(row=0, column=0, sticky="w")
            service_type = tk.StringVar()
            ttk.Combobox(push_form, textvariable=service_type,values=["feishu", "serverchan", "qiwei"],
                        state="readonly",width=15, font=self.default_font).grid(row=0, column=1, sticky="w")

            # 飞书配置区域
            feishu_frame = ttk.Frame(push_form)
            feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
            
            # Webhook URL行（可扩展）
            ttk.Label(feishu_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            feishu_url = ttk.Entry(feishu_frame)
            feishu_url.grid(row=0, column=1, sticky="ew", padx=5)
            feishu_frame.grid_columnconfigure(1, weight=1)

            ttk.Label(feishu_frame, text="是否有签名校验:").grid(row=1, column=0, sticky="w")
            has_sign = tk.BooleanVar()
            ttk.Checkbutton(feishu_frame, variable=has_sign, 
                        command=lambda: toggle_secret(secret_frame, has_sign.get())).grid(
                        row=1, column=1, sticky="w")

            # Secret行
            secret_frame = ttk.Frame(feishu_frame)
            ttk.Label(secret_frame, text="密钥:").grid(row=0, column=0, sticky="w")
            secret_entry = ttk.Entry(secret_frame)
            secret_entry.grid(row=0, column=1, sticky="ew", padx=5)
            secret_frame.grid_columnconfigure(1, weight=1)  # 允许Secret输入框扩展
            secret_frame.grid_remove()

            # ServerChan配置区域
            server_frame = ttk.Frame(push_form)
            ttk.Label(server_frame, text="SCKEY:").grid(row=0, column=0, sticky="w")
            sckey_entry = ttk.Entry(server_frame)
            sckey_entry.grid(row=0, column=1, sticky="ew")
            server_frame.grid_columnconfigure(1, weight=1)

            # Qiwei配置区域
            qiwei_frame = ttk.Frame(push_form)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url = ttk.Entry(qiwei_frame)
            qiwei_url.grid(row=0, column=1, sticky="ew")
            qiwei_frame.grid_columnconfigure(1, weight=1)

            # 类型切换处理
            def update_config_fields(*args):
                if service_type.get() == "feishu":
                    feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                    server_frame.grid_remove()
                    qiwei_frame.grid_remove()
                elif service_type.get() == "serverchan":
                    feishu_frame.grid_remove()
                    server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                    qiwei_frame.grid_remove()
                elif service_type.get() == "qiwei":
                    feishu_frame.grid_remove()
                    server_frame.grid_remove()
                    qiwei_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

            service_type.trace_add("write", update_config_fields)
            update_config_fields()  # 初始化显示

            def save_push_service():
                """保存推送服务配置"""
                service_type_val = service_type.get()
                if service_type_val == "feishu":
                    url = feishu_url.get()
                    if not url:
                        messagebox.showerror("错误", "飞书Webhook URL不能为空")
                        return

                    service = {
                        "type": "feishu",
                        "webhook_url": url,
                        "havesign": has_sign.get(),
                        "title": f"飞书推送 - {url[-20:]}"
                    }

                    if has_sign.get():
                        secret = secret_entry.get()
                        if not secret:
                            messagebox.showerror("错误", "签名模式必须填写密钥")
                            return
                        service["secret"] = secret

                elif service_type_val == "serverchan":  # serverchan
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                        
                    service = {
                        "type": "serverchan",
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    }
                
                elif service_type_val == "qiwei":
                    url = qiwei_url.get()
                    if not url:
                        messagebox.showerror("错误", "QiWei Webhook URL不能为空")
                        return
                    
                    service = {
                        "type": "qiwei",
                        "webhook_url": url,
                        "title": f"企业微信 - {url[-20:]}"
                    }
                else:
                    messagebox.showerror("错误", "未知的推送服务类型")
                    return

                push_services.append(service)
                push_list.insert("", "end", values=(service["type"], service["title"]))
                push_dialog.destroy()

            # 修改按钮框架布局
            btn_frame = ttk.Frame(push_dialog)
            btn_frame.pack(side="bottom", fill="x", padx=15, pady=10)  # 固定在底部

            # 保存按钮
            ttk.Button(btn_frame, 
                    text="保存", 
                    style="Accent.TButton",
                    command=save_push_service).pack(side="left", expand=True, fill="x", padx=5)

            # 取消按钮
            ttk.Button(btn_frame, 
                    text="取消", 
                    style="Accent.TButton",
                    command=push_dialog.destroy).pack(side="right", expand=True, fill="x", padx=5)

        def edit_push_service(listbox):
            """编辑推送服务配置"""
            selected = listbox.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个推送服务")
                return
            
            if not push_services:
                messagebox.showwarning("警告", "推送服务列表为空")
                return

            index = listbox.index(selected[0])
            service = push_services[index]

            # 创建新的配置对话框进行编辑
            push_dialog = tk.Toplevel(dialog)
            push_dialog.title(f"编辑推送服务 - {service['type']}")
            push_dialog.geometry("400x250")

            push_form = ttk.Frame(push_dialog, padding="15 10 15 10")
            push_form.pack(fill="both", expand=True)
            push_form.grid_rowconfigure(1, weight=1)  # 第1行可扩展
            push_form.grid_columnconfigure(1, weight=1)  # 第1列可扩展

            # 类型选择（禁用修改）
            ttk.Label(push_form, text="类型:").grid(row=0, column=0, sticky="w")
            ttk.Label(push_form, text=service["type"]).grid(row=0, column=1, sticky="w")

            # 飞书配置区域
            feishu_frame = ttk.Frame(push_form)
            feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
            ttk.Label(feishu_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            feishu_url = ttk.Entry(feishu_frame)
            feishu_url.insert(0, service.get("webhook_url", ""))
            feishu_url.grid(row=0, column=1, sticky="ew")
            feishu_frame.grid_columnconfigure(1, weight=1)

            ttk.Label(feishu_frame, text="是否有签名校验:").grid(row=1, column=0, sticky="w")
            has_sign = tk.BooleanVar(value=service.get("havesign", False))
            ttk.Checkbutton(feishu_frame, variable=has_sign, 
                        command=lambda: toggle_secret(secret_frame, has_sign.get())).grid(
                        row=1, column=1, sticky="w")

            secret_frame = ttk.Frame(feishu_frame)
            ttk.Label(secret_frame, text="密钥:").grid(row=0, column=0, sticky="w")
            secret_entry = ttk.Entry(secret_frame)
            secret_entry.insert(0, service.get("secret", ""))
            secret_entry.grid(row=0, column=1, sticky="ew")
            
            if service.get("havesign", False):
                secret_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
                secret_frame.grid_columnconfigure(1, weight=1)
            else:
                secret_frame.grid_remove()

            # ServerChan配置区域
            server_frame = ttk.Frame(push_form)
            ttk.Label(server_frame, text="SCKEY:").grid(row=0, column=0, sticky="w")
            sckey_entry = ttk.Entry(server_frame)
            sckey_entry.insert(0, service.get("sckey", ""))
            sckey_entry.grid(row=0, column=1, sticky="ew")
            server_frame.grid_columnconfigure(1, weight=1)

            # Qiwei配置区域
            qiwei_frame = ttk.Frame(push_form)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url = ttk.Entry(qiwei_frame)
            qiwei_url.insert(0, service.get("webhook_url", ""))
            qiwei_url.grid(row=0, column=1, sticky="ew")

            # 根据类型显示对应配置
            if service["type"] == "feishu":
                feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                server_frame.grid_remove()
                qiwei_frame.grid_remove()
            elif service["type"] == "serverchan":
                feishu_frame.grid_remove()
                server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                qiwei_frame.grid_remove()
            elif service["type"] == "qiwei":
                feishu_frame.grid_remove()
                server_frame.grid_remove()
                qiwei_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            else:
                feishu_frame.grid_remove()
                server_frame.grid_remove()
                qiwei_frame.grid_remove()
                messagebox.showerror("错误", "未知推送服务类型")

            def update_push_service():
                """更新推送服务配置"""
                if service["type"] == "feishu":
                    url = feishu_url.get()
                    if not url:
                        messagebox.showerror("错误", "飞书Webhook URL不能为空")
                        return

                    service.update({
                        "webhook_url": url,
                        "havesign": has_sign.get()
                    })

                    if has_sign.get():
                        secret = secret_entry.get()
                        if not secret:
                            messagebox.showerror("错误", "签名模式必须填写秘钥")
                            return
                        service["secret"] = secret
                    else:
                        service.pop("secret", None)
                    service["title"] = f"飞书推送 - {url[-20:]}"
                elif service["type"] == "serverchan":
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                        
                    service.update({
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    })
                elif service["type"] == "qiwei":
                    url = qiwei_url.get()
                    if not url:
                        messagebox.showerror("错误", "企微Webhook URL不能为空")
                        return
                    
                    service.update({
                        "webhook_url": url,
                        "title": f"企微推送 - {url[-20:]}"
                    })
                else: 
                    messagebox.showerror("错误", "未知推送服务类型")
                    return

                # 更新列表显示
                item = listbox.selection()[0]
                listbox.item(item, values=(service["type"], service["title"]))
                push_dialog.destroy()

            # 创建底部按钮框架
            btn_frame = ttk.Frame(push_dialog)
            btn_frame.pack(side="bottom", fill="x", padx=15, pady=10)

            # 保存按钮
            ttk.Button(btn_frame, 
                    text="保存", 
                    style="Accent.TButton",
                    command=update_push_service).pack(
                side="left", expand=True, fill="x", padx=5)

            # 取消按钮
            ttk.Button(btn_frame, 
                    text="取消", 
                    style="Accent.TButton",
                    command=push_dialog.destroy).pack(
                side="right", expand=True, fill="x", padx=5)

        def toggle_secret(frame, show):
            if show:
                frame.grid(row=2, column=0, columnspan=2, sticky="ew")  # 固定行号和跨列
            else:
                frame.grid_remove()

        def delete_push_service(listbox):
            """删除推送服务"""
            selected = listbox.selection()
            if not selected:
                messagebox.showwarning("警告", "请先选择一个推送服务")
                return

            index = listbox.index(selected[0])
            del push_services[index]
            listbox.delete(selected[0])

        # 推送服务操作按钮
        ttk.Button(push_btn_frame, text="添加", style="Accent.TButton",
                command=add_push_service).pack(fill="x", pady=2)
        ttk.Button(push_btn_frame, text="编辑", style="Accent.TButton",
                command=lambda: edit_push_service(push_list)).pack(fill="x", pady=2)
        ttk.Button(push_btn_frame, text="删除", style="Accent.TButton",
                command=lambda: delete_push_service(push_list)).pack(fill="x", pady=2)
        
        # 配置网格列权重
        form_frame.grid_columnconfigure(1, weight=1)

        # 按钮容器
        btn_container = ttk.Frame(form_frame)
        btn_container.grid(row=9, column=0, columnspan=3, sticky="e", pady=10)

        # 取消按钮
        ttk.Button(btn_container, text="取消", style="Accent.TButton",
                command=dialog.destroy).pack(side="right", padx=5)

        # 保存按钮
        ttk.Button(btn_container, text="保存", style="Accent.TButton",
                command=lambda: save_edited_user(push_services)).pack(
                side="right", padx=5)

        
        def save_edited_user(updated_push_services=None):
            """保存编辑后的用户配置"""
            if updated_push_services is None:
                updated_push_services = []
            new_username = self.username_var.get().strip()
            old_username = user["username"]

            # 检查用户名是否为空
            if not new_username:
                messagebox.showerror("错误", "用户名不能为空")
                return

            # 用户名格式验证
            if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$', new_username):
                messagebox.showerror("错误", "用户名格式错误！\n要求：\n1. 2-20个字符\n2. 仅支持中文、字母、数字和下划线")
                return

            # 检查用户名是否冲突
            if new_username != old_username and any(
                u["username"] == new_username and u != user  # 使用对象对比而非索引
                for u in self.users_data
            ):
                messagebox.showerror("错误", "该用户名已存在")
                return

            # 更新cookies文件路径
            new_cookies_file = f"cookies/{new_username}.json"
            if new_username != old_username:
                try:
                    old_cookies_file = user["cookies_file"]
                    if os.path.exists(old_cookies_file):
                        os.rename(old_cookies_file, new_cookies_file)
                except Exception as e:
                    messagebox.showerror("错误", f"无法更新Cookies文件：{str(e)}")
                    return

            # 更新用户数据
            edited_user = {
                "username": new_username,
                "cookies_file": new_cookies_file,
                "usertype": self.usertype_var.get(),  # 新增
                "tokenid": self.tokenid_var.get(),    # 新增
                "tasks": {task: var.get() for task, var in task_vars.items()},
                "push_services": [
                    {k: v for k, v in service.items() if k != "title"}
                    for service in updated_push_services or []
                ]
            }

            # self.users_data[index] = edited_user
            self.users_data[index].update(edited_user)
            self.refresh_user_list()
            dialog.destroy()
            self.save_users_config() # 实时保存用户配置更改 也可以删了，就会变成只有主界面的保存按钮才能保存
            messagebox.showinfo("成功", "用户信息已更新")  # ✅ 添加成功提示

    def remove_user(self):
        """删除选中的用户"""
        selected = self.user_list.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个用户")
            return
        
        index = self.user_list.index(selected[0])
        user = self.users_data[index]
        username = user["username"]
        cookies_file = user.get("cookies_file", "")

        
        if messagebox.askyesno("确认", f"确定要删除用户 '{username}' 吗？"):
            # 删除Cookies文件（如果存在）
            if cookies_file and os.path.exists(cookies_file):
                try:
                    os.remove(cookies_file)
                except Exception as e:
                    messagebox.showerror("错误", f"无法删除Cookies文件：{str(e)}")
                    return  # 阻止继续删除用户数据

            del self.users_data[index]
            self.refresh_user_list()
            self.save_users_config() # 实时保存用户配置更改 也可以删了，就会变成只有主界面的保存按钮才能保存
    
    def create_cookies_converter(self, parent, default_content=None):
        """创建带转换功能的Cookies配置区域"""
        converter_frame = ttk.Frame(parent)

        # 设置列权重：左侧和右侧可扩展，中间按钮列固定
        converter_frame.grid_columnconfigure(0, weight=1)  # 左侧输入区可扩展
        converter_frame.grid_columnconfigure(1, weight=0)  # 中间按钮列固定
        converter_frame.grid_columnconfigure(2, weight=1)  # 右侧显示区可扩展
        converter_frame.grid_rowconfigure(1, weight=1)  # 文本区域可垂直扩展
        
        # 左侧输入框
        input_label = ttk.Label(converter_frame, text="原始字符串:")
        input_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        input_text = tk.Text(converter_frame, height=5, font=self.default_font)
        input_text.grid(row=1, column=0, sticky="nsew", padx=5)
        
        # 右侧JSON显示
        json_label = ttk.Label(converter_frame, text="JSON格式:")
        json_label.grid(row=0, column=2, sticky="w", padx=5, pady=(5, 0))
        
        cookies_text = tk.Text(converter_frame, height=10, font=self.default_font)
        cookies_text.grid(row=1, column=2, sticky="nsew", padx=5)
        
        # 中间转换按钮
        convert_btn = ttk.Button(
            converter_frame,
            text="→\n转\n换",
            style="Accent.TButton",
            command=lambda: self.convert_string_to_json(input_text, cookies_text),
            width=6
        )
        convert_btn.grid(row=0, column=1, rowspan=2, sticky="ns", padx=20, pady=40)

        # ==== 水印提示逻辑 ==== 
        self.placeholder_text = "输入示例：appId=xxx; areaId=xxx; lang=xxx;"

        def set_placeholder():
            """设置水印提示"""
            input_text.delete("1.0", "end")
            input_text.insert("1.0", self.placeholder_text)
            input_text.tag_add("placeholder", "1.0", "end")
            input_text.tag_config("placeholder", foreground="gray")
            input_text._has_placeholder = True

        def clear_placeholder(event=None):
            """清除水印提示"""
            if getattr(input_text, "_has_placeholder", False):
                input_text.delete("1.0", "end")
                input_text.tag_config("placeholder", foreground="gray")  # 保留样式
                input_text._has_placeholder = False

        def restore_placeholder(event=None):
            """恢复水印提示"""
            if input_text.get("1.0", "end-1c") == "":
                set_placeholder()

        def on_key(event):
            """拦截 BackSpace 键，防止删除水印"""
            if getattr(input_text, "_has_placeholder", False):
                if event.keysym == "BackSpace":
                    return "break"
                else:
                    clear_placeholder()
            input_text.after(100, restore_placeholder)

        # 初始化水印提示
        input_text._has_placeholder = False
        input_text.bind("<FocusIn>", clear_placeholder)
        input_text.bind("<FocusOut>", restore_placeholder)
        input_text.bind("<Key>", on_key)

        set_placeholder()  # 初始设置
        # ==== 水印提示逻辑结束 ==== 

        # 插入默认内容
        # 插入默认内容
        if default_content is None:
            default_content = self.__class__.DEFAULT_COOKIES_TEMPLATE
        
        if default_content:
            if isinstance(default_content, str):
                cookies_text.insert("1.0", default_content)
            else:
                cookies_text.insert("1.0", json.dumps(default_content, indent=2, ensure_ascii=False))

        return converter_frame, cookies_text
    
    def convert_string_to_json(self, input_text, cookies_text):
        """转换字符串到JSON格式"""
        raw_str = input_text.get("1.0", "end-1c")

        # 检查是否是水印内容
        if getattr(input_text, "_has_placeholder", False) or raw_str == self.placeholder_text:
            messagebox.showwarning("警告", "请输入有效的Cookies字符串")
            return
        
        try:
            # 解析字符串为字典
            cookies_dict = {}
            pairs = [p.strip() for p in raw_str.split(";") if p.strip()]
            
            for pair in pairs:
                if "=" not in pair:
                    raise ValueError(f"无效的键值对: {pair}")
                
                key, value = pair.split("=", 1)
                cookies_dict[key.strip()] = value.strip()
            
            # 转换为JSON格式字符串
            json_str = json.dumps(cookies_dict, indent=2, ensure_ascii=False)
            
            # 更新右侧显示
            cookies_text.delete("1.0", "end")
            cookies_text.insert("1.0", json_str)
            
        except Exception as e:
            messagebox.showerror("转换失败", f"无法解析Cookies字符串：{str(e)}")

    def save_config(self):
        """保存配置到文件"""
        # 输入验证
        if self.log_days_var.get() < 1 or self.log_days_var.get() > 30:
            messagebox.showerror("错误", "日志保留天数必须在 1-30 天之间")
            return
        
        if self.retry_var.get() < 1 or self.retry_var.get() > 10:
            messagebox.showerror("错误", "重试次数必须在 1-10 次之间")
            return

        # 更新全局配置
        self.config_data.update({
            "default_user_agent": self.ua_var.get(),
            "log_level": self.log_level_var.get(),
            "log_retention_days": self.log_days_var.get(),
            "retry_attempts": self.retry_var.get()
        })
        
        # 保存用户配置
        self.config_data["users"] = self.users_data
        
        # 写入文件
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            
        messagebox.showinfo("成功", "配置保存成功")

    def save_users_config(self):
        """仅保存用户配置到文件"""
        try:
            # 更新配置数据中的用户列表
            self.config_data["users"] = self.users_data
            
            # 写入文件
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("错误", f"保存用户配置失败：{str(e)}")      

    def execute_task(self):
        """执行任务按钮点击事件"""

        # 获取当前可执行文件所在目录
        base_path = os.path.dirname(sys.argv[0])
        if sys_run == 1:
            qdjob_path = os.path.join(base_path, "QDjob.exe")
            qdjob_windows_path = os.path.join(base_path, "QDjob_windows.exe")
        elif sys_run == 2:
            qdjob_path = os.path.join(base_path, "QDjob")
            qdjob_windows_path = os.path.join(base_path, "QDjob_linux")
        else:
            messagebox.showerror("错误", "未知系统类型，请使用windows系统或者linux系统运行本程序")

        if os.path.exists(qdjob_path):
            import subprocess
            subprocess.Popen([qdjob_path])
        elif os.path.exists(qdjob_windows_path):
            import subprocess
            subprocess.Popen([qdjob_windows_path])
        else:
            error_message = (
                "❌未找到任务执行程序QDjob\n\n"
                "⚠️请将QDjob与本程序放置于同一个文件夹下\n\n"
                "⚠️请勿修改文件名"
            )
            messagebox.showerror("执行失败", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()