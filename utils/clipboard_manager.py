import os
import json
import threading
from collections import OrderedDict
from typing import List, Optional

class ClipboardHistoryManager:
    """剪贴板历史管理器（线程安全）"""

    def __init__(self, max_size: int = 50, data_dir: str = None):
        self._history: OrderedDict[str, None] = OrderedDict()
        self._max_size = max_size
        self._data_dir = data_dir
        self._file_path = os.path.join(data_dir, "clipboard_history.json") if data_dir else None
        self._max_text_length = 5000  # 每条记录最大字符数
        self._lock = threading.Lock()  # 线程安全锁
        self._load_history()

    def add(self, text: str):
        with self._lock:
            if not text or len(text.strip()) == 0:
                return
            # 截断过长文本
            if len(text) > self._max_text_length:
                text = text[:self._max_text_length] + "…[已截断]"

            if text in self._history:
                self._history.move_to_end(text)
            else:
                self._history[text] = None
                if len(self._history) > self._max_size:
                    self._history.popitem(last=False)
            self._save_history()

    def get_all(self) -> List[str]:
        with self._lock:
            return list(self._history.keys())

    def get_recent(self, limit: int = 10) -> List[str]:
        with self._lock:
            all_items = list(self._history.keys())
            return all_items[-limit:] if limit > 0 else all_items

    def clear(self):
        with self._lock:
            self._history.clear()
            self._save_history()

    def remove(self, text: str):
        with self._lock:
            if text in self._history:
                del self._history[text]
                self._save_history()

    def __len__(self) -> int:
        with self._lock:
            return len(self._history)

    def __contains__(self, text: str) -> bool:
        with self._lock:
            return text in self._history

    def _load_history(self):
        if not self._file_path or not os.path.exists(self._file_path):
            return
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, str):
                            self._history[item] = None
        except Exception as e:
            print(f"加载剪贴板历史失败: {e}")

    def _save_history(self):
        if not self._file_path:
            return
        try:
            os.makedirs(self._data_dir, exist_ok=True)
            # 限制JSON文件大小不超过10MB
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
            
            # 先尝试保存当前状态
            data = list(self._history.keys())
            json_str = json.dumps(data, ensure_ascii=False)
            
            # 如果超过大小，逐步移除旧记录直到大小合适
            while len(json_str.encode('utf-8')) > MAX_FILE_SIZE and len(data) > 0:
                # 移除最旧的记录
                if len(data) > 1:
                    data = data[1:]
                else:
                    data = []
                json_str = json.dumps(data, ensure_ascii=False)
            
            # 确保文件不会太大
            if len(data) > 0:
                with open(self._file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                # 如果没有内容，删除文件
                if os.path.exists(self._file_path):
                    os.remove(self._file_path)
        except Exception as e:
            print(f"保存剪贴板历史失败: {e}")