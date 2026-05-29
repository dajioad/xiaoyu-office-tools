import logging
import os
import threading
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class Logger:
    _instance = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir=None, max_days=7, max_bytes=10*1024*1024, backup_count=5):
        if Logger._initialized:
            return

        if log_dir is None:
            log_dir = os.path.join(os.path.expanduser("~"), ".office_tool", "logs")
        self.log_dir = log_dir
        self.max_days = max_days
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self._ensure_log_dir()

        self.logger = logging.getLogger("OfficeTool")
        self.logger.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self._setup_handlers()

        Logger._initialized = True


    def _ensure_log_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _setup_handlers(self):
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{today}.log")
        
        # 使用大小轮转文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self._clean_old_logs()

    def _clean_old_logs(self):
        try:
            now = datetime.now()
            cutoff = now - timedelta(days=self.max_days)
            for fname in os.listdir(self.log_dir):
                if fname.endswith('.log') or fname.endswith('.log.'):
                    file_path = os.path.join(self.log_dir, fname)
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime < cutoff:
                        try:
                            os.remove(file_path)
                        except:
                            pass
        except Exception as e:
            print(f"清理旧日志失败: {e}")

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message, exc_info=False):
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message, exc_info=False):
        self.logger.critical(message, exc_info=exc_info)


def get_logger():
    return Logger()