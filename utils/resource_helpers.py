import os
import sys
import platform

def get_os_type() -> str:
    """
    获取操作系统类型
    
    Returns:
        'windows', 'linux', 'darwin' (macOS) 或 'unknown'
    """
    return platform.system().lower()

def resource_path(relative_path: str) -> str:
    """
    获取资源绝对路径，兼容开发环境和 PyInstaller 打包后的路径。
    
    Args:
        relative_path: 相对于项目根目录的资源路径（如 "data/config.ini"）
    
    Returns:
        资源的绝对路径字符串
    """
    try:
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        
        # 处理跨平台路径分隔符
        if isinstance(relative_path, str):
            relative_path = relative_path.replace('/', os.sep).replace('\\', os.sep)
        
        return os.path.join(base_path, relative_path)
    except Exception as e:
        print(f"警告：获取资源路径失败 - {e}")
        return relative_path