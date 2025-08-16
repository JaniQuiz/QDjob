import logging
import os
import logging.handlers

LOG_DIR = 'logs'
DEFAULT_LOG_RETENTION = 7

class LoggerManager:
    _instance = None
    _logger = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def _setup_file_handler(self):
        """配置文件输出处理器"""
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        
        file_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(LOG_DIR, 'qidian.log'),
            when='midnight',
            backupCount=DEFAULT_LOG_RETENTION,
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        return file_handler
    
    def setup_basic_logger(self):
        """初始化基础日志系统（用于 pre_check）"""
        self._logger = logging.getLogger('Qidian')
        self._logger.setLevel('INFO')

        # 清除已有 handlers
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # 添加控制台 handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(console_handler)

        # 添加文件 handler
        file_handler = self._setup_file_handler()
        self._logger.addHandler(file_handler)

        return self._logger

    def reconfigure_logger(self, log_level='INFO', retention_days=7):
        """根据配置重新初始化日志系统"""
        self._logger.setLevel(log_level)

        # 移除旧的 handlers
        for handler in self._logger.handlers[:]:
            self._logger.removeHandler(handler)

        # 创建日志格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # 文件输出（带自动清理）
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            os.path.join(LOG_DIR, 'qidian.log'),
            when='midnight',
            backupCount=retention_days,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        return self._logger

    @property
    def logger(self):
        if self._logger is None:
            raise RuntimeError("Logger尚未初始化")
        return self._logger