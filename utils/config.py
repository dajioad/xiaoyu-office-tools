import os
import json
import configparser
from typing import Any, Callable, Optional, Dict, List, Tuple
from PySide6.QtCore import QObject, Signal
from .secure_config import SecureConfig


class ConfigChangeObserver(QObject):
    config_changed = Signal(str, str, object)
    def __init__(self, callback: Callable):
        super().__init__()
        self.callback = callback
    def notify(self, section: str, key: str, value: Any):
        self.callback(section, key, value)


class ConfigValidator:
    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None) -> Tuple[bool, str]:
        try:
            v = int(value)
            if min_val is not None and v < min_val:
                return False, f"值必须 ≥ {min_val}"
            if max_val is not None and v > max_val:
                return False, f"值必须 ≤ {max_val}"
            return True, ""
        except ValueError:
            return False, "必须是整数"
    
    @staticmethod
    def validate_positive_integer(value: str) -> Tuple[bool, str]:
        return ConfigValidator.validate_integer(value, 1)
    
    @staticmethod
    def validate_boolean(value: str) -> Tuple[bool, str]:
        if value.lower() in ('true', 'false', '1', '0', 'yes', 'no'):
            return True, ""
        return False, "必须是布尔值 (true/false)"
    
    @staticmethod
    def validate_theme(value: str, themes: List[str]) -> Tuple[bool, str]:
        return (True, "") if value in themes else (False, f"无效主题，可用: {', '.join(themes)}")
    
    @staticmethod
    def validate_language(value: str) -> Tuple[bool, str]:
        return (True, "") if value in ('zh', 'en') else (False, "语言必须是 zh 或 en")


