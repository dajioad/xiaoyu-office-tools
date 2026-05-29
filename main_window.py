# main_window.py
import os
import json
import sys
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTabWidget,
    QTextEdit, QPushButton, QLabel, QProgressBar, QMessageBox, QSplitter, QMenu,
    QStatusBar, QLineEdit, QScrollArea, QGroupBox, QSizePolicy, QFrame, QListWidget,
    QListWidgetItem, QApplication, QFileDialog, QSystemTrayIcon, QDialog, QFormLayout,
    QCheckBox, QComboBox, QInputDialog
)
from PySide6.QtGui import QKeySequence, QShortcut, QIcon, QMouseEvent, QFont, QAction, QPixmap, QCursor
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtCore import Qt, QTimer, Signal, QSize, QObject, QPropertyAnimation, QEasingCurve

import qtawesome as qta

from utils.text_processor import TextProcessor
from utils.logger import get_logger
from ui.guide import GuideManager
from ui.toolbox import ToolBoxWidget
from ui.symbol_panel import SymbolPanel
from ui.function_tutorial import FunctionTutorialWidget
from ui.problem_solver import ProblemSolverWidget

logger = get_logger()

APP_NAME = "小雨办公工具"
VERSION = "1.0"
DEFAULT_THEME = "blue"
MAX_OVERLAY_COUNT = 10
MAX_SYMBOL_HISTORY = 10

def _get_safe_font():
    import os
    import platform
    system = platform.system()
    if system == "Windows":
        safe_fonts = ["Microsoft YaHei", "Segoe UI", "Arial"]
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts", 0, winreg.KEY_READ) as key:
                available_fonts = []
                try:
                    i = 0
                    while True:
                        name, _, _ = winreg.EnumValue(key, i)
                        available_fonts.append(name)
                        i += 1
                except WindowsError:
                    pass
                for font in safe_fonts:
                    for avail in available_fonts:
                        if font.lower() in avail.lower():
                            return font
        except:
            pass
        return "Segoe UI"
    elif system == "Darwin":
        return "PingFang SC"
    else:
        return "Noto Sans CJK SC"

THEME_FONT = _get_safe_font()

BASE_PATH = Path(os.path.dirname(os.path.abspath(__file__)))
RESOURCE_PATH = BASE_PATH / "resources"
ICON_PATH = RESOURCE_PATH / "icons"
for path in [RESOURCE_PATH, ICON_PATH]:
    path.mkdir(exist_ok=True)

ICON_SIZE_SMALL = QSize(16, 16)
ICON_SIZE_MEDIUM = QSize(20, 20)
ICON_SIZE_LARGE = QSize(24, 24)

class EditableTextEdit(QTextEdit):
    double_clicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        super().mouseDoubleClickEvent(event)
        self.double_clicked.emit()

