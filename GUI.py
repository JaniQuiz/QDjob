import tkinter as tk
from tkinter import ttk, messagebox
import os, re
import json

class ConfigEditor:

    MAX_USERS = 3  # 类级常量，限制最大用户数

    def __init__(self, root):
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
        
        # 创建主界面
        self.create_ui()

    def init_styles(self):
        """初始化主题样式"""
        style = ttk.Style()
        
        # 设置主题
        style.theme_use('vista')
        
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
        ttk.Label(author_frame, text="作者: JaniQuiz", font=("微软雅黑", 10)).grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(author_frame, text="项目: QDjob", font=("微软雅黑", 10)).grid(
            row=1, column=0, sticky="w", padx=5, pady=2)

        # 创建超链接标签
        github_link = ttk.Label(author_frame, text="GitHub: https://github.com/JaniQuiz/QDjob",
                            foreground="blue", cursor="hand2", font=("微软雅黑", 10))
        github_link.grid(row=2, column=0, sticky="w", padx=5, pady=2)

        # 添加声明文本
        ttk.Label(author_frame, text="该项目为开源免费项目，不会收取任何费用。",
                style="Help.TLabel").grid(row=3, column=0, sticky="w", padx=5, pady=2)

        # 绑定超链接点击事件
        def callback(event):
            import webbrowser
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
                
            self.user_list.insert("", "end", values=(
                user["username"],
                user["user_agent"] or "默认User Agent",
                cookies_status
            ))
    
    def add_user(self):
        """添加用户对话框"""
        if len(self.users_data) >= self.__class__.MAX_USERS:
            messagebox.showerror("错误", f"最多只能添加{self.__class__.MAX_USERS}个用户")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("添加用户")
        dialog.geometry("800x800")
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

        # ====User Agent输入====
        ttk.Label(form_frame, text="User Agent:").grid(row=1, column=0, sticky="w")
        ua_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=ua_var, style="Custom.TEntry").grid(
            row=1, column=1, sticky="ew", padx=5)
        ttk.Label(form_frame, text="* 不填则使用默认User Agent", 
                style="Help.TLabel").grid(row=1, column=2, sticky="w")

        # ====任务配置====
        task_frame = ttk.LabelFrame(form_frame, text="默认任务配置")
        task_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        task_vars = {}
        tasks = ["签到任务", "激励碎片任务", "章节卡任务", "每日抽奖任务"]
        for i, task in enumerate(tasks):
            var = tk.BooleanVar(value=True)
            ttk.Checkbutton(task_frame, text=task, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=10, pady=5)
            task_vars[task] = var

        # ====推送服务配置====
        push_frame = ttk.LabelFrame(form_frame, text="推送服务")
        push_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        
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

        # ==== Cookies 配置区域 ====
        cookies_frame = ttk.LabelFrame(form_frame, text="Cookies配置")
        cookies_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        # 插入默认Cookies模板
        default_cookies = {
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
        # 创建带转换功能的Cookies配置区域
        converter_frame, cookies_text = self.create_cookies_converter(
            cookies_frame, default_cookies
        )

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
            
            # qiwei行
            qiwei_frame = ttk.Frame(feishu_frame)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url_entry = ttk.Entry(qiwei_frame)
            qiwei_url_entry.grid(row=0, column=1, sticky="ew", padx=5)
            
            ttk.Label(qiwei_frame, text="Mentioned UserId:").grid(row=1, column=0, sticky="w")
            qiwei_userid_entry = ttk.Entry(qiwei_frame)
            qiwei_userid_entry.grid(row=1, column=1, sticky="ew", padx=5)
            
            qiwei_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
            qiwei_frame.grid_columnconfigure(1, weight=1)
            qiwei_frame.grid_remove()

            # ServerChan配置区域
            server_frame = ttk.Frame(push_form)
            ttk.Label(server_frame, text="SCKEY:").grid(row=0, column=0, sticky="w")
            sckey_entry = ttk.Entry(server_frame)
            sckey_entry.grid(row=0, column=1, sticky="ew")
            server_frame.grid_columnconfigure(1, weight=1)

            # 类型切换处理
            def update_config_fields(*args):
                if service_type.get() == "feishu":
                    server_frame.grid_remove()
                    qiwei_frame.grid_remove()
                    feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                elif service_type.get() == "serverchan":
                    feishu_frame.grid_remove()
                    qiwei_frame.grid_remove()
                    server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
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

                elif service_type.get() == "serverchan":  # serverchan
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                        
                    service = {
                        "type": "serverchan",
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    }
                elif service_type.get() == "qiwei":  # qiwei
                    qiwei_url = qiwei_url_entry.get()
                    qiwei_userid = qiwei_userid_entry.get()
                    if not qiwei_url or not qiwei_userid:
                        messagebox.showerror("错误", "企微推送的Webhook URL不能为空")
                        return
                    
                    service = {
                        "type": "qiwei",
                        "webhook_url": qiwei_url,
                        "userid": qiwei_userid,
                        "title": f"企微 - {qiwei_userid[-20:]}"
                    }
                    
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
            
            # qiwei配置区域
            qiwei_frame = ttk.Frame(push_form)
            ttk.Label(qiwei_frame, text="Webhook URL:").grid(row=0, column=0, sticky="w")
            qiwei_url_entry = ttk.Entry(qiwei_frame)
            qiwei_url_entry.insert(0, service.get("webhook_url", ""))
            qiwei_url_entry.grid(row=0, column=1, sticky="ew")

            ttk.Label(qiwei_frame, text="UserId:").grid(row=1, column=0, sticky="w")
            qiwei_userid_entry = ttk.Entry(qiwei_frame)
            qiwei_userid_entry.insert(0, service.get("userid", ""))
            qiwei_userid_entry.grid(row=1, column=1, sticky="ew")
            
            # 根据类型显示对应配置
            if service["type"] == "feishu":
                server_frame.grid_remove()
                qiwei_frame.grid_remove()
                feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            elif service["type"] == "serverchan":
                feishu_frame.grid_remove()
                qiwei_frame.grid_remove()
                server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
            elif service["type"] == "qiwei":
                feishu_frame.grid_remove()
                server_frame.grid_remove()
                qiwei_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

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
                    qiwei_url = qiwei_url_entry.get()
                    qiwei_userid = qiwei_userid_entry.get()
                    
                    if not qiwei_url:
                        messagebox.showerror("错误", "企微推送的Webhook URL不能为空")
                        return
                    
                    service.update({
                        "webhook_url": qiwei_url,
                        "userid": qiwei_userid,
                        "title": f"企微 - {qiwei_userid[-20:]}"
                    })
                    
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
        btn_container.grid(row=10, column=0, columnspan=3, sticky="e", pady=10)

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
            
            # 检查用户名是否冲突
            if any(u["username"] == username for u in self.users_data):
                messagebox.showerror("错误", "该用户名已存在")
                return
                
            new_user = {
                "username": username,
                "cookies_file": f"cookies/{username}.json",
                "user_agent": ua_var.get(),
                "tasks": {task: var.get() for task, var in task_vars.items()},
                "push_services": [
                    {k: v for k, v in service.items() if k != "title"}  # 过滤 title 字段
                    for service in push_services
                ]
            }

            # 验证并保存Cookies
            try:
                cookies_data = json.loads(cookies_text.get("1.0", "end-1c"))
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"Cookies JSON格式错误：{str(e)}")
                return

            try:
                with open(new_user["cookies_file"], 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("错误", f"无法写入Cookies文件：{str(e)}")
                return
            
            self.users_data.append(new_user)
            self.refresh_user_list()
            dialog.destroy()
            self.save_users_config() # 实时保存用户配置更改 也可以删了，就会变成只有主界面的保存按钮才能保存
            messagebox.showinfo("成功", "用户保存成功")  # ✅ 添加成功提示

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
        dialog.geometry("800x800")
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

        # ====User Agent输入====
        ttk.Label(form_frame, text="User Agent:").grid(row=1, column=0, sticky="w")
        ua_var = tk.StringVar(value=user.get("user_agent", ""))
        ttk.Entry(form_frame, textvariable=ua_var, style="Custom.TEntry").grid(
            row=1, column=1, sticky="ew", padx=5)
        ttk.Label(form_frame, text="* 不填则使用默认User Agent", 
                style="Help.TLabel").grid(row=1, column=2, sticky="w")

        # ====任务配置====
        task_frame = ttk.LabelFrame(form_frame, text="任务配置")
        task_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)

        task_vars = {}
        tasks = ["签到任务", "激励碎片任务", "章节卡任务", "每日抽奖任务"]
        for i, task in enumerate(tasks):
            var = tk.BooleanVar(value=user["tasks"].get(task, True))
            ttk.Checkbutton(task_frame, text=task, variable=var).grid(
                row=i//3, column=i%3, sticky="w", padx=10, pady=5)
            task_vars[task] = var

        # ====推送服务配置====
        push_frame = ttk.LabelFrame(form_frame, text="推送服务")
        push_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)

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

        # ==== Cookies 配置区域 ====
        cookies_frame = ttk.LabelFrame(form_frame, text="Cookies配置")
        cookies_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)

        # 读取现有Cookies内容
        try:
            if os.path.exists(user["cookies_file"]):
                with open(user["cookies_file"], 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = None
        except Exception as e:
            content = "// 读取Cookies失败：" + str(e)

        # 使用create_cookies_converter创建带转换功能的区域
        converter_frame, cookies_text = self.create_cookies_converter(
            cookies_frame, content if content else None
        )

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
            ttk.Combobox(push_form, textvariable=service_type,values=["feishu", "serverchan"],
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

            # 类型切换处理
            def update_config_fields(*args):
                if service_type.get() == "feishu":
                    server_frame.grid_remove()
                    feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                else:
                    feishu_frame.grid_remove()
                    server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

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

                else:  # serverchan
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return

                    service = {
                        "type": "serverchan",
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    }

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

            # 根据类型显示对应配置
            if service["type"] == "feishu":
                server_frame.grid_remove()
                feishu_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                feishu_frame.grid_columnconfigure(1, weight=1)
            else:
                feishu_frame.grid_remove()
                server_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
                server_frame.grid_columnconfigure(1, weight=1)

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
                else:
                    sckey = sckey_entry.get()
                    if not sckey:
                        messagebox.showerror("错误", "ServerChan SCKEY不能为空")
                        return
                    service.update({
                        "sckey": sckey,
                        "title": f"Server酱 - {sckey[-20:]}"
                    })

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
        btn_container.grid(row=10, column=0, columnspan=3, sticky="e", pady=10)

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
                "user_agent": ua_var.get(),
                "tasks": {task: var.get() for task, var in task_vars.items()},
                "push_services": [
                    {k: v for k, v in service.items() if k != "title"}  # 过滤 title 字段
                    for service in updated_push_services or []
                ]
            }

            # 保存Cookies
            try:
                cookies_data = json.loads(cookies_text.get("1.0", "end-1c"))
            except json.JSONDecodeError as e:
                messagebox.showerror("错误", f"Cookies JSON格式错误：{str(e)}")
                return

            try:
                with open(user["cookies_file"], 'w', encoding='utf-8') as f:
                    json.dump(cookies_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                messagebox.showerror("错误", f"无法写入Cookies文件：{str(e)}")
                return

            self.users_data[index] = edited_user
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
        converter_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 设置列权重：左侧和右侧可扩展，中间按钮列固定
        converter_frame.grid_columnconfigure(0, weight=1)  # 左侧输入区可扩展
        converter_frame.grid_columnconfigure(1, weight=0)  # 中间按钮列固定
        converter_frame.grid_columnconfigure(2, weight=1)  # 右侧显示区可扩展

        # 左侧输入框（使用grid布局替代原pack布局）
        input_label = ttk.Label(converter_frame, text="原始字符串:")
        input_label.grid(row=0, column=0, sticky="w")

        input_text = tk.Text(converter_frame, height=5, font=self.default_font)
        input_text.grid(row=1, column=0, sticky="nsew", padx=5)

        # 右侧JSON显示
        json_label = ttk.Label(converter_frame, text="JSON格式:")
        json_label.grid(row=0, column=2, sticky="w")

        cookies_text = tk.Text(converter_frame, height=10, font=self.default_font)
        cookies_text.grid(row=1, column=2, sticky="nsew", padx=5)

        # 中间转换按钮（固定大小 + 固定间距）
        convert_btn = ttk.Button(
            converter_frame,
            text="→\n转\n换",
            style="Accent.TButton",
            command=lambda: self.convert_string_to_json(input_text, cookies_text),
            width=6  # 按钮宽度（字符数）
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
        import sys, os

        # 获取当前可执行文件所在目录
        base_path = os.path.dirname(sys.argv[0])
        qdjob_path = os.path.join(base_path, "QDjob.exe")

        if os.path.exists(qdjob_path):
            import subprocess
            subprocess.Popen([qdjob_path])
        else:
            error_message = (
                "❌未找到QDjob文件\n\n"
                "⚠️请将QDjob与本程序放置于同一个文件夹下\n\n"
                "⚠️请勿修改文件名"
            )
            messagebox.showerror("执行失败", error_message)

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()