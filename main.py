import sys
import os
import platform

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QIcon

sys.dont_write_bytecode = True
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 跨平台QT主题设置
os_type = platform.system().lower()
if os_type == 'windows':
    os.environ['QT_QUICK_CONTROLS_STYLE'] = 'Windows'
    os.environ['QT_QPA_PLATFORMTHEME'] = 'windows'
elif os_type == 'linux':
    os.environ['QT_QPA_PLATFORMTHEME'] = 'gtk3'
elif os_type == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'

from utils.resource_helpers import resource_path
from utils.config import ConfigManager
from ui.main_window import MainWindow
from utils.secure_activation import SecureActivationManager


def main():
    force_pro = len(sys.argv) > 1 and sys.argv[1].lower() == "pro"

    app = QApplication(sys.argv)
    app.setApplicationName("小雨办公工具")
    
    # 设置全局窗口图标（影响所有弹窗和任务栏图标）
    # 兼容开发环境和打包后的运行环境
    if getattr(sys, 'frozen', False):
        # 打包后的环境：从exe所在目录获取
        base_path = os.path.dirname(sys.executable)
        icon_path = os.path.join(base_path, "小雨办公工具.ico")
    else:
        # 开发环境：从当前目录获取
        icon_path = "小雨办公工具.ico"
    
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    
    # 跨平台字体设置
    if os_type == 'windows':
        app.setFont(QFont("微软雅黑", 10))
    elif os_type == 'darwin':
        app.setFont(QFont("PingFang SC", 13))
    else:
        app.setFont(QFont("Noto Sans CJK SC", 10))
    
    cfg = ConfigManager()
    cfg.init_config()

    def late_init():
        try:
            act_mgr = SecureActivationManager(cfg.data_dir)
            act_mgr.get_machine_code()   # 预生成机器码

            win = MainWindow(cfg)
            if force_pro:
                win.setWindowTitle("小雨办公工具 - Pro版")
                if hasattr(win, "activation_manager"):
                    win.activation_manager._cached = {"activated": True, "license_type": "pro"}
                    win.update_activation_status()
                    win.update_tab_permissions()

            default_page = cfg.get_config("UI", "default_page", "符号处理")
            if default_page == "符号与公式助手":
                if hasattr(win, 'show_symbol_panel'):
                    win.show_symbol_panel()
            else:
                win.show()
                win.raise_()
                tab_map = {"符号处理": 0, "表格编辑": 1, "文本处理": 2, "工具箱": 3}
                if default_page in tab_map:
                    win.tab_widget.setCurrentIndex(tab_map[default_page])

        except Exception as e:
            import traceback
            QMessageBox.critical(None, "启动失败", f"{str(e)}\n{traceback.format_exc()}")
            app.quit()

    QTimer.singleShot(0, late_init)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