class ThemeManager:
    THEMES = {
        "blue": {
            "name": "现代蓝色",
            "primary": "#3b82f6",
            "primary_light": "#dbeafe",
            "primary_dark": "#2563eb",
            "bg": "#f8fafc",
            "card": "#ffffff",
            "text": "#1e293b",
            "text_secondary": "#64748b",
            "border": "#e2e8f0",
            "shadow": "rgba(15,23,42,0.08)",
            "pro_bg": "#dbeafe",
            "pro_text": "#f59e0b",
            "pro_border": "#3b82f6",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "orange": {
            "name": "活力橙色",
            "primary": "#f97316",
            "primary_light": "#ffedd5",
            "primary_dark": "#ea580c",
            "bg": "#fefcfb",
            "card": "#ffffff",
            "text": "#1e293b",
            "text_secondary": "#78716c",
            "border": "#fed7aa",
            "shadow": "rgba(15,23,42,0.08)",
            "is_pro": True,
            "pro_bg": "#ffedd5",
            "pro_text": "#eab308",
            "pro_border": "#f97316",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "dark_blue": {
            "name": "商务深蓝",
            "primary": "#1e3a8a",
            "primary_light": "#dbeafe",
            "primary_dark": "#1e40af",
            "bg": "#f1f5f9",
            "card": "#ffffff",
            "text": "#0f172a",
            "text_secondary": "#475569",
            "border": "#cbd5e1",
            "shadow": "rgba(15,23,42,0.12)",
            "is_pro": True,
            "pro_bg": "#e0e7ff",
            "pro_text": "#eab308",
            "pro_border": "#1e3a8a",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "green": {
            "name": "护眼豆沙绿",
            "primary": "#10b981",
            "primary_light": "#d1fae5",
            "primary_dark": "#059669",
            "bg": "#f0fdf4",
            "card": "#ffffff",
            "text": "#14532d",
            "text_secondary": "#45759d",
            "border": "#a7f3d0",
            "shadow": "rgba(16,185,129,0.08)",
            "is_pro": True,
            "pro_bg": "#d1fae5",
            "pro_text": "#ca8a04",
            "pro_border": "#10b981",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "pink": {
            "name": "樱花粉",
            "primary": "#ec4899",
            "primary_light": "#fce7f3",
            "primary_dark": "#db2777",
            "bg": "#fdf2f8",
            "card": "#ffffff",
            "text": "#831843",
            "text_secondary": "#9d174d",
            "border": "#fbcfe8",
            "shadow": "rgba(236,72,153,0.08)",
            "is_pro": True,
            "pro_bg": "#fce7f3",
            "pro_text": "#eab308",
            "pro_border": "#ec4899",
            "success": "#10b981",
            "warning": "#f59e0b",
            "error": "#ef4444"
        },
        "dark": {
            "name": "暗黑模式",
            "primary": "#60a5fa",
            "primary_light": "#1e3a5f",
            "primary_dark": "#3b82f6",
            "bg": "#0f172a",
            "card": "#1e293b",
            "text": "#f1f5f9",
            "text_secondary": "#94a3b8",
            "border": "#334155",
            "shadow": "rgba(0,0,0,0.5)",
            "selection_bg": "#2563eb",
            "selection_text": "#ffffff",
            "is_pro": True,
            "pro_bg": "#1f2937",
            "pro_text": "#fbbf24",
            "pro_border": "#60a5fa",
            "success": "#34d399",
            "warning": "#f59e0b",
            "error": "#ef4444"
        }
    }
    
    def __init__(self):
        self.current_theme = "blue"
        self._stylesheet_cache = {}
    
    def get_theme(self, theme_name=None):
        if theme_name is None:
            theme_name = self.current_theme
        return self.THEMES.get(theme_name, self.THEMES["blue"])
    
    def set_theme(self, theme_name):
        if theme_name in self.THEMES:
            self.current_theme = theme_name
            self._stylesheet_cache.pop(theme_name, None)
    
    def is_pro_theme(self, theme_name):
        theme = self.THEMES.get(theme_name)
        return theme and theme.get("is_pro", False)
    
    def generate_stylesheet(self, theme_name=None):
        theme_name = theme_name or self.current_theme
        if theme_name in self._stylesheet_cache:
            return self._stylesheet_cache[theme_name]
        theme = self.get_theme(theme_name)
        primary = theme["primary"]
        primary_light = theme["primary_light"]
        primary_dark = theme["primary_dark"]
        bg = theme["bg"]
        card = theme["card"]
        text = theme["text"]
        text_secondary = theme["text_secondary"]
        border = theme["border"]
        pro_bg = theme.get("pro_bg", "#2A2A2A")
        pro_text = theme.get("pro_text", "#D4AF37")
        pro_border = theme.get("pro_border", "#D4AF37")
        
        # 判断是否是暗黑模式
        is_dark = theme_name == "dark"
        
        # 计算主题特定的颜色
        card_hover_bg = "#334155" if is_dark else card
        button_bg = "#334155" if is_dark else card
        button_border = "#475569" if is_dark else border
        scrollbar_handle = "#475569" if is_dark else border
        
        tab_style = f"""
            QTabWidget::pane {{
                border: none;
                background-color: transparent;
            }}
            QTabBar::tab {{
                background-color: transparent;
                border: none;
                padding: 10px 24px;
                margin-right: 8px;
                color: {text_secondary};
                border-bottom: 2px solid transparent;
                border-radius: 12px 12px 0 0;
                font-weight: 500;
                transition: all 0.2s;
            }}
            QTabBar::tab:hover {{
                color: {primary};
                background-color: {primary}20;
                border-bottom-color: {primary}60;
                transform: translateY(-1px);
            }}
            QTabBar::tab:selected {{
                color: {primary};
                border-bottom: 2px solid {primary};
                background-color: {card};
                font-weight: 600;
            }}
        """
        
        # 统一美观的滚动条样式
        scrollbar_style = f"""
            QScrollBar:vertical {{
                width: 10px;
                background-color: {bg};
                border-radius: 5px;
                margin: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {scrollbar_handle};
                border-radius: 5px;
                min-height: 40px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {primary};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                height: 10px;
                background-color: {bg};
                border-radius: 5px;
                margin: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {scrollbar_handle};
                border-radius: 5px;
                min-width: 40px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {primary};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
        
        # 统一精美的符号按钮样式
        symbol_button_style = f"""
            .SymbolButton {{
                background-color: {button_bg};
                border: 2px solid {button_border};
                border-radius: 12px;
                font-size: 13px;
                min-width: 90px;
                max-width: 110px;
                min-height: 44px;
                transition: all 0.2s;
            }}
            .SymbolButton:hover {{
                border-color: {primary};
                background-color: {primary_light};
                transform: translateY(-2px);
                box-shadow: 0 4px 16px {primary}30;
            }}
            .SymbolButton:pressed {{
                transform: translateY(0);
            }}
            .SymbolButton[selected="true"] {{
                background-color: {primary};
                color: white;
                border-color: {primary};
                box-shadow: 0 0 20px {primary}50;
            }}
        """
        
        # 统一精美的工具按钮样式
        toolbar_button_style = f"""
            .ToolbarButton {{
                background-color: {button_bg};
                border: 1px solid {button_border};
                border-radius: 8px;
                padding: 6px 12px;
                color: {text};
                font-size: 13px;
                transition: all 0.2s ease;
            }}
            .ToolbarButton:hover {{
                border-color: {primary};
                color: {primary};
                background-color: {primary_light};
                transform: translateY(-1px);
                box-shadow: 0 2px 12px {primary}20;
            }}
        """
        
        # 统一精美的位置按钮样式
        position_button_style = f"""
            .PositionButton {{
                background-color: {button_bg};
                border: 2px solid {button_border};
                border-radius: 10px;
                font-size: 13px;
                min-height: 36px;
                padding: 4px 16px;
                transition: all 0.2s;
            }}
            .PositionButton:hover {{
                border-color: {primary};
                background-color: {primary_light};
                transform: translateY(-1px);
            }}
        """
        
        # 统一精美的文本编辑框样式
        text_edit_style = f"""
            .ModernTextEdit, .ResultTextEdit {{
                background-color: {button_bg};
                border: 2px solid {button_border};
                border-radius: 14px;
                padding: 12px;
                color: {text};
                transition: border 0.2s, box-shadow 0.2s;
            }}
            .ModernTextEdit:focus, .ResultTextEdit:focus {{
                border-color: {primary};
                box-shadow: 0 0 0 3px {primary}35;
            }}
        """
        
        # 统一精美的列表样式
        list_style = f"""
            QListWidget {{
                background-color: {button_bg};
                alternate-background-color: {button_bg};
                border: 1px solid {button_border};
                border-radius: 8px;
            }}
            QListWidget::item {{
                background-color: {button_bg};
                color: {text};
                padding: 8px 12px;
                border-radius: 4px;
            }}
            QListWidget::item:selected {{
                background-color: {primary};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {primary_light};
                color: {primary};
            }}
        """
        
        # 统一精美的菜单样式
        menu_style = f"""
            QMenu {{
                background-color: {button_bg};
                border: 1px solid {button_border};
                border-radius: 12px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background-color: {primary if is_dark else primary_light};
                color: {'white' if is_dark else primary};
            }}
        """
        
        stylesheet = f"""
            QWidget {{
                background-color: {bg};
                color: {text};
            }}
            .main-card {{
                background-color: {card};
                border-radius: 16px;
                border: 1px solid {border};
                box-shadow: 0 4px 20px {theme.get('shadow', 'rgba(0,0,0,0.08)')};
            }}
            .PrimaryButton {{
                background-color: {primary};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }}
            .PrimaryButton:hover {{
                background-color: {primary_dark};
            }}
            .ProButton {{
                background: {pro_bg};
                color: {pro_text};
                border: 1px solid {pro_border};
                border-radius: 8px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 14px;
                min-height: 32px;
            }}
            .ProButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {pro_bg}, stop:1 {primary_dark});
                color: #FFD700;
                border-color: #FFD700;
            }}
            {toolbar_button_style}
            {symbol_button_style}
            {position_button_style}
            {text_edit_style}
            {tab_style}
            {scrollbar_style}
            QStatusBar {{
                background-color: {card};
                border-top: 1px solid {border};
                color: {text_secondary};
                padding: 4px 12px;
                font-size: 12px;
            }}
            QSplitter::handle {{
                background-color: {border};
            }}
            QSplitter::handle:hover {{
                background-color: {primary};
            }}
            {menu_style}
            {list_style}
            QMessageBox {{
                background-color: {card};
            }}
            QMessageBox QLabel {{
                color: {text};
                font-size: 14px;
                padding: 8px;
            }}
            QMessageBox QPushButton {{
                background-color: {button_bg};
                border: 1px solid {button_border};
                border-radius: 8px;
                padding: 8px 20px;
                color: {text};
                font-size: 13px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {primary_light};
                border-color: {primary};
                color: {primary};
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {primary};
                color: white;
            }}
        """
        self._stylesheet_cache[theme_name] = stylesheet
        return stylesheet

class MainWindow(QMainWindow):
    def __init__(self, config_manager=None):
        super().__init__()
        if config_manager is None:
            from utils.config import ConfigManager
            config_manager = ConfigManager()
            config_manager.init_config()
        self.config_manager = config_manager
        self.text_processor = TextProcessor()
        self.text_processor.insert_mode = "single"
        self.overlay_chain = []
        self.filter_history = []  # 筛选历史记录
        self.now_sym = None
        self.now_pos = None
        self.origin_text = ""
        self.build_text = ""

        self.theme_manager = ThemeManager()

        self._init_basic_configs()

        self._excel_cache = None
        self._word_cache = None
        self._toolbox_cache = None
        self._excel_tab_loaded = False
        self._word_tab_loaded = False
        self._toolbox_tab_loaded = False

        self._guide_triggered = {}
        self._guide_initialized = False
        
        self._symbol_grid_cache = None

        import os
        from pathlib import Path
        app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = app_dir / "小雨办公工具.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self.init_ui()
        self.init_system_tray()

    def update_split_mode(self, split_mode):
        """更新所有子组件的分隔模式"""
        self.split_mode = split_mode
        if hasattr(self, 'excel_widget') and self.excel_widget:
            if hasattr(self.excel_widget, 'update_split_mode'):
                self.excel_widget.update_split_mode(split_mode)
        if hasattr(self, 'word_widget') and self.word_widget:
            if hasattr(self.word_widget, 'update_split_mode'):
                self.word_widget.update_split_mode(split_mode)
        # 如果 symbol_panel 也需要，可以添加

    def apply_font(self, font_family: str, font_size: str):
        """应用字体族和字号，同时保持缩放比例"""
        try:
            base_font_size = int(font_size)
            # 获取当前缩放比例（默认100%）
            scale_text = self.config_manager.get_config("UI", "scale_factor", "100")
            scale_percent = int(scale_text.replace('%', ''))
            final_font_size = max(8, int(base_font_size * scale_percent / 100))
            
            font = QFont(font_family, final_font_size)
            QApplication.setFont(font)
            self.setFont(font)
            for child in self.findChildren(QWidget):
                child.setFont(font)
            
            self.config_manager.set_config("UI", "font_family", font_family)
            self.config_manager.set_config("UI", "font_size", str(base_font_size))
        except Exception as e:
            logger.error(f"字体应用失败: {e}", exc_info=True)

    def apply_scale_factor(self, scale_text: str):
        """根据缩放百分比调整全局字体大小，实现界面缩放"""
        try:
            # 从配置读取当前基础字号（如果没有则使用默认值）
            base_font_size = int(self.config_manager.get_config("UI", "font_size", "10"))
            scale_percent = int(scale_text.replace('%', ''))
            new_font_size = max(8, int(base_font_size * scale_percent / 100))
            
            font_family = self.config_manager.get_config("UI", "font_family", "微软雅黑")
            font = QFont(font_family, new_font_size)
            QApplication.setFont(font)
            self.setFont(font)
            
            # 更新配置中的字号（可选，保留缩放后的字号）
            self.config_manager.set_config("UI", "font_size", str(new_font_size))
            
            # 刷新所有子控件的字体
            for child in self.findChildren(QWidget):
                child.setFont(font)
            
        except Exception as e:
            logger.error(f"缩放应用失败: {e}", exc_info=True)

    def apply_animation(self, enabled: bool):
        self._enable_animation = enabled

    def apply_layout_mode(self, mode: str):
        if mode == "紧凑":
            self.centralWidget().layout().setContentsMargins(4, 4, 4, 4)
            self.centralWidget().layout().setSpacing(4)
        else:
            self.centralWidget().layout().setContentsMargins(12, 12, 12, 12)
            self.centralWidget().layout().setSpacing(8)

    def apply_tray_behavior(self, behavior: str):
        pass

    def update_tray_icon_visibility(self):
        show_tray = self.config_manager.get_config("UI", "show_tray_icon", "true") == "true"
        if show_tray:
            if self.tray_icon is None:
                self.init_system_tray()
            if self.tray_icon:
                self.tray_icon.show()
        else:
            if self.tray_icon:
                self.tray_icon.hide()

    def toggle_symbol_panel_theme(self):
        if self.symbol_panel is None:
            from ui.symbol_panel import SymbolPanel
            self.symbol_panel = SymbolPanel(self)
        self.symbol_panel.toggle_panel_theme()
        self.update_dark_mode_action_icon()

    def _init_basic_configs(self):
        self.symbol_history = []
        self.max_symbol_history = 10
        self.auto_remove_blank_lines = False
        self.auto_remove_extra_spaces = False
        self.auto_remove_all_whitespace = False
        self.skip_empty_cells = False
        self.auto_save_history_enabled = False
        self.history_count = 10
        self.fail_notify_enabled = True
        self.process_thread = None
        self.is_processing = False
        self.full_width = True
        self.custom_delimiter = None
        self.split_mode = 0
        self.current_operation = None
        self.current_position = None
        self.recent_files = []
        self.tray_icon = None
        self.minimize_to_tray = True

        from utils.secure_activation import SecureActivationManager
        self.activation_manager = SecureActivationManager(self.config_manager.data_dir)
        self.license_type = self.activation_manager.get_license_type()

        self.guide_manager = GuideManager(self.config_manager, self)
        self.symbol_panel = None
        
        self._reminder_timer = None

        self.disabled_default_symbols = []
        self.custom_map = {}
        self.all_symbols = []
        self.disabled_default_formulas = []
        self._configs_loaded = False
    
    def _load_configs_lazy(self):
        if self._configs_loaded:
            return
        self.load_disabled_symbols()
        self.load_custom_symbols_into_list()
        self.all_symbols = self.build_all_symbols()
        self._load_disabled_formulas()
        # 提醒功能已移除
        self._configs_loaded = True

    def _setup_reminder(self):
        import traceback
        from datetime import datetime
        def log(msg):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [_setup_reminder] {msg}")
        try:
            log("开始设置提醒...")
            if hasattr(self, '_reminder_timer') and self._reminder_timer:
                self._reminder_timer.stop()
            enabled = self.config_manager.get_config("Reminder", "enabled", "false").lower() == "true"
            if not enabled:
                return
            interval_text = self.config_manager.get_config("Reminder", "interval", "1小时")
            interval_map = {"30分钟": 1800, "1小时": 3600, "2小时": 7200, "4小时": 14400}
            if interval_text == "自定义":
                try:
                    custom_minutes = int(self.config_manager.get_config("Reminder", "custom_minutes", "60"))
                    interval_seconds = custom_minutes * 60
                except:
                    interval_seconds = 3600
            else:
                interval_seconds = interval_map.get(interval_text, 3600)
            log(f"  间隔: {interval_seconds} 秒")
            if not hasattr(self, '_reminder_timer') or not self._reminder_timer:
                self._reminder_timer = QTimer(self)
                self._reminder_timer.timeout.connect(self._show_reminder)
            self._reminder_timer.start(interval_seconds * 1000)
            logger.info("提醒设置完成")
        except Exception as e:
            logger.error(f"提醒设置异常: {e}", exc_info=True)
    
    def _show_themed_message_box(self, title, text, icon=QMessageBox.Information, detailed_text=None, standard_buttons=QMessageBox.Ok):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        if detailed_text:
            msg_box.setDetailedText(detailed_text)
        msg_box.setStandardButtons(standard_buttons)
        msg_box.setStyleSheet(self.theme_manager.generate_stylesheet())
        return msg_box.exec()

    def show_warning(self, title, text):
        return self._show_themed_message_box(title, text, QMessageBox.Warning)

    def show_info(self, title, text):
        return self._show_themed_message_box(title, text, QMessageBox.Information)

    def show_error(self, title, text):
        return self._show_themed_message_box(title, text, QMessageBox.Critical)

    def show_question(self, title, text, buttons=QMessageBox.Yes | QMessageBox.No):
        return self._show_themed_message_box(title, text, QMessageBox.Question, standard_buttons=buttons)

    def _show_reminder(self):
        message = self.config_manager.get_config("Reminder", "message", "起来活动一下，注意休息哦！")
        self._show_themed_message_box("提醒", message, QMessageBox.Information)

    def _load_disabled_formulas(self):
        disabled_str = self.config_manager.get_config("SymbolPanel", "disabled_default_formulas", "[]")
        try:
            self.disabled_default_formulas = json.loads(disabled_str)
        except:
            self.disabled_default_formulas = []
        if not isinstance(self.disabled_default_formulas, list):
            self.disabled_default_formulas = []

    def load_disabled_symbols(self):
        disabled_str = self.config_manager.get_config("Symbols", "disabled_default_symbols", "")
        if not disabled_str:
            self.disabled_default_symbols = []
        else:
            try:
                self.disabled_default_symbols = json.loads(disabled_str)
            except:
                self.disabled_default_symbols = [s for s in disabled_str.split(",") if s]

    def save_disabled_symbols(self):
        disabled_str = json.dumps(self.disabled_default_symbols)
        self.config_manager.set_config("Symbols", "disabled_default_symbols", disabled_str)

    def build_all_symbols(self):
        DEFAULT_SYMBOL_INFO = {
            "double_quote": ("双引号", "\"\""),
            "single_quote": ("单引号", "''"),
            "book_title": ("书名号", "《》"),
            "comma": ("逗号", "，"),
            "period": ("句号", "。"),
            "colon": ("冒号", "："),
            "semicolon": ("分号", "；"),
            "bracket_paren": ("小括号", "()"),
            "bracket_square": ("中括号", "[]"),
            "bracket_curly": ("大括号", "{}"),
            "bracket_corner": ("角括号", "【】"),
            "enum_comma": ("顿号", "、"),
            "percent": ("百分号", "%"),
            "sqrt": ("根号", "√"),
            "at": ("艾特", "@"),
            "hash": ("井号", "#"),
            "ellipsis": ("省略号", "…"),
            "middle_dot": ("间隔号", "·"),
            "question": ("问号", "？"),
            "exclamation": ("感叹号", "！"),
            "plus": ("加号", "+"),
            "minus": ("减号", "-"),
        }
        all_default = list(DEFAULT_SYMBOL_INFO.items())
        custom_defaults = self.config_manager.get_config("Symbols", "custom_defaults", "{}")
        try:
            custom_defaults_data = json.loads(custom_defaults)
        except:
            custom_defaults_data = {}
        active_defaults = []
        for key, (orig_name, orig_value) in all_default:
            if key in self.disabled_default_symbols:
                continue
            display_value = orig_value
            if key in custom_defaults_data and "value" in custom_defaults_data[key]:
                display_value = custom_defaults_data[key]["value"]
            active_defaults.append((display_value, key))
        customs = [(sym, key) for key, sym in self.custom_map.items()]
        return active_defaults + customs

    def restore_all_default_symbols(self):
        if self.disabled_default_symbols:
            self.disabled_default_symbols.clear()
            self.save_disabled_symbols()
            self.all_symbols = self.build_all_symbols()
            self.render_symbol_buttons()
            if hasattr(self, 'symbol_panel') and self.symbol_panel:
                self.symbol_panel.refresh_symbol_grid()
            self.show_toast("已恢复所有默认符号")
        else:
            self.show_toast("没有隐藏的默认符号")

    def load_custom_symbols_into_list(self):
        custom_str = self.config_manager.get_config("Symbols", "custom_symbols", "")
        if custom_str:
            try:
                custom_list = json.loads(custom_str)
                for key, value in custom_list:
                    self.custom_map[key] = value
            except:
                symbols = custom_str.replace("%%", "%").split("|")
                seen = set()
                for sym in symbols:
                    sym = sym.strip()
                    if sym and sym not in seen:
                        seen.add(sym)
                        self.custom_map[sym] = sym

    def render_symbol_buttons(self):
        try:
            self._load_configs_lazy()
            if not hasattr(self, 'symbol_grid') or self.symbol_grid is None:
                print("错误：symbol_grid 未准备好")
                return

            self.symbol_grid_widget.setUpdatesEnabled(False)

            # 彻底清空旧的网格
            while self.symbol_grid.count():
                item = self.symbol_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            self.symbol_buttons = {}
            self._symbol_render_index = 0

            # 每行6列，按钮更宽敞
            buttons_per_row = 6
            cfg = self.get_symbol_config()
            total = len(self.all_symbols)

            for idx in range(total):
                display_text, key = self.all_symbols[idx]
                row = idx // buttons_per_row
                col = idx % buttons_per_row
                btn_text = display_text.replace("&", "&&")
                btn = QPushButton(btn_text)
                btn.setProperty("class", "SymbolButton")
                # 高度适中，宽度略宽，每行6个更舒服
                btn.setMinimumHeight(40)
                btn.setMaximumHeight(40)
                btn.setMinimumWidth(90)
                btn.setMaximumWidth(120)
                chinese_name = cfg.get(key, (None, None, None, key))[3] if key in cfg else key
                btn.setToolTip(f"{chinese_name} ")
                btn.clicked.connect(lambda checked, k=key, b=btn: self.on_symbol_click(k, b))
                self.symbol_grid.addWidget(btn, row, col)
                self.symbol_buttons[key] = btn

            self.symbol_grid_widget.setUpdatesEnabled(True)
            self.symbol_grid_widget.update()
            self.symbol_grid_widget.parent().update()

        except Exception as e:
            logger.error(f"渲染符号按钮异常: {e}", exc_info=True)

    def _symbol_render_batch(self):
        pass

    def _replace_symbol_grid(self, cached_grid):
        if self.symbol_grid_widget is cached_grid:
            return
        parent_layout = self.symbol_grid_widget.parent().layout()
        if parent_layout:
            parent_layout.removeWidget(self.symbol_grid_widget)
        self.symbol_grid_widget.deleteLater()
        self.symbol_grid_widget = cached_grid
        if parent_layout:
            parent_layout.addWidget(self.symbol_grid_widget)

    def reload_custom_symbol_buttons(self):
        self.custom_map.clear()
        self.load_custom_symbols_into_list()
        self.all_symbols = self.build_all_symbols()
        self.render_symbol_buttons()
        if hasattr(self, 'symbol_panel') and self.symbol_panel:
            self.symbol_panel.refresh_symbol_grid()

    def _delayed_init_phase1(self):
        self.load_theme_settings()
        self.load_settings()
        self.load_recent_files()
        self.apply_theme()
        
        font_family = self.config_manager.get_config("UI", "font_family", "微软雅黑")
        font_size = self.config_manager.get_config("UI", "font_size", "10")
        scale_text = self.config_manager.get_config("UI", "scale_factor", "100")
        # 先设置基础字体，再根据缩放调整
        self.apply_font(font_family, font_size)

    def _delayed_init_phase2(self):
        self.init_shortcuts()

    def _delayed_init_phase3(self):
        self._load_configs_lazy()
        self.render_symbol_buttons()
        self.refresh_symbol_button_labels()
        self.guide_manager = GuideManager(self.config_manager, self)

    def _delayed_init_phase4(self):
        try:
            self.init_system_tray()
        except Exception as e:
            logger.error(f"初始化系统托盘失败: {e}", exc_info=True)
        QTimer.singleShot(200, self.check_and_show_guide)

    def load_theme_settings(self):
        theme_name = self.config_manager.get_config("App", "theme", "blue")
        if self.theme_manager.is_pro_theme(theme_name) and not self.activation_manager.is_activated():
            self.theme_manager.set_theme("blue")
            self.save_theme_settings()
        else:
            self.theme_manager.set_theme(theme_name)

    def save_theme_settings(self):
        if not self.activation_manager.is_activated() and self.theme_manager.is_pro_theme(self.theme_manager.current_theme):
            self.theme_manager.set_theme("blue")
        self.config_manager.set_config("App", "theme", self.theme_manager.current_theme)

    def apply_theme(self):
        import traceback
        from datetime import datetime
        def log(msg):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [apply_theme] {msg}")
        try:
            log("开始应用主题...")
            log(f"当前主题: {self.theme_manager.current_theme}")
            stylesheet = self.theme_manager.generate_stylesheet()
            self.setStyleSheet(stylesheet)
            self.update_dark_mode_action_icon()
            self._apply_theme_to_children()
        except Exception as e:
            logger.error(f"主题应用异常: {e}", exc_info=True)

    def _apply_theme_to_children(self):
        dark_themes = ["dark"]
        is_dark = self.theme_manager.current_theme in dark_themes
        if hasattr(self, 'toolbox_widget') and self.toolbox_widget:
            self.toolbox_widget.apply_theme()
        if hasattr(self, 'excel_widget') and self.excel_widget:
            if hasattr(self.excel_widget, 'apply_theme'):
                self.excel_widget.apply_theme()
        if hasattr(self, 'word_widget') and self.word_widget:
            if hasattr(self.word_widget, 'apply_theme'):
                self.word_widget.apply_theme()
        if hasattr(self, 'symbol_panel') and self.symbol_panel:
            if hasattr(self.symbol_panel, 'apply_theme'):
                self.symbol_panel.apply_theme()
        if hasattr(self, 'guide_manager') and self.guide_manager:
            if hasattr(self.guide_manager, 'apply_theme'):
                self.guide_manager.apply_theme()
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme()
            icon_name = ["hashtag", "table", "file-word", "toolbox", "book", "wrench"][i]
            icon_color = '#e0e0e0' if is_dark else '#409eff'
            self.tab_widget.setTabIcon(i, qta.icon(f'fa5s.{icon_name}', color=icon_color))
        if is_dark:
            self._update_toolbar_for_dark_mode()
            self._update_status_bar_for_dark_mode()
        else:
            self._reset_toolbar_for_light_mode()
            self._reset_status_bar_for_light_mode()

    def _update_status_bar_for_dark_mode(self):
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border-top: 1px solid #3a3a3a;
            }
            QStatusBar QLabel {
                background-color: transparent;
                border: none;
                color: #e0e0e0;
            }
        """)
        self.char_count_label.setStyleSheet("color: #e0e0e0; background: transparent; border: none;")
        self.status_label.setStyleSheet("color: #409eff; background: transparent; border: none;")
        self.license_label.setStyleSheet("color: #a0a0a0; background: transparent; border: none;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 4px;
                text-align: center;
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #409eff;
            }
        """)

    def _reset_status_bar_for_light_mode(self):
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #f5f5f5;
                color: #303133;
                border-top: 1px solid #e4e7ed;
            }
            QStatusBar QLabel {
                background-color: transparent;
                border: none;
                color: #303133;
            }
        """)
        self.char_count_label.setStyleSheet("color: #606266; background: transparent; border: none;")
        self.status_label.setStyleSheet("color: #409eff; background: transparent; border: none;")
        self.license_label.setStyleSheet("color: #909399; background: transparent; border: none;")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e4e7ed;
                border-radius: 4px;
                text-align: center;
                background-color: white;
                color: #606266;
            }
            QProgressBar::chunk {
                border-radius: 3px;
                background-color: #409eff;
            }
        """)

    def _update_toolbar_for_dark_mode(self):
        for child in self.findChildren(QPushButton):
            obj_name = child.objectName()
            if obj_name in ["ToolbarButton", "SettingsButton"]:
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #2d2d2d;
                        color: #e0e0e0;
                        border: 1px solid #3a3a3a;
                        border-radius: 6px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #383838;
                    }
                """)
            elif obj_name == "PrimaryButton":
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #409eff;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #66b1ff;
                    }
                """)

    def _reset_toolbar_for_light_mode(self):
        for child in self.findChildren(QPushButton):
            obj_name = child.objectName()
            if obj_name in ["ToolbarButton", "SettingsButton"]:
                child.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        color: #606266;
                        border: 1px solid #dcdfe6;
                        border-radius: 6px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #f5f7fa;
                    }
                """)
            elif obj_name == "PrimaryButton":
                child.setStyleSheet("""
                    QPushButton {
                        background-color: #409eff;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 6px 12px;
                    }
                    QPushButton:hover {
                        background-color: #66b1ff;
                    }
                """)

    def update_dynamic_styles(self):
        pass

    def overlay_chain_symbols(self):
        return [op["symbol"] for op in self.overlay_chain]

    def init_ui(self):
        self.setWindowTitle("小雨办公工具")
        self.setMinimumSize(1100, 750)
        self.resize(1200, 800)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        top_bar = self.create_top_toolbar()
        main_layout.addWidget(top_bar)
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.addTab(self.create_symbol_tab(), "  符号处理")
        self._excel_placeholder = QWidget()
        self._word_placeholder = QWidget()
        self._toolbox_placeholder = QWidget()
        self.tab_widget.addTab(self._excel_placeholder, "  表格编辑")
        self.tab_widget.addTab(self._word_placeholder, "  文本处理")
        self.tab_widget.addTab(self._toolbox_placeholder, "  工具箱")
        # 使用分离后的组件
        function_widget = FunctionTutorialWidget(self)
        self.tab_widget.addTab(function_widget, "  函数教程")
        problem_widget = ProblemSolverWidget(self)
        self.tab_widget.addTab(problem_widget, "  问题解决")
        self._excel_widget_created = False
        self._word_widget_created = False
        self._toolbox_widget_created = False
        for i, icon_name in enumerate(["hashtag", "table", "file-word", "toolbox", "book", "wrench"]):
            self.tab_widget.setTabIcon(i, qta.icon(f'fa5s.{icon_name}', color='#409eff'))
        main_layout.addWidget(self.tab_widget, stretch=1)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        self.status_bar = self.statusBar()
        self.status_bar.setContentsMargins(8, 2, 8, 2)
        self.char_count_label = QLabel("字符数: 0/1000")
        self.status_label = QLabel("就绪")
        self.license_label = QLabel(self.get_license_text())
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.hide()
        self.status_bar.addWidget(self.char_count_label)
        self.status_bar.addPermanentWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.license_label)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.update_activation_status()

        QTimer.singleShot(100, self._delayed_init_phase1)
        QTimer.singleShot(200, self._delayed_init_phase2)
        QTimer.singleShot(300, self._delayed_init_phase3)
        QTimer.singleShot(500, self._delayed_init_phase4)

    def create_top_toolbar(self):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve

        card = QFrame()
        card.setProperty("class", "main-card")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(10)

        self.settings_btn = QPushButton(" 设置")
        self.settings_btn.setIcon(qta.icon('fa5s.cog', color='#606266'))
        self.settings_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.settings_btn.clicked.connect(self.show_settings)
        self.settings_btn.setProperty("class", "ToolbarButton")
        layout.addWidget(self.settings_btn)

        self.recent_menu_btn = QPushButton(" 最近文件")
        self.recent_menu_btn.setIcon(qta.icon('fa5s.folder-open', color='#606266'))
        self.recent_menu_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.recent_menu_btn.setProperty("class", "ToolbarButton")
        self.recent_menu = QMenu()
        self.recent_menu_btn.setMenu(self.recent_menu)
        layout.addWidget(self.recent_menu_btn)
        self.update_recent_menu()

        layout.addStretch()

        self.pro_btn = QPushButton(" Pro版")
        self.pro_btn.setIcon(qta.icon('fa5s.gem', color='#D4AF37'))
        self.pro_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.pro_btn.clicked.connect(self.show_activation_dialog)
        self.pro_btn.setProperty("class", "ProButton")

        self.pro_btn.setToolTip(
            "✨ 升级 Pro 版，解锁全部高阶功能 ✨\n\n"
            "• 无限制 Excel/Word 编辑\n"
            "• 批量文件处理\n"
            "• 图片 OCR 与文字提取\n"
            "• 专属主题（暗黑/樱花粉等）\n"
            "• 无水印导出 PDF\n\n"
            "点击查看详情 →"
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.pro_btn.setGraphicsEffect(shadow)

        self.pro_btn_hover_anim = QPropertyAnimation(shadow, b"blurRadius")
        self.pro_btn_hover_anim.setDuration(200)
        self.pro_btn_hover_anim.setEasingCurve(QEasingCurve.OutCubic)

        def on_hover_enter(event):
            self.pro_btn_hover_anim.stop()
            self.pro_btn_hover_anim.setEndValue(18)
            self.pro_btn_hover_anim.start()
            self.pro_btn.setIcon(qta.icon('fa5s.gem', color='#FFD700'))
            event.accept()

        def on_hover_leave(event):
            self.pro_btn_hover_anim.stop()
            self.pro_btn_hover_anim.setEndValue(12)
            self.pro_btn_hover_anim.start()
            self.pro_btn.setIcon(qta.icon('fa5s.gem', color='#D4AF37'))
            event.accept()

        self.pro_btn.enterEvent = on_hover_enter
        self.pro_btn.leaveEvent = on_hover_leave

        self.pro_btn_scale_anim = QPropertyAnimation(self.pro_btn, b"geometry")
        self.pro_btn_scale_anim.setDuration(100)
        self.pro_btn_scale_anim.setEasingCurve(QEasingCurve.OutQuad)

        def on_press(event):
            geom = self.pro_btn.geometry()
            self.pro_btn_scale_anim.stop()
            self.pro_btn_scale_anim.setStartValue(geom)
            self.pro_btn_scale_anim.setEndValue(geom.adjusted(2, 1, -2, -1))
            self.pro_btn_scale_anim.start()
            QPushButton.mousePressEvent(self.pro_btn, event)

        def on_release(event):
            geom = self.pro_btn.geometry()
            self.pro_btn_scale_anim.stop()
            self.pro_btn_scale_anim.setStartValue(geom)
            self.pro_btn_scale_anim.setEndValue(geom.adjusted(-2, -1, 2, 1))
            self.pro_btn_scale_anim.start()
            QPushButton.mouseReleaseEvent(self.pro_btn, event)

        self.pro_btn.mousePressEvent = on_press
        self.pro_btn.mouseReleaseEvent = on_release

        layout.addWidget(self.pro_btn)

        return card

    def create_symbol_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ===== 上部内容区域（左右分栏，比例3:2） =====
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # ----- 左侧区域 (3/5) -----
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        # 输入区域
        input_section = QFrame()
        input_section.setProperty("class", "main-card")
        input_layout = QVBoxLayout(input_section)
        input_layout.setContentsMargins(12, 12, 12, 12)
        input_layout.setSpacing(8)

        input_title_layout = QHBoxLayout()
        input_icon_label = QLabel()
        input_icon_label.setPixmap(qta.icon('fa5s.file-alt', color='#409eff').pixmap(16, 16))
        input_title_layout.addWidget(input_icon_label)
        input_text_label = QLabel("输入文本")
        input_text_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #303133;")
        input_title_layout.addWidget(input_text_label)
        input_title_layout.addStretch()
        input_layout.addLayout(input_title_layout)

        self.input_text = QTextEdit()
        self.input_text.setProperty("class", "ModernTextEdit")
        self.input_text.setPlaceholderText("请输入需要处理的文本...")
        self.input_text.textChanged.connect(self.on_input_text_changed)
        input_layout.addWidget(self.input_text, stretch=1)

        # 转换按钮行
        btn_row_layout = QHBoxLayout()
        btn_row_layout.addStretch()
        self.transform_btn = QPushButton(" 转换")
        self.transform_btn.setIcon(qta.icon('fa5s.arrow-right', color='white'))
        self.transform_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.transform_btn.clicked.connect(self._do_text_transform)
        self.transform_btn.setProperty("class", "ToolbarButton")
        self.transform_btn.setMinimumHeight(36)
        self.transform_btn.setStyleSheet("background-color: #409eff; color: white; border-radius: 4px;")
        btn_row_layout.addWidget(self.transform_btn)

        clear_input_btn = QPushButton(" 清空输入")
        clear_input_btn.setIcon(qta.icon('fa5s.trash-alt', color='#606266'))
        clear_input_btn.setIconSize(ICON_SIZE_MEDIUM)
        clear_input_btn.clicked.connect(self.clear_input_only)
        clear_input_btn.setProperty("class", "ToolbarButton")
        clear_input_btn.setMinimumHeight(36)
        btn_row_layout.addWidget(clear_input_btn)
        input_layout.addLayout(btn_row_layout)

        left_layout.addWidget(input_section, stretch=2)

        # 符号与插入方式区域
        control_section = QFrame()
        control_section.setProperty("class", "main-card")
        control_layout = QVBoxLayout(control_section)
        control_layout.setContentsMargins(12, 12, 12, 12)
        control_layout.setSpacing(12)

        # 符号标题
        sym_title_layout = QHBoxLayout()
        sym_icon_label = QLabel()
        sym_icon_label.setPixmap(qta.icon('fa5s.bullseye', color='#409eff').pixmap(16, 16))
        sym_title_layout.addWidget(sym_icon_label)
        sym_text_label = QLabel("选择符号")
        sym_text_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #303133;")
        sym_title_layout.addWidget(sym_text_label)
        sym_title_layout.addStretch()
        control_layout.addLayout(sym_title_layout)

        self.symbol_scroll = QScrollArea()
        self.symbol_scroll.setWidgetResizable(True)
        self.symbol_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.symbol_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.symbol_scroll.setFrameShape(QFrame.NoFrame)
        self.symbol_scroll.setMinimumHeight(150)

        self.symbol_grid_widget = QWidget()
        self.symbol_grid = QGridLayout(self.symbol_grid_widget)
        self.symbol_grid.setSpacing(6)
        self.symbol_grid.setContentsMargins(0, 0, 0, 0)
        self.symbol_scroll.setWidget(self.symbol_grid_widget)
        control_layout.addWidget(self.symbol_scroll, stretch=1)

        # 插入方式标题
        pos_title_layout = QHBoxLayout()
        pos_icon_label = QLabel()
        pos_icon_label.setPixmap(qta.icon('fa5s.location-arrow', color='#409eff').pixmap(16, 16))
        pos_title_layout.addWidget(pos_icon_label)
        pos_text_label = QLabel("插入方式")
        pos_text_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #303133;")
        pos_title_layout.addWidget(pos_text_label)
        pos_title_layout.addStretch()
        control_layout.addLayout(pos_title_layout)

        pos_grid = QGridLayout()
        pos_grid.setSpacing(8)
        positions = [("头部", "head"), ("尾部", "tail"), ("两端", "both"), ("分隔", "split")]
        self.position_buttons = {}
        for idx, (name, key) in enumerate(positions):
            btn = QPushButton(name)
            btn.setProperty("class", "PositionButton")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked, p=key: self.set_position(p))
            pos_grid.addWidget(btn, 0, idx)
            self.position_buttons[key] = btn
        control_layout.addLayout(pos_grid)

        # 功能按钮
        tool_row = QHBoxLayout()
        tool_row.setSpacing(8)
        self.width_btn = QPushButton("全角")
        self.width_btn.setIcon(qta.icon('fa5s.text-width', color='#606266'))
        self.width_btn.setIconSize(ICON_SIZE_SMALL)
        self.width_btn.clicked.connect(self.toggle_width)
        self.width_btn.setProperty("class", "ToolbarButton")
        tool_row.addWidget(self.width_btn)
        self.symbol_lang_btn = QPushButton(" 中文符号")
        self.symbol_lang_btn.setIcon(qta.icon('fa5s.language', color='#606266'))
        self.symbol_lang_btn.setIconSize(ICON_SIZE_SMALL)
        self.symbol_lang_btn.clicked.connect(self.toggle_symbol_language)
        self.symbol_lang_btn.setProperty("class", "ToolbarButton")
        tool_row.addWidget(self.symbol_lang_btn)
        control_layout.addLayout(tool_row)

        # 历史记录
        hist_label = QLabel("⏪ 最近使用")
        hist_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        control_layout.addWidget(hist_label)
        hist_grid = QGridLayout()
        hist_grid.setSpacing(8)
        self.history_buttons = []
        for i in range(5):
            btn = QPushButton()
            btn.setProperty("class", "ToolbarButton")
            btn.setMinimumHeight(28)
            btn.setVisible(False)
            hist_grid.addWidget(btn, 0, i)
            self.history_buttons.append(btn)
        control_layout.addLayout(hist_grid)

        left_layout.addWidget(control_section, stretch=3)
        content_layout.addWidget(left_widget, 3)

        # ----- 右侧区域 (2/5) -----
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)

        # ===== 顶部工具栏（右上角） =====
        top_toolbar = QHBoxLayout()
        top_toolbar.setSpacing(8)

        top_toolbar.addStretch()  # 把按钮推到右边

        # 筛选按钮（右上角左侧）
        filter_btn = QPushButton(" 筛选")
        filter_btn.setIcon(qta.icon('fa5s.filter', color='#606266'))
        filter_btn.setIconSize(ICON_SIZE_MEDIUM)
        filter_btn.setMinimumHeight(34)
        filter_btn.setProperty("class", "ToolbarButton")
        filter_btn.clicked.connect(self.show_filter_dialog)
        top_toolbar.addWidget(filter_btn)

        # 应用叠加按钮（右上角右侧）
        self.overlay_btn = QPushButton(" 应用叠加")
        self.overlay_btn.setIcon(qta.icon('fa5s.layer-group', color='white'))
        self.overlay_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.overlay_btn.setMinimumHeight(34)
        self.overlay_btn.setProperty("class", "PrimaryButton")
        self.overlay_btn.setStyleSheet("""
            QPushButton.PrimaryButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #409eff, stop:1 #1e80ff);
                color: white;
                border: none;
                border-radius: 17px;
                font-weight: bold;
                font-size: 13px;
                padding: 4px 16px;
            }
            QPushButton.PrimaryButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66b1ff, stop:1 #409eff);
                box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
            }
            QPushButton.PrimaryButton:pressed {
                background: #1e80ff;
            }
        """)
        self.overlay_btn.clicked.connect(self.apply_overlay)
        top_toolbar.addWidget(self.overlay_btn)

        right_layout.addLayout(top_toolbar)

        # ===== 1. 预览区 =====
        preview_header = QHBoxLayout()
        preview_label = QLabel("👁️ 预览 (当前符号效果)")
        preview_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #606266;")
        preview_header.addWidget(preview_label)
        preview_header.addStretch()
        right_layout.addLayout(preview_header)

        self.ui_preview_area = QTextEdit()
        self.ui_preview_area.setProperty("class", "ResultTextEdit")
        self.ui_preview_area.setReadOnly(True)
        self.ui_preview_area.setPlaceholderText("选择符号和位置后，这里显示当前符号应用到原始文本的效果...")
        self.ui_preview_area.setMaximumHeight(120)
        right_layout.addWidget(self.ui_preview_area)

        # 预览操作行（复制左对齐，清空右对齐）
        preview_action_row = QHBoxLayout()
        preview_action_row.setSpacing(12)

        copy_preview_btn = QPushButton(" 复制预览")
        copy_preview_btn.setIcon(qta.icon('fa5s.copy', color='#606266'))
        copy_preview_btn.setIconSize(ICON_SIZE_SMALL)
        copy_preview_btn.setProperty("class", "ToolbarButton")
        copy_preview_btn.clicked.connect(lambda: self.copy_text_area(self.ui_preview_area))
        preview_action_row.addWidget(copy_preview_btn)

        preview_action_row.addStretch()

        clear_preview_btn = QPushButton(" 清空预览")
        clear_preview_btn.setIcon(qta.icon('fa5s.eraser', color='#909399'))
        clear_preview_btn.setIconSize(ICON_SIZE_SMALL)
        clear_preview_btn.setProperty("class", "ToolbarButton")
        clear_preview_btn.clicked.connect(self.clear_preview_only)
        preview_action_row.addWidget(clear_preview_btn)

        right_layout.addLayout(preview_action_row)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #e0e0e0; margin: 8px 0;")
        right_layout.addWidget(line)

        # ===== 2. 结果区 =====
        result_header = QHBoxLayout()
        result_label = QLabel("✅ 最终结果 (叠加后)")
        result_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #303133;")
        result_header.addWidget(result_label)
        result_header.addStretch()
        right_layout.addLayout(result_header)

        self.ui_final_result = QTextEdit()
        self.ui_final_result.setProperty("class", "ResultTextEdit")
        self.ui_final_result.setReadOnly(True)
        self.ui_final_result.setPlaceholderText("点击「应用叠加」后，结果会叠加到这里...")
        self.ui_final_result.setMinimumHeight(130)
        right_layout.addWidget(self.ui_final_result, stretch=1)

        # 结果操作行（复制左对齐，清空右对齐）
        result_action_row = QHBoxLayout()
        result_action_row.setSpacing(12)

        self.copy_final_btn = QPushButton(" 复制成品")
        self.copy_final_btn.setIcon(qta.icon('fa5s.copy', color='#409eff'))
        self.copy_final_btn.setIconSize(ICON_SIZE_MEDIUM)
        self.copy_final_btn.setMinimumHeight(36)
        self.copy_final_btn.setMinimumWidth(100)
        self.copy_final_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #409eff;
                border-radius: 18px;
                color: #409eff;
                font-weight: bold;
                font-size: 13px;
                padding: 4px 14px;
            }
            QPushButton:hover {
                background-color: #ecf5ff;
                border-color: #66b1ff;
                color: #66b1ff;
            }
            QPushButton:pressed {
                background-color: #d9ecff;
            }
        """)
        self.copy_final_btn.clicked.connect(lambda: self.copy_text_area(self.ui_final_result))
        result_action_row.addWidget(self.copy_final_btn)

        result_action_row.addStretch()

        clear_result_btn = QPushButton(" 清空结果")
        clear_result_btn.setIcon(qta.icon('fa5s.eraser', color='#909399'))
        clear_result_btn.setIconSize(ICON_SIZE_SMALL)
        clear_result_btn.setMinimumHeight(34)
        clear_result_btn.setMinimumWidth(80)
        clear_result_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f7fa;
                border: 1px solid #dcdfe6;
                border-radius: 17px;
                color: #909399;
                font-size: 13px;
                padding: 2px 12px;
            }
            QPushButton:hover {
                background-color: #ecf5ff;
                border-color: #409eff;
                color: #409eff;
            }
            QPushButton:pressed {
                background-color: #d9ecff;
            }
        """)
        clear_result_btn.clicked.connect(self.clear_output_only)
        result_action_row.addWidget(clear_result_btn)

        right_layout.addLayout(result_action_row)

        content_layout.addWidget(right_widget, 2)

        main_layout.addWidget(content_widget, stretch=1)

        return tab

    def create_excel_edit_tab(self):
        if self.activation_manager.is_activated() and self._excel_cache is not None:
            return self._excel_cache
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 10, 0, 0)
        from ui.excel_edit_dialog import ExcelEditDialog
        # ✅ 这里补上 theme_manager 参数
        excel_widget = ExcelEditDialog(self, is_pro=self.activation_manager.is_activated())
        excel_widget.setWindowFlags(Qt.Widget)
        excel_widget.setParent(tab)
        layout.addWidget(excel_widget)
        self.excel_widget = excel_widget
        if self.activation_manager.is_activated():
            self._excel_cache = tab
        return tab

    def create_word_tab(self):
        if self.activation_manager.is_activated() and self._word_cache is not None:
            return self._word_cache
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        from ui.word_edit_dialog import WordEditDialog
        word_widget = WordEditDialog(
            self,
            is_pro=self.activation_manager.is_activated(),
            theme_manager=self.theme_manager,
            config_manager=self.config_manager,
            main_window=self
        )
        word_widget.setWindowFlags(Qt.Widget)
        word_widget.setParent(tab)
        layout.addWidget(word_widget)
        self.word_widget = word_widget
        if self.activation_manager.is_activated():
            self._word_cache = tab
        return tab

    def create_tools_tab(self):
        if self.activation_manager.is_activated() and self._toolbox_cache is not None:
            return self._toolbox_cache
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        toolbox_widget = ToolBoxWidget(self)
        layout.addWidget(toolbox_widget)
        self.toolbox_widget = toolbox_widget
        if self.activation_manager.is_activated():
            self._toolbox_cache = tab
        return tab

    def _lazy_load_excel_tab(self):
        if self._excel_widget_created:
            return
        widget = self.create_excel_edit_tab()
        self._replace_placeholder(1, widget)
        self._excel_widget_created = True

    def _lazy_load_word_tab(self):
        if self._word_widget_created:
            return
        widget = self.create_word_tab()
        self._replace_placeholder(2, widget)
        self._word_widget_created = True

    def _lazy_load_toolbox_tab(self):
        if self._toolbox_widget_created:
            return
        widget = self.create_tools_tab()
        self._replace_placeholder(3, widget)
        self._toolbox_widget_created = True

    def _replace_placeholder(self, idx, new_widget):
        self.tab_widget.currentChanged.disconnect(self._on_tab_changed)
        try:
            old_widget = self.tab_widget.widget(idx)
            if old_widget is new_widget:
                return
            tab_text = self.tab_widget.tabText(idx)
            tab_icon = self.tab_widget.tabIcon(idx)
            self.tab_widget.removeTab(idx)
            if old_widget:
                old_widget.deleteLater()
            self.tab_widget.insertTab(idx, new_widget, tab_text)
            self.tab_widget.setTabIcon(idx, tab_icon)
            self.tab_widget.setCurrentIndex(idx)
        finally:
            self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _replace_tab_content(self, idx, creator):
        self.tab_widget.currentChanged.disconnect(self._on_tab_changed)
        try:
            tab_text = self.tab_widget.tabText(idx)
            tab_icon = self.tab_widget.tabIcon(idx)
            old_widget = self.tab_widget.widget(idx)
            if old_widget:
                self.tab_widget.removeTab(idx)
                old_widget.deleteLater()
            new_widget = creator()
            if new_widget is None:
                return
            self.tab_widget.insertTab(idx, new_widget, tab_icon, tab_text)
            self.tab_widget.setCurrentIndex(idx)
        finally:
            self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _find_tab_index(self, tab_text):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == tab_text:
                return i
        return -1

    def _load_excel_tab(self):
        if self._excel_tab_loaded:
            return
        idx = self._find_tab_index("  表格编辑")
        if idx == -1:
            return
        widget = self.create_excel_edit_tab()
        old_widget = self.tab_widget.widget(idx)
        if old_widget is widget:
            self._excel_tab_loaded = True
            return
        self.tab_widget.removeTab(idx)
        self.tab_widget.insertTab(idx, widget, "  表格编辑")
        self.tab_widget.setTabIcon(idx, qta.icon('fa5s.table', color='#409eff'))
        self._excel_tab_loaded = True
        if self.activation_manager.is_activated() and hasattr(self, 'excel_widget') and self.excel_widget:
            self.excel_widget.is_pro = True

    def _load_word_tab(self):
        if self._word_tab_loaded:
            return
        idx = self._find_tab_index("  文本处理")
        if idx == -1:
            return
        widget = self.create_word_tab()
        old_widget = self.tab_widget.widget(idx)
        if old_widget is widget:
            self._word_tab_loaded = True
            return
        self.tab_widget.removeTab(idx)
        self.tab_widget.insertTab(idx, widget, "  文本处理")
        self.tab_widget.setTabIcon(idx, qta.icon('fa5s.file-word', color='#409eff'))
        self._word_tab_loaded = True
        if self.activation_manager.is_activated() and hasattr(self, 'word_widget') and self.word_widget:
            self.word_widget.is_pro = True

    def _load_toolbox_tab(self):
        if self._toolbox_tab_loaded:
            return
        idx = self._find_tab_index("  工具箱")
        if idx == -1:
            return
        widget = self.create_tools_tab()
        old_widget = self.tab_widget.widget(idx)
        if old_widget is widget:
            self._toolbox_tab_loaded = True
            return
        self.tab_widget.removeTab(idx)
        self.tab_widget.insertTab(idx, widget, "  工具箱")
        self.tab_widget.setTabIcon(idx, qta.icon('fa5s.toolbox', color='#409eff'))
        self._toolbox_tab_loaded = True
        if self.activation_manager.is_activated() and hasattr(self, 'toolbox_widget') and self.toolbox_widget:
            self.toolbox_widget.is_pro = True

    def _on_tab_changed(self, index):
        """标签页切换处理（懒加载 + 新手引导）"""
        if index == 1 and not self._excel_widget_created:
            self._lazy_load_excel_tab()
        elif index == 2 and not self._word_widget_created:
            self._lazy_load_word_tab()
        elif index == 3 and not self._toolbox_widget_created:
            self._lazy_load_toolbox_tab()
        QTimer.singleShot(500, lambda: self.guide_manager.show_guide_for_tab(index))

    def check_and_show_guide(self):
        """检查并显示新手引导（启动时调用）"""
        self._guide_initialized = True

    def init_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Return"), self, self.apply_overlay)
        QShortcut(QKeySequence("Ctrl+L"), self, self.clear_input_only)

    def refresh_symbol_button_labels(self):
        mapping = {
            "double_quote": ("\" \"", "\" \""),
            "single_quote": ("' '", "' '"),
            "book_title": ("《》", "<<>>"),
            "comma": ("，", ","),
            "period": ("。", "."),
            "colon": ("：", ":"),
            "semicolon": ("；", ";"),
            "bracket_paren": ("()", "()"),
            "bracket_square": ("[]", "[]"),
            "bracket_curly": ("{}", "{}"),
            "bracket_corner": ("【】", "[]"),
            "enum_comma": ("、", ","),
            "percent": ("%", "%"),
            "sqrt": ("√", "√"),
            "at": ("@", "@"),
            "hash": ("#", "#"),
            "ellipsis": ("…", "..."),
            "middle_dot": ("·", "·"),
        }
        lang = self.text_processor.language
        for key, btn in self.symbol_buttons.items():
            if key in mapping:
                zh_text, en_text = mapping[key]
                text = en_text if lang == "en" else zh_text
                btn.setText(text.replace("&", "&&"))

    def update_symbol_buttons(self):
        self._load_configs_lazy()
        pass

    def toggle_symbol_language(self):
        new_lang = "en" if self.text_processor.language == "zh" else "zh"
        self.text_processor.set_language(new_lang)
        self.symbol_lang_btn.setText(" 中文符号" if new_lang == "zh" else " 英文符号")
        self.refresh_symbol_button_labels()
        if self.symbol_panel is not None:
            self.symbol_panel.refresh_symbol_grid()
        if hasattr(self, 'excel_widget') and self.excel_widget is not None:
            self.excel_widget.set_language(new_lang)
        if hasattr(self, 'word_widget') and self.word_widget is not None:
            self.word_widget.set_language(new_lang)

    def init_system_tray(self):
        if self.tray_icon is not None:
            return
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self)
        import os
        from pathlib import Path
        
        # 兼容打包后的环境
        if getattr(sys, 'frozen', False):
            # 打包后的环境：从exe所在目录获取
            app_dir = Path(os.path.dirname(sys.executable))
        else:
            # 开发环境
            app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 优先使用ICO文件（支持多尺寸），其次使用PNG
        icon_path = app_dir / "小雨办公工具.ico"
        if not icon_path.exists():
            icon_path = app_dir / "小雨办公工具.png"
        
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#409eff"))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(8, 8, 48, 48)
            painter.setPen(QColor("white"))
            font = QFont("Arial", 24, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "雨")
            painter.end()
            self.tray_icon.setIcon(QIcon(pixmap))
        tray_menu = QMenu(self)
        show_action = QAction("显示主窗口", self)
        show_action.setIcon(qta.icon('fa5s.eye', color='#606266'))
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)
        hide_action = QAction("最小化到托盘", self)
        hide_action.setIcon(qta.icon('fa5s.window-minimize', color='#606266'))
        hide_action.triggered.connect(self.hide_to_tray)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        screenshot_menu = tray_menu.addMenu("截图")
        screenshot_menu.setIcon(qta.icon('fa5s.camera', color='#606266'))
        fullscreen_screenshot = QAction("全屏截图", self)
        fullscreen_screenshot.setIcon(qta.icon('fa5s.expand', color='#606266'))
        fullscreen_screenshot.triggered.connect(lambda: self.trigger_screenshot(mode='full'))
        screenshot_menu.addAction(fullscreen_screenshot)
        region_screenshot = QAction("区域截图", self)
        region_screenshot.setIcon(qta.icon('fa5s.crop', color='#606266'))
        region_screenshot.triggered.connect(lambda: self.trigger_screenshot(mode='region'))
        screenshot_menu.addAction(region_screenshot)
        window_screenshot = QAction("当前窗口", self)
        window_screenshot.setIcon(qta.icon('fa5s.window-restore', color='#606266'))
        window_screenshot.triggered.connect(lambda: self.trigger_screenshot(mode='window'))
        screenshot_menu.addAction(window_screenshot)
        symbol_action = QAction("📝 符号与公式助手", self)
        symbol_action.setIcon(qta.icon('fa5s.hashtag', color='#606266'))
        symbol_action.triggered.connect(self.show_symbol_panel)
        symbol_action.setEnabled(self.activation_manager.is_activated())
        tray_menu.addAction(symbol_action)
        tray_menu.addSeparator()
        quit_action = QAction("退出", self)
        quit_action.setIcon(qta.icon('fa5s.sign-out-alt', color='#606266'))
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.setToolTip("小雨办公工具")
        self.tray_icon.show()

    def update_dark_mode_action_icon(self):
        pass

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide_to_tray()
            else:
                self.show_window()
        elif reason == QSystemTrayIcon.Trigger:
            if not self.isVisible():
                self.show_window()

    def show_window(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def hide_to_tray(self):
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage("小雨办公工具", "程序已最小化到托盘", QSystemTrayIcon.Information, 2000)

    def closeEvent(self, event):
        if hasattr(self, 'symbol_panel') and self.symbol_panel is not None:
            self.symbol_panel.close()
        if self.tray_icon and self.tray_icon.isVisible():
            tray_behavior = self.config_manager.get_config("UI", "tray_behavior", "点击关闭：最小化到托盘")
            if tray_behavior == "点击关闭：退出程序":
                event.accept()
            elif tray_behavior == "点击关闭：最小化到托盘":
                self.hide_to_tray()
                event.ignore()
            else:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("退出软件")
                msg_box.setText("是否要退出软件")
                yes_btn = msg_box.addButton("是", QMessageBox.YesRole)
                no_btn = msg_box.addButton("否", QMessageBox.NoRole)
                close_btn = msg_box.addButton("关闭", QMessageBox.RejectRole)
                msg_box.setDefaultButton(close_btn)
                msg_box.setEscapeButton(close_btn)
                msg_box.setStyleSheet(self.theme_manager.generate_stylesheet())
                msg_box.exec()
                clicked = msg_box.clickedButton()
                if clicked == yes_btn:
                    event.accept()
                elif clicked == no_btn:
                    self.hide_to_tray()
                    event.ignore()
                else:
                    event.ignore()
        else:
            event.accept()

    def quit_application(self):
        QApplication.quit()

    def show_symbol_panel(self):
        if not self.activation_manager.is_activated():
            self.show_warning("免费版限制", "符号与公式助手为 PRO 版专属功能，请升级后使用。")
            return
        if self.symbol_panel is None:
            from ui.symbol_panel import SymbolPanel
            self.symbol_panel = SymbolPanel(self)
        else:
            self.symbol_panel.load_custom_formulas()
            self.symbol_panel.load_disabled_default_formulas()
            self.symbol_panel.refresh_symbol_grid()
            self.symbol_panel.refresh_formula_list()
        cursor_pos = QCursor.pos()
        x = cursor_pos.x() - self.symbol_panel.width() // 2
        y = cursor_pos.y() - self.symbol_panel.height() - 10
        self.symbol_panel.move(x, y)
        self.symbol_panel.show()
        self.symbol_panel.raise_()
        self.symbol_panel.activateWindow()

    def set_now_sym(self, sym_id):
        self.now_sym = sym_id
        self.refresh_sym_btn()
        self.refresh_main_preview()

    def set_now_pos(self, pos_key):
        self.now_pos = pos_key
        self.refresh_pos_btn()
        self.refresh_main_preview()

    def _show_activation_success_animation(self):
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve, QTimer
        import random
        overlay = QWidget(self)
        overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        overlay.setAttribute(Qt.WA_TranslucentBackground)
        overlay.setGeometry(self.geometry())
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.6);")
        overlay.show()
        center_widget = QWidget(overlay)
        center_widget.setGeometry(overlay.rect())
        layout = QVBoxLayout(center_widget)
        layout.setAlignment(Qt.AlignCenter)
        icon_label = QLabel()
        icon_label.setPixmap(qta.icon('fa5s.gem', color='#FFD700').pixmap(100, 100))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        success_label = QLabel("激活成功！")
        success_label.setStyleSheet("color: #FFD700; font-size: 28px; font-weight: bold;")
        success_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(success_label)
        subtitle_label = QLabel("感谢您升级到 Pro 版")
        subtitle_label.setStyleSheet("color: white; font-size: 16px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        particles = []
        for _ in range(30):
            particle = QLabel(overlay)
            particle.setFixedSize(6, 6)
            particle.setStyleSheet("background-color: #FFD700; border-radius: 3px;")
            particle.move(random.randint(0, overlay.width()), random.randint(0, overlay.height()))
            particle.show()
            particles.append(particle)
        scale_anim = QPropertyAnimation(icon_label, b"geometry")
        scale_anim.setDuration(800)
        start_rect = icon_label.geometry()
        icon_label.resize(50, 50)
        icon_label.move((overlay.width() - 50) // 2, (overlay.height() - 50) // 2 - 50)
        scale_anim.setStartValue(icon_label.geometry())
        scale_anim.setEndValue(start_rect)
        scale_anim.setEasingCurve(QEasingCurve.OutElastic)
        opacity_effect = QGraphicsOpacityEffect(center_widget)
        center_widget.setGraphicsEffect(opacity_effect)
        fade_anim = QPropertyAnimation(opacity_effect, b"opacity")
        fade_anim.setDuration(1200)
        fade_anim.setStartValue(0.0)
        fade_anim.setKeyValueAt(0.2, 1.0)
        fade_anim.setEndValue(0.0)
        fade_anim.setEasingCurve(QEasingCurve.InOutQuad)
        for p in particles:
            anim = QPropertyAnimation(p, b"geometry")
            anim.setDuration(1000)
            start = p.geometry()
            dx = random.randint(-200, 200)
            dy = random.randint(-200, 200)
            end = start.translated(dx, dy)
            anim.setStartValue(start)
            anim.setEndValue(end)
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
        scale_anim.start()
        fade_anim.start()
        QTimer.singleShot(1500, overlay.close)

    def trigger_screenshot(self, mode='full'):
        if not hasattr(self, 'toolbox_widget'):
            self.toolbox_widget = ToolBoxWidget(self)
        self._main_was_visible = self.isVisible()
        self._screenshot_mode = mode
        if self.isVisible():
            self.hide()
        QTimer.singleShot(500, self._do_open_screenshot)

    def _do_open_screenshot(self):
        self.toolbox_widget._main_window_hidden = True
        self.toolbox_widget.open_screenshot(mode=getattr(self, '_screenshot_mode', 'full'))
        if not self.toolbox_widget.isVisible():
            self.toolbox_widget.show()

    # ========== 设置对话框 ==========
    def show_settings(self):
        from ui.settings_dialog import SettingsDialog
        dlg = SettingsDialog(self, self)
        dlg.exec()

    def _reset_guide_and_close_settings(self, dialog):
        current_tab = self.tab_widget.currentIndex()
        self.guide_manager.reset_guide(current_tab)
        dialog.accept()
        QTimer.singleShot(200, lambda: self.guide_manager.show_guide_for_tab(current_tab))

    def save_settings_and_close(self, dialog):
        try:
            self.fail_notify_enabled = self.fail_notify_check.isChecked()
            self.split_mode = self.split_combo.currentIndex()
            self.config_manager.set_config("App", "fail_notify", str(self.fail_notify_enabled).lower())
            self.config_manager.set_config("App", "split_mode", str(self.split_mode))
            dialog.accept()
            self.show_toast("设置已保存")
            def do_post_updates():
                self._setup_auto_backup()
                self._setup_reminder()
            QTimer.singleShot(100, do_post_updates)
        except Exception as e:
            self.show_error("错误", f"保存失败：{str(e)}")

    def load_recent_files(self):
        try:
            recent_str = self.config_manager.get_config("App", "recent_files", "[]")
            self.recent_files = json.loads(recent_str)
        except:
            self.recent_files = []

    def save_recent_files(self):
        try:
            self.config_manager.set_config("App", "recent_files", json.dumps(self.recent_files))
        except:
            pass

    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
        self.save_recent_files()
        self.update_recent_menu()

    def update_recent_menu(self):
        self.recent_menu.clear()
        if self.recent_files:
            for fp in self.recent_files[:10]:
                if os.path.exists(fp):
                    action = QAction(os.path.basename(fp), self)
                    action.setData(fp)
                    action.triggered.connect(lambda checked, path=fp: self.open_excel_edit_window(path))
                    self.recent_menu.addAction(action)
            self.recent_menu.addSeparator()
            self.recent_menu.addAction("清空历史", self.clear_recent_history)
        else:
            self.recent_menu.addAction("暂无最近文件").setEnabled(False)

    def clear_recent_history(self):
        self.recent_files.clear()
        self.save_recent_files()
        self.update_recent_menu()
        self.show_info("提示", "最近文件历史已清空")

    def open_excel_edit_window(self, file_path):
        self.tab_widget.setCurrentIndex(1)
        if hasattr(self, 'excel_widget') and self.excel_widget is not None:
            self.excel_widget.open_file_direct(file_path)
        else:
            QTimer.singleShot(500, lambda: self._open_excel_file_delayed(file_path))

    def _open_excel_file_delayed(self, file_path):
        if hasattr(self, 'excel_widget') and self.excel_widget is not None:
            self.excel_widget.open_file_direct(file_path)
        else:
            self.show_warning("提示", "Excel 组件尚未加载，请稍后重试。")

    def load_settings(self):
        self.auto_remove_blank_lines = self.config_manager.get_config("Experience", "auto_remove_blank_lines", "false") == "true"
        self.auto_remove_extra_spaces = self.config_manager.get_config("Experience", "auto_remove_extra_spaces", "false") == "true"
        self.auto_remove_all_whitespace = self.config_manager.get_config("Experience", "auto_remove_all_whitespace", "false") == "true"
        self.skip_empty_cells = self.config_manager.get_config("Experience", "skip_empty_cells", "false") == "true"
        self.auto_save_history_enabled = self.config_manager.get_config("App", "auto_save_history", "false") == "true"
        self.history_count = int(self.config_manager.get_config("App", "history_count", "10"))
        self.fail_notify_enabled = self.config_manager.get_config("App", "fail_notify", "true") == "true"
        self.split_mode = int(self.config_manager.get_config("App", "split_mode", "0"))

    def show_activation_dialog(self):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame, QWidget, QScrollArea, QMessageBox, QGraphicsDropShadowEffect
        from PySide6.QtCore import Qt, QPoint

        theme = self.theme_manager.get_theme()
        primary = theme["primary"]
        pro_text = theme.get("pro_text", "#D4AF37")
        card = theme["card"]
        text = theme["text"]
        text_secondary = theme["text_secondary"]
        border = theme["border"]

        class TransparentDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setAttribute(Qt.WA_OpaquePaintEvent, False)
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                bg_color = QColor(255, 255, 255)
                painter.setBrush(bg_color)
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(self.rect(), 16, 16)
                painter.setBrush(Qt.NoBrush)
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 15, 15)

        dialog = TransparentDialog(self)
        dialog.setWindowTitle("升级到 Pro 版")
        dialog.setFixedSize(560, 640)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 100))
        title_bar = QFrame(dialog)
        title_bar.setFixedHeight(56)
        title_bar.setStyleSheet("QFrame { background-color: transparent; border-top-left-radius: 16px; border-top-right-radius: 16px; }")
        title_bar.setCursor(Qt.SizeAllCursor)
        title_bar.setGraphicsEffect(shadow)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(20, 0, 20, 0)
        price_title = QLabel("¥19.9 永久畅享")
        price_title.setAlignment(Qt.AlignCenter)
        price_title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {primary}; background: transparent;")
        title_layout.addWidget(price_title, 1)
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; border-radius: 16px; font-size: 20px; font-weight: bold; color: #EF4444; }
            QPushButton:hover { background: #FEE2E2; color: #DC2626; }
        """)
        close_btn.clicked.connect(dialog.reject)
        title_layout.addWidget(close_btn)

        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{ background-color: {card}; border-radius: 16px; border: 1px solid {border}; }}
            QPushButton#copyBtn {{ background-color: {card}; border: 1px solid {border}; border-radius: 6px; padding: 6px 12px; color: {text_secondary}; font-size: 12px; }}
            QPushButton#copyBtn:hover {{ background-color: {primary}20; border-color: {primary}; color: {primary}; }}
            QPushButton#activateBtn {{ background-color: {primary}; color: white; border: none; border-radius: 8px; padding: 10px 24px; font-weight: bold; font-size: 14px; }}
            QPushButton#activateBtn:hover {{ background-color: {theme['primary_dark']}; }}
            QLineEdit {{ border: 1px solid {border}; border-radius: 8px; padding: 10px; font-size: 13px; background-color: {card}; color: {text}; }}
            QLineEdit:focus {{ border-color: {primary}; }}
            QFrame#freeFrame {{ background-color: {card}; border: 1px solid {border}; border-radius: 12px; padding: 20px; }}
            QFrame#proFrame {{ background-color: {card}; border: 2px solid {primary}; border-radius: 12px; padding: 20px; }}
            QFrame#proTopLine {{ background-color: {primary}; height: 2px; border-radius: 1px; margin: -20px -20px 12px -20px; }}
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 0, 20, 20)
        main_layout.setSpacing(20)
        desc_label = QLabel("解锁全部高阶功能")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(f"color: {text_secondary}; font-size: 14px; background: transparent; margin-bottom: 8px;")
        main_layout.addWidget(desc_label)

        compare_layout = QHBoxLayout()
        compare_layout.setSpacing(20)
        free_frame = QFrame()
        free_frame.setObjectName("freeFrame")
        free_layout = QVBoxLayout(free_frame)
        free_layout.setSpacing(12)
        free_title = QLabel("免费基础版")
        free_title.setStyleSheet(f"font-weight: bold; color: {text}; font-size: 16px;")
        free_title.setAlignment(Qt.AlignCenter)
        free_layout.addWidget(free_title)
        for item in ["✓ 基础编辑", "✓ 常用符号", "✓ 简易模板", "✓ 快捷工具"]:
            lbl = QLabel(item)
            lbl.setStyleSheet(f"color: {text_secondary}; font-size: 13px; padding: 4px 0;")
            free_layout.addWidget(lbl)
        free_layout.addStretch()
        compare_layout.addWidget(free_frame, 1)

        pro_frame = QFrame()
        pro_frame.setObjectName("proFrame")
        pro_layout = QVBoxLayout(pro_frame)
        pro_layout.setSpacing(12)
        pro_top_line = QFrame()
        pro_top_line.setObjectName("proTopLine")
        pro_layout.addWidget(pro_top_line)
        pro_title = QLabel("💎 Pro 尊享版")
        pro_title.setStyleSheet(f"font-weight: bold; color: {primary}; font-size: 16px;")
        pro_title.setAlignment(Qt.AlignCenter)
        pro_layout.addWidget(pro_title)
        for item in ["✓ 全功能开放", "✓ 无水印导出", "✓ 后台文档编辑", "✓ 个性化主题"]:
            lbl = QLabel(item)
            lbl.setStyleSheet(f"color: {text_secondary}; font-size: 13px; padding: 4px 0;")
            pro_layout.addWidget(lbl)
        pro_layout.addStretch()
        compare_layout.addWidget(pro_frame, 1)

        main_layout.addLayout(compare_layout)

        machine_code = self.activation_manager.get_machine_code()
        machine_widget = QWidget()
        machine_row = QHBoxLayout(machine_widget)
        machine_row.setContentsMargins(0, 0, 0, 0)
        machine_row.setSpacing(12)
        machine_label = QLabel("设备编码：")
        machine_label.setStyleSheet(f"font-weight: bold; color: {text}; font-size: 13px;")
        machine_row.addWidget(machine_label)
        code_label = QLabel(machine_code)
        code_label.setStyleSheet("font-family: monospace; font-size: 13px; background-color: white; padding: 6px 10px; border-radius: 6px; color: #303133;")
        code_label.setWordWrap(True)
        machine_row.addWidget(code_label, 1)
        copy_btn = QPushButton("复制")
        copy_btn.setObjectName("copyBtn")
        copy_btn.setCursor(Qt.PointingHandCursor)
        def copy_machine_code():
            if not machine_code:
                QMessageBox.warning(dialog, "提示", "设备编码为空，无法复制")
                return
            clipboard = QApplication.clipboard()
            clipboard.setText(machine_code)
            if clipboard.text() == machine_code:
                self.show_toast("设备编码已复制")
            else:
                QMessageBox.warning(dialog, "复制失败", "请手动选择并复制")
        copy_btn.clicked.connect(copy_machine_code)
        machine_row.addWidget(copy_btn)
        main_layout.addWidget(machine_widget)

        if not self.activation_manager.is_activated():
            code_input_widget = QWidget()
            code_input_row = QHBoxLayout(code_input_widget)
            code_input_row.setContentsMargins(0, 0, 0, 0)
            code_input_row.setSpacing(12)
            key_label = QLabel("激活密钥：")
            key_label.setStyleSheet(f"font-weight: bold; color: {text}; font-size: 13px;")
            code_input_row.addWidget(key_label)
            self.activation_code_edit = QLineEdit()
            self.activation_code_edit.setPlaceholderText("XXXX-XXXX-XXXX-XXXX")
            code_input_row.addWidget(self.activation_code_edit, 1)
            activate_btn = QPushButton("立即激活")
            activate_btn.setObjectName("activateBtn")
            activate_btn.setCursor(Qt.PointingHandCursor)
            activate_btn.clicked.connect(lambda: self.activate_pro_version_with_code(dialog, self.activation_code_edit))
            code_input_row.addWidget(activate_btn)
            main_layout.addWidget(code_input_widget)
            purchase_label = QLabel("💰 购买请联系客服")
            purchase_label.setAlignment(Qt.AlignCenter)
            purchase_label.setStyleSheet(f"color: {primary}; font-size: 18px; font-weight: bold; background: transparent; margin-top: 20px; margin-bottom: 8px;")
            main_layout.addWidget(purchase_label)
            contact_label = QLabel("📞 微信 fangbaby2233 | QQ 2818491757")
            contact_label.setAlignment(Qt.AlignCenter)
            contact_label.setStyleSheet(f"color: {text_secondary}; font-size: 15px; font-weight: 600; background: transparent; margin-bottom: 16px;")
            main_layout.addWidget(contact_label)
        else:
            activated_label = QLabel("✅ 您已是Pro版用户")
            activated_label.setAlignment(Qt.AlignCenter)
            activated_label.setStyleSheet(f"color: {primary}; font-size: 16px; font-weight: bold; margin: 16px 0;")
            main_layout.addWidget(activated_label)

        scroll.setWidget(container)
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.addWidget(title_bar)
        dialog_layout.addWidget(scroll)

        drag_pos = None
        def mouse_press_event(event):
            nonlocal drag_pos
            if event.button() == Qt.LeftButton:
                drag_pos = event.globalPosition().toPoint() - dialog.frameGeometry().topLeft()
                event.accept()
        def mouse_move_event(event):
            nonlocal drag_pos
            if drag_pos and event.buttons() == Qt.LeftButton:
                dialog.move(event.globalPosition().toPoint() - drag_pos)
                event.accept()
        def mouse_release_event(event):
            nonlocal drag_pos
            drag_pos = None
            event.accept()
        title_bar.mousePressEvent = mouse_press_event
        title_bar.mouseMoveEvent = mouse_move_event
        title_bar.mouseReleaseEvent = mouse_release_event

        screen_geo = QApplication.primaryScreen().availableGeometry()
        dialog.move((screen_geo.width() - dialog.width()) // 2, (screen_geo.height() - dialog.height()) // 2)
        dialog.exec()

    def _copy_simple_code(self, text):
        from PySide6.QtWidgets import QMessageBox
        try:
            from PySide6.QtGui import QGuiApplication
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(None, "复制成功", f"设备编码已复制到剪贴板：\n{text}")
        except Exception as e:
            QMessageBox.warning(None, "复制失败", f"无法复制，请手动复制：\n{text}")
    
    def _copy_to_clipboard(self, text):
        if not text:
            self.show_toast("没有可复制的内容")
            return
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            if clipboard.text() == text:
                self.show_toast("✅ 已复制到剪贴板")
            else:
                from PySide6.QtGui import QGuiApplication
                QGuiApplication.clipboard().setText(text)
                self.show_toast("✅ 已复制到剪贴板")
        except Exception as e:
            print(f"复制失败: {e}")
            self.show_toast(f"复制失败: {str(e)}")
            return
        try:
            if (hasattr(self, 'toolbox_widget') and self.toolbox_widget is not None and
                hasattr(self.toolbox_widget, '_on_clipboard_change')):
                QTimer.singleShot(100, self.toolbox_widget._on_clipboard_change)
        except Exception:
            pass

    def activate_pro_version_with_code(self, dialog, code_edit):
        code = code_edit.text().strip()
        if not code:
            self.show_warning("提示", "请输入激活码！")
            return
        is_success, license_type, error_msg = self.activation_manager.activate(code)
        if is_success:
            dialog.close()
            self.show_info("激活成功", "恭喜您，已成功激活 Pro 版！")
            self._post_activation_refresh()
        else:
            self.show_warning("激活失败", error_msg or "激活码无效，请检查后重试")

    def _post_activation_refresh(self):
        self.update_activation_status()
        self.apply_theme()
        self.update_tab_permissions()
        self._excel_cache = None
        self._word_cache = None
        self._toolbox_cache = None
        if hasattr(self, 'excel_widget') and self.excel_widget:
            self.excel_widget.is_pro = True
            self.excel_widget.enable_pro_features()
        if hasattr(self, 'word_widget') and self.word_widget:
            self.word_widget.is_pro = True
            self.word_widget.enable_pro_features()
        if hasattr(self, 'toolbox_widget') and self.toolbox_widget:
            self.toolbox_widget.refresh_activation_status()
        current_idx = self.tab_widget.currentIndex()
        if current_idx in [1, 2, 3]:
            self._on_tab_changed(current_idx)

    def update_activation_status(self):
        if self.activation_manager.is_activated():
            self.license_label.setText("⭐ Pro版")
            self.license_label.setStyleSheet("color: #67c23a; font-weight: bold;")
        else:
            self.license_label.setText("🔒 免费版")
            self.license_label.setStyleSheet("color: #909399;")
        self.update_tab_permissions()

    def update_tab_permissions(self):
        is_pro = self.activation_manager.is_activated()
        for idx in [1, 2, 3]:
            self.tab_widget.setTabEnabled(idx, True)
            if not is_pro:
                self.tab_widget.setTabText(idx, "🔒 " + self.tab_widget.tabText(idx).replace("🔒 ", ""))
            else:
                self.tab_widget.setTabText(idx, self.tab_widget.tabText(idx).replace("🔒 ", ""))

    def get_license_text(self):
        return "⭐ Pro版" if self.activation_manager.is_activated() else "🔒 免费版"

    def refresh_main_preview(self):
        """实时预览当前选择符号和位置应用到原始文本的效果（不修改最终结果）
        预览显示在右侧的预览区中，不影响叠加结果。
        """
        if self.now_sym and self.now_pos and self.origin_text:
            symbol = self.get_symbol_info(self.now_sym) or self.now_sym
            preview = self.apply_symbol_whole(self.origin_text, symbol, self.now_pos)
            self.ui_preview_area.setPlainText(preview)
        else:
            self.ui_preview_area.clear()

    def apply_symbol_whole(self, text, symbol, position):
        pure = text.strip()
        if not pure:
            return text
        if isinstance(symbol, str) and symbol.startswith("custom_") and hasattr(self, 'custom_map'):
            actual = self.custom_map.get(symbol)
            if actual:
                if len(actual) == 2:
                    left, right = actual[0], actual[1]
                else:
                    left = right = actual
            else:
                left = right = symbol
        elif isinstance(symbol, tuple) and len(symbol) >= 2:
            left, right = symbol[0], symbol[1]
        elif isinstance(symbol, str):
            if len(symbol) >= 2:
                left, right = symbol[0], symbol[1]
            else:
                left = right = symbol
        else:
            left = right = str(symbol) if symbol else ""

        if position == "head":
            return left + pure
        elif position == "tail":
            return pure + right
        elif position == "both":
            return left + pure + right
        elif position == "split":
            chars = list(pure)
            if self.split_mode == 0:
                return left.join(chars)
            elif self.split_mode == 1:
                # 每个字符被 left + right 包裹，无分隔符
                return "".join([f"{left}{c}{right}" for c in chars])
            elif self.split_mode == 2:
                # 每个字符被 left + right 包裹，逗号分隔
                return ",".join([f"{left}{c}{right}" for c in chars])
        return pure

    def apply_symbol(self, symbol):
        if not self.input_text.toPlainText().strip():
            self.show_toast("请先输入文本")
            return
        self.now_sym = symbol
        self.refresh_sym_btn()
        self.refresh_main_preview()

    def on_symbol_click(self, sym_key, btn):
        self.apply_symbol(sym_key)
        self.refresh_main_preview()

    def set_position(self, position):
        self.now_pos = position
        self.refresh_pos_btn()
        self.refresh_main_preview()  
        for pos, btn in self.position_buttons.items():
            btn.setChecked(pos == position)
        self.current_position = position
        self.show_toast(f"已选择：{self.get_position_name(position)}")
        self.update_char_count()

    def refresh_sym_btn(self):
        theme = self.theme_manager.get_theme()
        primary = theme["primary"]
        for symbol, btn in self.symbol_buttons.items():
            if symbol == self.now_sym:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {primary};
                        border: 2px solid {primary};
                        border-radius: 10px;
                        color: white;
                        min-width: 100px;
                        max-width: 100px;
                        min-height: 44px;
                        max-height: 44px;
                        font-size: 15px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {theme["primary_light"]};
                        border-color: {theme["primary_light"]};
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 2px solid #dcdfe6;
                        border-radius: 10px;
                        color: #303133;
                        font-size: 15px;
                        font-weight: 500;
                        min-width: 100px;
                        max-width: 100px;
                        min-height: 44px;
                        max-height: 44px;
                    }
                    QPushButton:hover {
                        border-color: #409eff;
                        background-color: #ecf5ff;
                        color: #409eff;
                    }
                    QPushButton:pressed {
                        background-color: #d9ecff;
                    }
                """)

    def refresh_pos_btn(self):
        theme = self.theme_manager.get_theme()
        primary = theme["primary"]
        for pos, btn in self.position_buttons.items():
            if pos == self.now_pos:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {primary};
                        border: 2px solid {primary};
                        border-radius: 10px;
                        color: white;
                        min-width: 80px;
                        min-height: 40px;
                        font-size: 14px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        background-color: {theme["primary_light"]};
                        border-color: {theme["primary_light"]};
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffffff;
                        border: 2px solid #dcdfe6;
                        border-radius: 10px;
                        color: #303133;
                        min-width: 80px;
                        min-height: 40px;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        border-color: #409eff;
                        background-color: #ecf5ff;
                        color: #409eff;
                    }
                    QPushButton:pressed {
                        background-color: #d9ecff;
                    }
                """)

    def get_symbol_info(self, symbol):
        if hasattr(self, 'custom_map') and symbol in self.custom_map:
            custom_sym = self.custom_map.get(symbol)
            if custom_sym:
                if len(custom_sym) == 2:
                    return (custom_sym[0], custom_sym[1])
                elif len(custom_sym) == 1:
                    return (custom_sym, custom_sym)
        if self.text_processor.language == "en":
            mapping = {
                "double_quote": ('"', '"'),
                "single_quote": ("'", "'"),
                "book_title": ("<<", ">>"),
                "comma": (",", ","),
                "period": (".", "."),
                "colon": (":", ":"),
                "semicolon": (";", ";"),
                "bracket_paren": ("(", ")"),
                "bracket_square": ("[", "]"),
                "bracket_curly": ("{", "}"),
                "bracket_corner": ("[", "]"),
                "enum_comma": (",", ","),
                "percent": ("%", "%"),
                "sqrt": ("√", "√"),
                "at": ("@", "@"),
                "hash": ("#", "#"),
                "ellipsis": ("...", "..."),
                "middle_dot": ("·", "·"),
                "question": ("?", "?"),
                "exclamation": ("!", "!"),
                "plus": ("+", "+"),
                "minus": ("-", "-"),
            }
        else:
            mapping = {
                "double_quote": ('"', '"'),
                "single_quote": ("'", "'"),
                "book_title": ("《", "》"),
                "comma": ("，", "，"),
                "period": ("。", "。"),
                "colon": ("：", "："),
                "semicolon": ("；", "；"),
                "bracket_paren": ("（", "）"),
                "bracket_square": ("[", "]"),
                "bracket_curly": ("{", "}"),
                "bracket_corner": ("【", "】"),
                "enum_comma": ("、", "、"),
                "percent": ("%", "%"),
                "sqrt": ("√", "√"),
                "at": ("@", "@"),
                "hash": ("#", "#"),
                "ellipsis": ("…", "…"),
                "middle_dot": ("·", "·"),
                "question": ("？", "？"),
                "exclamation": ("！", "！"),
                "plus": ("+", "+"),
                "minus": ("-", "-"),
            }
        if isinstance(symbol, str) and symbol in mapping:
            return mapping[symbol]
        return symbol

    def get_symbol_config(self):
        custom_defaults = self.config_manager.get_config("Symbols", "custom_defaults", "{}")
        try:
            custom_defaults_data = json.loads(custom_defaults)
        except:
            custom_defaults_data = {}
        if self.text_processor.language == "en":
            default_config = {
                "double_quote": ("\"", "\"", "\"\"", "双引号"),
                "single_quote": ("'", "'", "''", "单引号"),
                "book_title": ("<<", ">>", "<<>>", "书名号"),
                "comma": (",", ",", ",", "逗号"),
                "period": (".", ".", ".", "句号"),
                "colon": (":", ":", ":", "冒号"),
                "semicolon": (";", ";", ";", "分号"),
                "bracket_paren": ("(", ")", "()", "圆括号"),
                "bracket_square": ("[", "]", "[]", "方括号"),
                "bracket_curly": ("{", "}", "{}", "花括号"),
                "bracket_corner": ("[", "]", "[]", "角括号"),
                "enum_comma": (",", ",", ",", "顿号"),
                "percent": ("%", "%", "%", "百分号"),
                "sqrt": ("√", "√", "√", "根号"),
                "at": ("@", "@", "@", "艾特"),
                "hash": ("#", "#", "#", "井号"),
                "ellipsis": ("...", "...", "...", "省略号"),
                "middle_dot": ("·", "·", "·", "间隔号"),
                "question": ("?", "?", "?", "问号"),
                "exclamation": ("!", "!", "!", "感叹号"),
                "plus": ("+", "+", "+", "加号"),
                "minus": ("-", "-", "-", "减号"),
            }
        else:
            default_config = {
                "double_quote": ("\"", "\"", "\"\"", "双引号"),
                "single_quote": ("'", "'", "''", "单引号"),
                "book_title": ("《", "》", "《》", "书名号"),
                "comma": ("，", "，", "，", "逗号"),
                "period": ("。", "。", "。", "句号"),
                "colon": ("：", "：", "：", "冒号"),
                "semicolon": ("；", "；", "；", "分号"),
                "bracket_paren": ("（", "）", "（）", "圆括号"),
                "bracket_square": ("【", "】", "【】", "方括号"),
                "bracket_curly": ("｛", "｝", "｛｝", "花括号"),
                "bracket_corner": ("【", "】", "【】", "角括号"),
                "enum_comma": ("、", "、", "、", "顿号"),
                "percent": ("%", "%", "%", "百分号"),
                "sqrt": ("√", "√", "√", "根号"),
                "at": ("@", "@", "@", "艾特"),
                "hash": ("#", "#", "#", "井号"),
                "ellipsis": ("…", "…", "…", "省略号"),
                "middle_dot": ("·", "·", "·", "间隔号"),
                "question": ("？", "？", "？", "问号"),
                "exclamation": ("！", "！", "！", "感叹号"),
                "plus": ("+", "+", "+", "加号"),
                "minus": ("-", "-", "-", "减号"),
            }
        for key, modification in custom_defaults_data.items():
            if key in default_config:
                orig_left, orig_right, orig_display, orig_name = default_config[key]
                new_value = modification.get("value", orig_display)
                new_name = modification.get("name", orig_name)
                if len(new_value) == 2:
                    new_left, new_right = new_value[0], new_value[1]
                else:
                    new_left = new_right = new_value
                default_config[key] = (new_left, new_right, new_value, new_name)
        for key, sym in self.custom_map.items():
            if len(sym) == 2:
                left, right = sym[0], sym[1]
            else:
                left = right = sym
            default_config[key] = (left, right, sym, key)
        
        enabled_config = {}
        for key, value in default_config.items():
            if key not in self.disabled_default_symbols:
                enabled_config[key] = value
        return enabled_config

    def get_position_name(self, pos):
        names = {"head": "头部", "tail": "尾部", "both": "两端", "split": "分隔"}
        return names.get(pos, pos)

    def toggle_width(self):
        self.full_width = not self.full_width
        self.width_btn.setText("全角" if self.full_width else "半角")

    def clear_output_only(self):
        self.ui_final_result.clear()
        self.show_toast("已清空结果")

    def clear_preview_only(self):
        self.ui_preview_area.clear()
        self.show_toast("已清空预览")

    def _process_input_text(self, text):
        result = text
        if self.auto_remove_all_whitespace:
            import re
            result = re.sub(r'\s+', '', result)
        else:
            if self.auto_remove_blank_lines:
                lines = result.split('\n')
                result = '\n'.join(line for line in lines if line.strip())
            if self.auto_remove_extra_spaces:
                import re
                result = re.sub(r' ', '', result)
        return result

    def on_input_text_changed(self):
        self.origin_text = self.input_text.toPlainText()
        self.build_text = self.origin_text
        self.overlay_chain = []
        self.now_sym = None
        self.now_pos = None
        self.refresh_sym_btn()
        self.refresh_pos_btn()
        self.update_char_count()
        self.refresh_main_preview()
        self.ui_final_result.setPlainText(self.build_text)
    
    def _do_text_transform(self):
        raw_txt = self.input_text.toPlainText()
        processed_txt = self._process_input_text(raw_txt)
        self.input_text.blockSignals(True)
        self.input_text.setPlainText(processed_txt)
        self.input_text.blockSignals(False)
        self.origin_text = processed_txt
        self.build_text = processed_txt
        self.ui_preview_area.clear()
        self.ui_final_result.setPlainText(self.build_text)
        self.overlay_chain = []
        self.now_sym = None
        self.now_pos = None
        self.refresh_sym_btn()
        self.refresh_pos_btn()
        self.update_char_count()
        self.show_toast("转换完成")

    def clear_input_only(self):
        self.input_text.blockSignals(True)
        self.input_text.clear()
        self.input_text.blockSignals(False)
        self.origin_text = ""
        self.build_text = ""
        self.ui_final_result.clear()
        self.ui_preview_area.clear()
        self.overlay_chain = []
        self.now_sym = None
        self.now_pos = None
        self.refresh_sym_btn()
        self.refresh_pos_btn()
        self.update_char_count()
        self.show_toast("已清空输入")

    def clear_input(self):
        self.clear_input_only()

    def apply_overlay(self):
        if not self.now_sym or not self.now_pos or not self.build_text:
            self.show_toast("请先输入文本并选择符号和位置")
            return
        # 当前符号叠加后结果
        symbol = self.get_symbol_info(self.now_sym) or self.now_sym
        new_build = self.apply_symbol_whole(self.build_text, symbol, self.now_pos)
        
        # 真正叠加：更新 build_text 和叠加链
        self.overlay_chain.append({"symbol": self.now_sym, "position": self.now_pos})
        self.build_text = new_build
        self.ui_final_result.setPlainText(self.build_text)
        # 自动将焦点移至结果框并选中全部文本
        self.ui_final_result.setFocus()
        self.ui_final_result.selectAll()
        self.update_char_count()
        self._add_symbol_to_history(self.now_sym, self.now_pos)
        
        # 在状态栏显示叠加历史
        overlay_summary = " → ".join([
            f"{self.get_symbol_display_name(item['symbol'])}-{self.get_position_display_name(item['position'])}"
            for item in self.overlay_chain
        ])
        self.status_label.setText(f"已叠加: {overlay_summary}")
        
        self.show_toast("已应用叠加")

    def _add_symbol_to_history(self, symbol, position):
        history_item = {"symbol": symbol, "position": position}
        for i, item in enumerate(self.symbol_history):
            if item["symbol"] == symbol and item["position"] == position:
                self.symbol_history.pop(i)
                break
        self.symbol_history.insert(0, history_item)
        if len(self.symbol_history) > self.max_symbol_history:
            self.symbol_history.pop()
        self._refresh_symbol_history_ui()

    def _refresh_symbol_history_ui(self):
        if not hasattr(self, 'history_buttons') or not self.history_buttons:
            return
        for btn in self.history_buttons:
            btn.setVisible(False)
        for i, item in enumerate(self.symbol_history):
            if i < len(self.history_buttons):
                btn = self.history_buttons[i]
                sym_name = self.get_symbol_display_name(item["symbol"])
                pos_name = self.get_position_display_name(item["position"])
                btn.setText(f"⏪ {sym_name} ({pos_name})")
                btn.setVisible(True)
                try:
                    btn.clicked.disconnect()
                except (TypeError, RuntimeError):
                    pass
                btn.clicked.connect(
                    lambda checked, s=item["symbol"], p=item["position"]:
                    self._apply_from_history(s, p)
                )

    def _apply_from_history(self, symbol, position):
        self.now_sym = symbol
        self.now_pos = position
        self.refresh_sym_btn()
        self.refresh_pos_btn()
        self.refresh_main_preview()
        self.show_toast(f"已选择历史记录：{self.get_symbol_display_name(symbol)} ({self.get_position_display_name(position)})")

    def copy_text_area(self, text_edit):
        text = text_edit.toPlainText()
        if not text:
            self.show_toast("内容为空，无法复制")
            return
        QApplication.clipboard().setText(text)
        if hasattr(self, 'toolbox_widget') and hasattr(self.toolbox_widget, '_on_clipboard_change'):
            QTimer.singleShot(100, self.toolbox_widget._on_clipboard_change)
        self.show_toast("已复制到剪贴板")

    def show_toast(self, message):
        toast = QLabel(message, self)
        toast.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        toast.setStyleSheet("QLabel { background-color: rgba(0, 0, 0, 0.85); color: white; padding: 10px 20px; border-radius: 8px; font-size: 14px; }")
        toast.show()
        geo = self.screen().geometry()
        toast.move((geo.width() - toast.sizeHint().width()) // 2, (geo.height() - toast.sizeHint().height()) // 2)
        QTimer.singleShot(2000, toast.close)

    def update_char_count(self):
        count = len(self.input_text.toPlainText())
        self.char_count_label.setText(f"字符数: {count}/1000")
        if count > 1000:
            self.status_label.setText("⚠️ 超过1000字符限制")
            self.status_label.setStyleSheet("color: #f56c6c;")
        else:
            self.status_label.setText("就绪")
            self.status_label.setStyleSheet("")

    def get_symbol_display_name(self, key):
        cfg = self.get_symbol_config()
        if key in cfg:
            return cfg[key][3]
        names = {
            "bracket_paren": "圆括号", "bracket_square": "方括号", "bracket_curly": "花括号",
            "bracket_corner": "角括号", "quote_corner": "角引号", "comma": "逗号",
            "period": "句号", "enum_comma": "顿号", "colon": "冒号", "semicolon": "分号",
            "plus": "加号", "minus": "减号", "asterisk": "乘号", "slash": "除号",
            "equal": "等号", "greater": "大于", "less": "小于", "greater_equal": "大于等于",
            "less_equal": "小于等于", "percent": "百分号", "sqrt": "根号", "pi": "圆周率",
            "at": "艾特", "hash": "井号", "emdash": "破折号", "ellipsis": "省略号",
            "middle_dot": "间隔号", "double_quote": "双引号", "single_quote": "单引号",
            "book_title": "书名号", "question": "问号", "exclamation": "感叹号"
        }
        if key.startswith("custom_"):
            return "自定义"
        return names.get(key, key)

    def get_position_display_name(self, pos):
        names = {"head": "头部", "tail": "尾部", "both": "两端", "split": "分隔"}
        return names.get(pos, pos)

    def show_filter_dialog(self):
        from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
        theme = self.theme_manager.get_theme()
        card = theme["card"]
        text = theme["text"]
        border = theme["border"]
        primary = theme["primary"]
        primary_light = theme.get("primary_light", primary)
        dialog = QDialog(self)
        dialog.setWindowTitle("筛选符号")
        dialog.setFixedSize(450, 260)
        screen_geo = QApplication.primaryScreen().availableGeometry()
        x = (screen_geo.width() - dialog.width()) // 2
        y = (screen_geo.height() - dialog.height()) // 2
        dialog.move(x, y)
        dialog.setStyleSheet(f"""
            QDialog {{
                background-color: rgba(255, 255, 255, 0.96);
                border-radius: 16px;
            }}
            QLabel {{
                color: {text};
                font-size: 14px;
            }}
            QLineEdit {{
                border: 1px solid {border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: {card};
                color: {text};
            }}
            QLineEdit:focus {{
                border-color: {primary};
            }}
            QTextEdit {{
                border: 1px solid {border};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: {card};
                color: {text};
            }}
            QTextEdit:focus {{
                border-color: {primary};
            }}
            QComboBox {{
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 14px;
                background-color: {card};
                color: {text};
            }}
            QComboBox:focus {{
                border-color: {primary};
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton#applyBtn {{
                background-color: {primary};
                color: white;
            }}
            QPushButton#applyBtn:hover {{
                background-color: {primary_light};
            }}
            QPushButton#clearBtn {{
                background-color: {border};
                color: {text};
            }}
            QPushButton#clearBtn:hover {{
                background-color: {primary_light};
                color: white;
            }}
            QPushButton#cancelBtn {{
                background-color: {border};
                color: {text};
            }}
            QPushButton#cancelBtn:hover {{
                background-color: {primary_light};
                color: white;
            }}
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # 筛选区域选择
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("筛选区域："))
        self.filter_target_combo = QComboBox()
        self.filter_target_combo.addItems(["预览区", "成品区"])
        target_layout.addWidget(self.filter_target_combo)
        target_layout.addStretch()
        layout.addLayout(target_layout)
        
        layout.addWidget(QLabel("输入要移除的符号（空格分隔）："))
        self.filter_edit = QTextEdit()
        self.filter_edit.setPlaceholderText("例如: ★ ● ◆ (多个符号用空格分隔)")
        self.filter_edit.setMaximumHeight(80)
        self.filter_edit.setPlainText(self.config_manager.get_config("Filter", "symbols", ""))
        layout.addWidget(self.filter_edit)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        apply_btn = QPushButton("应用")
        apply_btn.setObjectName("applyBtn")
        apply_btn.clicked.connect(lambda: self.apply_filter_action(dialog))
        clear_btn = QPushButton("清除")
        clear_btn.setObjectName("clearBtn")
        clear_btn.clicked.connect(lambda: self.clear_filter_action(dialog))
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.clicked.connect(dialog.close)
        btn_layout.addWidget(apply_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        dialog.exec()

    def apply_filter_action(self, dialog):
        symbols = self.filter_edit.toPlainText().strip()
        target = self.filter_target_combo.currentText()
        self.config_manager.set_config("Filter", "symbols", symbols)
        
        # 筛选不参与叠加链，只保存当前文本状态用于恢复
        if target == "预览区":
            # 保存筛选前的预览区状态
            current_state = {
                'target': 'preview',
                'text': self.ui_preview_area.toPlainText()
            }
            self.filter_history.append(current_state)
            # 执行筛选
            result = current_state['text']
            for s in symbols.split():
                if s:
                    result = result.replace(s, "")
            self.ui_preview_area.setPlainText(result)
            self.show_toast("预览区筛选已应用")
        else:  # 成品区
            # 保存筛选前的成品区状态
            current_state = {
                'target': 'final',
                'text': self.ui_final_result.toPlainText(),
                'build_text': self.build_text
            }
            self.filter_history.append(current_state)
            # 执行筛选
            result = current_state['text']
            for s in symbols.split():
                if s:
                    result = result.replace(s, "")
            self.ui_final_result.setPlainText(result)
            # 更新 build_text 但保留叠加链
            self.build_text = result
            self.show_toast("成品区筛选已应用")
        
        # 只保留最近10条历史记录
        if len(self.filter_history) > 10:
            self.filter_history.pop(0)
        
        dialog.close()

    def clear_filter_action(self, dialog):
        self.filter_edit.clear()
        self.config_manager.set_config("Filter", "symbols", "")
        
        # 恢复到最后一次筛选前的状态
        if self.filter_history:
            last_state = self.filter_history.pop()
            if last_state.get('target') == 'preview':
                self.ui_preview_area.setPlainText(last_state['text'])
            else:
                self.ui_final_result.setPlainText(last_state['text'])
                self.build_text = last_state.get('build_text', self.ui_final_result.toPlainText())
            self.show_toast("已恢复到筛选前的状态")
        else:
            self.show_toast("没有可恢复的筛选历史")
        
        dialog.close()
    
    def _refresh_symbols_after_delete(self):
        self.render_symbol_buttons()
        if hasattr(self, 'symbol_panel') and self.symbol_panel:
            self.symbol_panel.refresh_symbol_grid()