class ConfigManager:
    VALIDATION_RULES = {
        "App": {
            "interface_scale": ConfigValidator.validate_positive_integer,
            "max_windows": ConfigValidator.validate_positive_integer,
            "sound_enabled": ConfigValidator.validate_boolean,
        },
        "Symbols": {
            "language": ConfigValidator.validate_language,
        }
    }
    
    CONFIG_METADATA = {
        "App": {"version": "1.0.0", "theme": "blue", "interface_scale": "100", "sound_enabled": "true", "max_windows": "5"},
        "TextProcessor": {"max_characters": "1000", "enable_smart_split": "true", "desensitize_level": "2"},
        "Symbols": {"language": "zh", "custom_symbols": "[]", "disabled_default_symbols": "[]", "custom_defaults": "{}"},
        "Formulas": {"disabled": "[]", "custom": "[]", "custom_defaults": "{}"},
        "UI": {"animation": "true", "default_page": "符号处理"},
        "Backup": {"auto_backup": "false", "auto_interval": "每天"},
        "File": {"default_path": "", "default_encoding": "UTF-8"},
        "Update": {"auto_check": "false"},
        "Reminder": {"enabled": "false", "interval": "1小时", "custom_minutes": "60", "message": "起来活动一下"},
        "Hotkeys": {"show_window": "Ctrl+Shift+W", "symbol_panel": "Ctrl+Shift+S", "screenshot": "Ctrl+Shift+X"},
        "SymbolPanel": {"theme": "light"},
        "Filter": {"symbols": ""}
    }
    
    def __init__(self):
        if os.name == 'nt':
            # 使用用户的 Documents 文件夹，更稳定
            user_dir = os.path.join(os.path.expanduser("~"), "Documents", "小雨办公工具")
        else:
            xdg = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            user_dir = os.path.join(xdg, "小雨办公工具")
        self.data_dir = user_dir
        self.config_path = os.path.join(self.data_dir, "config.ini")
        self._cache: Dict[str, Dict[str, str]] = {}
        self._loaded = False
        self._observers: List[ConfigChangeObserver] = []
    
    def _load_cache(self):
        if self._loaded:
            return
        os.makedirs(self.data_dir, exist_ok=True)
        # 使用RawConfigParser禁用interpolation，避免JSON中的%字符引发错误
        cfg = configparser.RawConfigParser()
        cfg.read(self.config_path, encoding="utf-8")
        for sec in cfg.sections():
            self._cache[sec] = dict(cfg[sec])
        self._loaded = True
    
    def _write_cache(self):
        # 自动备份现有配置（如果存在）
        if os.path.exists(self.config_path):
            self._backup_config()
            
        # 使用RawConfigParser禁用interpolation，避免JSON中的%字符引发错误
        cfg = configparser.RawConfigParser()
        for sec, vals in self._cache.items():
            cfg[sec] = vals
        with open(self.config_path, "w", encoding="utf-8") as f:
            cfg.write(f)
    
    def _backup_config(self):
        """自动备份配置文件，保留最近5个备份"""
        try:
            import shutil
            from datetime import datetime
            
            # 备份文件夹
            backup_dir = os.path.join(self.data_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名（带时间戳）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"config_backup_{timestamp}.ini"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 复制当前配置文件
            shutil.copy2(self.config_path, backup_path)
            
            # 清理旧备份（保留最近5个）
            self._cleanup_old_backups(backup_dir, 5)
        except Exception as e:
            # 备份失败不影响保存操作
            pass
    
    def _cleanup_old_backups(self, backup_dir, keep_count=5):
        """清理旧备份，只保留最近N个"""
        try:
            if not os.path.exists(backup_dir):
                return
                
            # 获取所有备份文件并按修改时间排序
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.startswith("config_backup_") and filename.endswith(".ini"):
                    filepath = os.path.join(backup_dir, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # 按时间从旧到新排序
            backup_files.sort(key=lambda x: x[1])
            
            # 只保留最近keep_count个
            if len(backup_files) > keep_count:
                for filepath, _ in backup_files[:len(backup_files) - keep_count]:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
        except Exception:
            pass
    
    def init_config(self):
        self._load_cache()
        if not os.path.exists(self.config_path):
            self.create_default_config()
    
    def create_default_config(self):
        for sec, items in self.CONFIG_METADATA.items():
            self._cache[sec] = items.copy()
        self._write_cache()
    
    def get_config(self, section: str, key: str, default: Any = None) -> str:
        self._load_cache()
        return self._cache.get(section, {}).get(key, default)
    
    def get_config_typed(self, section: str, key: str, value_type: str, default: Any = None) -> Any:
        val = self.get_config(section, key)
        if val is None:
            return default
        try:
            if value_type == "integer":
                return int(val)
            elif value_type == "boolean":
                return val.lower() in ('true', '1', 'yes')
            elif value_type == "float":
                return float(val)
            return val
        except (ValueError, TypeError):
            return default
    
    def set_config(self, section: str, key: str, value: Any, validate: bool = True) -> Tuple[bool, str]:
        if validate:
            rule = self.VALIDATION_RULES.get(section, {}).get(key)
            if rule:
                ok, msg = rule(str(value))
                if not ok:
                    return False, msg
        self._load_cache()
        if section not in self._cache:
            self._cache[section] = {}
        self._cache[section][key] = str(value)
        self._write_cache()
        if validate:
            for obs in self._observers:
                obs.notify(section, key, value)
        return True, ""
    
    def batch_set_config(self, configs: List[Tuple[str, str, Any]], validate: bool = True) -> Tuple[bool, str]:
        self._load_cache()
        for sec, key, val in configs:
            if validate:
                rule = self.VALIDATION_RULES.get(sec, {}).get(key)
                if rule:
                    ok, msg = rule(str(val))
                    if not ok:
                        return False, msg
            if sec not in self._cache:
                self._cache[sec] = {}
            self._cache[sec][key] = str(val)
        self._write_cache()
        if validate:
            for sec, key, val in configs:
                for obs in self._observers:
                    obs.notify(sec, key, val)
        return True, ""
    
    def register_observer(self, callback: Callable) -> ConfigChangeObserver:
        obs = ConfigChangeObserver(callback)
        self._observers.append(obs)
        return obs
    
    def unregister_observer(self, observer: ConfigChangeObserver):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def get_all_configs(self, section: str) -> Dict[str, str]:
        self._load_cache()
        return self._cache.get(section, {}).copy()
    
    def load_json_data(self, filename: str) -> Optional[dict]:
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON失败 {filename}: {e}")
            return None
    
    def save_json_data(self, filename: str, data: dict):
        path = os.path.join(self.data_dir, filename)
        os.makedirs(self.data_dir, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)