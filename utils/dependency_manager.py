import sys
from typing import Dict, Optional, Callable, Tuple
from functools import wraps

class DependencyInfo:
    def __init__(self, name, package, purpose, req_ver=None):
        self.name = name; self.package = package; self.purpose = purpose
        self.req_ver = req_ver; self.is_available = False; self.import_error = None
    def __repr__(self):
        return f"{self.name}: {'✓' if self.is_available else '✗'}"

class DependencyManager:
    DEPENDENCIES = {
        "excel": DependencyInfo("Excel处理", "openpyxl", "Excel文件读写"),
        "word": DependencyInfo("Word处理", "python-docx", "Word文档读写"),
        "text_processing": DependencyInfo("文本处理", "jieba", "中文分词"),
    }

    def _check(self):
        for name, dep in self.DEPENDENCIES.items():
            try:
                if name == "excel": import openpyxl
                elif name == "word": import docx
                elif name == "text_processing": import jieba
                dep.is_available = True
            except ImportError as e:
                dep.is_available = False
                dep.import_error = str(e)

    def is_available(self, name): return self.DEPENDENCIES.get(name, False).is_available
    def get_missing(self): return [d for d in self.DEPENDENCIES.values() if not d.is_available]
    def get_install_cmd(self, name):
        d = self.DEPENDENCIES.get(name)
        if not d: return None
        cmd = f"pip install {d.package}"
        if d.req_ver: cmd += d.req_ver
        return cmd
    def check_and_warn(self, name, show_dlg=None):
        if self.is_available(name): return True
        d = self.DEPENDENCIES.get(name)
        if not d: return False
        msg = f"【{d.name}】需要安装：{d.package}\n安装命令：{self.get_install_cmd(name)}"
        if show_dlg:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "缺少依赖", msg)
        else:
            print(msg)
        return False
    def get_feature_status(self): return {n:d.is_available for n,d in self.DEPENDENCIES.items()}

_dep_mgr = None
def get_dependency_manager():
    global _dep_mgr
    if _dep_mgr is None: _dep_mgr = DependencyManager()
    return _dep_mgr

def require_dependency(name, fallback=None):
    def deco(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if get_dependency_manager().is_available(name):
                return func(*args, **kwargs)
            if fallback: return fallback(*args, **kwargs)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(None, "功能不可用", f"【{name}】需要安装依赖包")
            return None
        return wrapper
    return deco

def check_word_support(show=True): return get_dependency_manager().check_and_warn("word", QMessageBox.warning if show else None)
def check_pdf_support(show=True): return get_dependency_manager().check_and_warn("pdf", QMessageBox.warning if show else None)
def check_excel_support(show=True): return get_dependency_manager().check_and_warn("excel", QMessageBox.warning if show else None)

PYMUPDF_AVAILABLE = get_dependency_manager().is_available("pdf")
DOCX_AVAILABLE = get_dependency_manager().is_available("word")
DOCX2PDF_AVAILABLE = get_dependency_manager().is_available("word_export")