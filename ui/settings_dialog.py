# ui/settings_dialog.py
import os
import json
import subprocess
import platform
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QWidget, QFrame, QLabel, QPushButton,
    QCheckBox, QComboBox, QLineEdit, QScrollArea, QStackedWidget, QListWidget,
    QListWidgetItem, QMessageBox, QFileDialog, QSpinBox, QSizePolicy, QTextEdit,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView, QToolButton,
    QGraphicsDropShadowEffect, QFontComboBox, QMenu,
)
from PySide6.QtCore import Qt, QTimer, QSize, QPoint, QUrl
from PySide6.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush, QDesktopServices, QAction, QWheelEvent,
)
import qtawesome as qta
from ui.symbol_panel import SymbolPanel

APP_NAME = "小雨办公工具"
VERSION = "1.0"


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event: QWheelEvent):
        event.ignore()


class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelFontComboBox(QFontComboBox):
    def wheelEvent(self, event):
        event.ignore()


class SettingsDialog(QDialog):
    DEFAULT_SYMBOL_NAMES = {
        "double_quote": {"name": "双引号", "zh": "“”", "en": '""'},
        "single_quote": {"name": "单引号", "zh": "‘’", "en": "''"},
        "book_title": {"name": "书名号", "zh": "《》", "en": "<>"},
        "comma": {"name": "逗号", "zh": "，", "en": ","},
        "period": {"name": "句号", "zh": "。", "en": "."},
        "colon": {"name": "冒号", "zh": "：", "en": ":"},
        "semicolon": {"name": "分号", "zh": "；", "en": ";"},
        "bracket_paren": {"name": "小括号", "zh": "（）", "en": "()"},
        "bracket_square": {"name": "中括号", "zh": "【】", "en": "[]"},
        "bracket_curly": {"name": "大括号", "zh": "｛｝", "en": "{}"},
        "bracket_corner": {"name": "角括号", "zh": "「」", "en": "<>"},
        "enum_comma": {"name": "顿号", "zh": "、", "en": ","},
        "percent": {"name": "百分号", "zh": "%", "en": "%"},
        "sqrt": {"name": "根号", "zh": "√", "en": "√"},
        "at": {"name": "艾特", "zh": "@", "en": "@"},
        "hash": {"name": "井号", "zh": "#", "en": "#"},
        "ellipsis": {"name": "省略号", "zh": "……", "en": "..."},
        "middle_dot": {"name": "间隔号", "zh": "·", "en": "·"},
        "question": {"name": "问号", "zh": "？", "en": "?"},
        "exclamation": {"name": "感叹号", "zh": "！", "en": "!"},
        "plus": {"name": "加号", "zh": "+", "en": "+"},
        "minus": {"name": "减号", "zh": "-", "en": "-"},
    }

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.theme_manager = main_window.theme_manager
        self.activation_manager = main_window.activation_manager
        self.custom_map = dict(main_window.custom_map)
        self.disabled_default_symbols = list(main_window.disabled_default_symbols)
        
        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # 设置窗口图标
        from pathlib import Path
        from PySide6.QtGui import QIcon
        app_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = app_dir / "小雨办公工具.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        self._original_custom_map = dict(main_window.custom_map)
        self._original_disabled_symbols = list(main_window.disabled_default_symbols)

        custom_formulas_str = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
        self._custom_formulas = [tuple(f.split("|")) for f in custom_formulas_str.split(";;") if f] if custom_formulas_str else []
        self._original_custom_formulas = list(self._custom_formulas)

        disabled_str = self.config_manager.get_config("SymbolPanel", "disabled_default_formulas", "[]")
        try:
            self.disabled_default_formulas = json.loads(disabled_str)
        except:
            self.disabled_default_formulas = []
        if not isinstance(self.disabled_default_formulas, list):
            self.disabled_default_formulas = []
        self._original_disabled_formulas = list(self.disabled_default_formulas)

        self.auto_remove_blank_lines = self.config_manager.get_config("Experience", "auto_remove_blank_lines", "false") == "true"
        self.auto_remove_extra_spaces = self.config_manager.get_config("Experience", "auto_remove_extra_spaces", "false") == "true"
        self.auto_remove_all_whitespace = self.config_manager.get_config("Experience", "auto_remove_all_whitespace", "false") == "true"
        self.skip_empty_cells = self.config_manager.get_config("Experience", "skip_empty_cells", "false") == "true"
        self.split_mode = main_window.split_mode

        self.drag_pos = None

        self.init_ui()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()

    def reject(self):
        self.custom_map = dict(self._original_custom_map)
        self.disabled_default_symbols = list(self._original_disabled_symbols)
        self.disabled_default_formulas = list(self._original_disabled_formulas)
        self._custom_formulas = list(self._original_custom_formulas)
        super().reject()

    def _open_config_folder(self):
        config_path = self.config_manager.data_dir
        if not config_path:
            self._show_themed_message_box("错误", "配置目录未初始化", QMessageBox.Critical)
            return
        try:
            os.makedirs(config_path, exist_ok=True)
            self._open_folder_safely(config_path)
        except Exception as e:
            self._show_themed_message_box("错误", f"打开配置文件夹失败：{str(e)}", QMessageBox.Critical)

    def _open_log_folder(self):
        if not self.config_manager.data_dir:
            self._show_themed_message_box("错误", "配置目录未初始化", QMessageBox.Critical)
            return
        log_path = os.path.join(os.path.dirname(self.config_manager.data_dir), "logs")
        try:
            os.makedirs(log_path, exist_ok=True)
            self._open_folder_safely(log_path)
        except Exception as e:
            self._show_themed_message_box("错误", f"打开日志文件夹失败：{str(e)}", QMessageBox.Critical)

    def _open_folder_safely(self, path):
        if not os.path.exists(path):
            self._show_themed_message_box("路径错误", f"文件夹不存在：{path}", QMessageBox.Warning)
            return
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            self._show_themed_message_box("打开失败", f"无法打开文件夹：{str(e)}", QMessageBox.Critical)

    def _show_themed_message_box(self, title, text, icon=QMessageBox.Warning):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet(self.main_window.theme_manager.generate_stylesheet())
        return msg_box.exec()

    def _show_question(self, title, text, yes_text="是", no_text="否"):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Question)
        yes_btn = msg_box.addButton(yes_text, QMessageBox.YesRole)
        no_btn = msg_box.addButton(no_text, QMessageBox.NoRole)
        msg_box.setDefaultButton(no_btn)
        msg_box.setEscapeButton(no_btn)
        msg_box.setStyleSheet(self.main_window.theme_manager.generate_stylesheet())
        msg_box.exec()
        clicked = msg_box.clickedButton()
        if clicked == yes_btn:
            return True
        return False

    def _refresh_backup_list(self):
        if not hasattr(self, "backup_list"):
            return
        self.backup_list.clear()
        backup_dir = self.backup_location_edit.text().strip()
        if not os.path.exists(backup_dir):
            return
        backups = []
        for f in os.listdir(backup_dir):
            if f.endswith(".ini"):
                full_path = os.path.join(backup_dir, f)
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
                backups.append((mtime, f, full_path, size))
        backups.sort(reverse=True)
        from datetime import datetime
        for mtime, fname, fpath, fsize in backups[:20]:
            dt = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
            size_str = f"{fsize/1024:.1f}KB" if fsize < 1024*1024 else f"{fsize/1024/1024:.1f}MB"
            self.backup_list.addItem(f"{dt} | {size_str} | {fname}")

    def _show_backup_context_menu(self, pos):
        item = self.backup_list.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        delete_action = QAction("删除此备份", self)
        delete_action.triggered.connect(lambda: self._delete_single_backup(item))
        menu.addAction(delete_action)
        menu.exec_(self.backup_list.mapToGlobal(pos))

    def _delete_single_backup(self, item):
        text = item.text()
        fname = text.split("|")[-1].strip()
        backup_dir = self.backup_location_edit.text().strip()
        backup_path = os.path.join(backup_dir, fname)
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
                self._refresh_backup_list()
                self.main_window.show_toast("已删除备份")
            except Exception as e:
                self._show_themed_message_box("错误", f"删除失败：{str(e)}", QMessageBox.Critical)
        else:
            self._show_themed_message_box("错误", f"文件不存在：{backup_path}", QMessageBox.Critical)

    def init_ui(self):
        self.resize(900, 700)
        theme = self.theme_manager.get_theme()
        bg = theme["bg"]
        card_bg = theme["card"]
        text = theme["text"]
        text_secondary = theme["text_secondary"]
        border = theme["border"]
        primary = theme["primary"]
        primary_light = theme.get("primary_light", primary)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg};
                border-radius: 16px;
            }}
            QListWidget[class="sidebar"] {{ 
                background-color: {card_bg}; 
                border: 1px solid {border}; 
                border-radius: 12px; 
                padding: 8px;
                outline: none;
            }}
            QListWidget[class="sidebar"]::item {{ 
                padding: 12px 16px; 
                border-radius: 8px; 
                color: {text_secondary};
                font-size: 14px;
                margin: 2px 0;
            }}
            QListWidget[class="sidebar"]::item:selected {{ 
                background-color: {primary}; 
                color: white; 
                font-weight: 600;
            }}
            QListWidget[class="sidebar"]::item:hover:!selected {{ 
                background-color: {primary_light}; 
                color: {primary};
            }}
            QListWidget {{ 
                background-color: {card_bg}; 
                border: 1px solid {border}; 
                border-radius: 8px; 
                padding: 4px;
                outline: none;
            }}
            QListWidget::item {{ 
                padding: 8px 12px; 
                border-radius: 6px; 
                color: {text};
                font-size: 13px;
                margin: 1px 0;
            }}
            QListWidget::item:selected {{ 
                background-color: {primary}; 
                color: white; 
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{ 
                background-color: {primary_light}; 
            }}
            QScrollArea {{ background: transparent; border: none; }}
            QFrame#card {{ 
                background-color: {card_bg}; 
                border: 1px solid {border}; 
                border-radius: 12px; 
                margin: 0px 0px 20px 0px; 
                background-image: none;
            }}
            QFrame#card > QWidget, QFrame#card > QLayout > QWidget {{ 
                background-color: {card_bg}; 
                background-image: none;
            }}
            QLabel#card_title {{ 
                font-size: 18px; 
                font-weight: 700; 
                color: {text}; 
                padding: 16px 20px 4px 20px; 
            }}
            QLabel#setting_title {{ 
                font-size: 15px; 
                font-weight: 600; 
                color: {text}; 
            }}
            QLabel#setting_desc {{ 
                font-size: 12px; 
                color: {text_secondary}; 
                padding: 4px 0 8px 0;
            }}
            QCheckBox {{ 
                spacing: 8px;
                color: {text};
                font-size: 14px;
                background-color: transparent;
            }}
            QComboBox, QLineEdit {{ 
                border: 1px solid {border}; 
                border-radius: 8px; 
                padding: 8px 12px; 
                background-color: {card_bg}; 
                color: {text}; 
                font-size: 14px;
                min-height: 20px;
            }}
            QComboBox:hover, QLineEdit:hover {{ border-color: {primary}; }}
            QComboBox:focus, QLineEdit:focus {{ border-color: {primary}; }}
            QPushButton {{ 
                background-color: {card_bg}; 
                border: 1px solid {border}; 
                border-radius: 8px; 
                padding: 8px 16px; 
                color: {text}; 
                font-size: 14px;
            }}
            QPushButton:hover {{ 
                background-color: {primary_light}; 
                border-color: {primary}; 
                color: {primary}; 
            }}
            QPushButton#primaryBtn {{ 
                background-color: {primary}; 
                color: white; 
                border: none; 
                padding: 10px 24px; 
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton#primaryBtn:hover {{ 
                background-color: {primary_light}; 
            }}
            QPushButton#saveBtn {{ 
                background-color: {primary}; 
                color: white; 
                border: none; 
                padding: 10px 28px; 
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton#saveBtn:hover {{ 
                background-color: {primary_light}; 
            }}
            QPushButton#softDeleteBtn {{ 
                background-color: {card_bg}; 
                color: {primary}; 
                border: 1px solid {border}; 
                border-radius: 8px; 
                padding: 8px 16px; 
                font-size: 14px;
            }}
            QPushButton#softDeleteBtn:hover {{ 
                background-color: #fef0f0; 
                border-color: #f56c6c; 
                color: #f56c6c;
            }}
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        stacked = QStackedWidget()
        stacked.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # ---------- 通用设置页面 ----------
        general_page = QWidget()
        general_layout = QVBoxLayout(general_page)
        general_layout.setContentsMargins(0, 0, 0, 0)
        general_layout.setSpacing(0)
        scroll_general = QScrollArea()
        scroll_general.setWidgetResizable(True)
        scroll_general.setFrameShape(QFrame.NoFrame)
        scroll_general.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        general_content = QWidget()
        general_content_layout = QVBoxLayout(general_content)
        general_content_layout.setContentsMargins(0, 0, 0, 20)
        general_content_layout.setSpacing(0)

        # 卡片：体验优化
        card_opt = QFrame()
        card_opt.setObjectName("card")
        opt_layout = QVBoxLayout(card_opt)
        opt_layout.setSpacing(12)
        opt_title = QLabel("体验优化")
        opt_title.setObjectName("card_title")
        opt_layout.addWidget(opt_title)
        
        self.auto_remove_blank_lines_check = QCheckBox("去除空白行")
        self.auto_remove_blank_lines_check.setChecked(self.auto_remove_blank_lines)
        opt_layout.addWidget(self.auto_remove_blank_lines_check)
        opt_layout.addWidget(QLabel("  移除文本中的空行"))
        
        self.auto_remove_extra_spaces_check = QCheckBox("去除多余空格")
        self.auto_remove_extra_spaces_check.setChecked(self.auto_remove_extra_spaces)
        opt_layout.addWidget(self.auto_remove_extra_spaces_check)
        opt_layout.addWidget(QLabel("  将多个连续空格合并为一个"))
        
        self.auto_remove_all_whitespace_check = QCheckBox("去除所有空白")
        self.auto_remove_all_whitespace_check.setChecked(self.auto_remove_all_whitespace)
        opt_layout.addWidget(self.auto_remove_all_whitespace_check)
        opt_layout.addWidget(QLabel("  移除所有空格和换行，拼接为单行"))
        
        self.skip_empty_cells_check = QCheckBox("跳过空白单元格")
        self.skip_empty_cells_check.setChecked(self.skip_empty_cells)
        opt_layout.addWidget(self.skip_empty_cells_check)
        opt_layout.addWidget(QLabel("  Excel表格符号处理时跳过空白单元格，仅处理有内容的单元格"))
        general_content_layout.addWidget(card_opt)

        # 分隔格式设置
        card_split = QFrame()
        card_split.setObjectName("card")
        split_layout = QVBoxLayout(card_split)
        split_layout.setSpacing(12)
        split_title = QLabel("分隔格式设置")
        split_title.setObjectName("card_title")
        split_layout.addWidget(split_title)
        split_desc = QLabel("选择符号处理时的分隔模式")
        split_desc.setObjectName("setting_desc")
        split_layout.addWidget(split_desc)
        self.split_combo = NoWheelComboBox()
        self.split_combo.addItems(["普通分隔", "无间隔引号拼接", "逗号数组分隔"])
        self.split_combo.setCurrentIndex(self.split_mode)
        split_layout.addWidget(self.split_combo)
        general_content_layout.addWidget(card_split)

        # 文件设置
        card_file = QFrame()
        card_file.setObjectName("card")
        file_layout = QVBoxLayout(card_file)
        file_layout.setSpacing(12)
        file_title = QLabel("文件设置")
        file_title.setObjectName("card_title")
        file_layout.addWidget(file_title)
        path_layout = QHBoxLayout()
        path_label = QLabel("默认保存路径：")
        path_label.setMinimumWidth(120)
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.config_manager.get_config("File", "default_path", ""))
        path_btn = QPushButton(" 浏览")
        path_btn.setIcon(qta.icon("fa5s.folder-open", color=text))
        path_btn.clicked.connect(lambda: self.path_edit.setText(QFileDialog.getExistingDirectory(self, "选择默认保存路径") or self.path_edit.text()))
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(path_btn)
        file_layout.addLayout(path_layout)
        encoding_layout = QHBoxLayout()
        encoding_label = QLabel("默认文件编码：")
        encoding_label.setMinimumWidth(120)
        self.encoding_combo = NoWheelComboBox()
        self.encoding_combo.addItems(["UTF-8", "GBK", "GB18030", "UTF-16"])
        self.encoding_combo.setFocusPolicy(Qt.StrongFocus)
        self.encoding_combo.wheelEvent = lambda e: e.ignore()
        saved_encoding = self.config_manager.get_config("File", "default_encoding", "UTF-8")
        encoding_idx = self.encoding_combo.findText(saved_encoding)
        if encoding_idx >= 0:
            self.encoding_combo.setCurrentIndex(encoding_idx)
        encoding_layout.addWidget(encoding_label)
        encoding_layout.addWidget(self.encoding_combo)
        encoding_layout.addStretch()
        file_layout.addLayout(encoding_layout)
        general_content_layout.addWidget(card_file)

        scroll_general.setWidget(general_content)
        general_layout.addWidget(scroll_general)
        stacked.addWidget(general_page)

        # ---------- 界面设置页面 ----------
        ui_page = QWidget()
        ui_layout = QVBoxLayout(ui_page)
        ui_layout.setContentsMargins(0, 0, 0, 0)
        ui_layout.setSpacing(0)
        scroll_ui = QScrollArea()
        scroll_ui.setWidgetResizable(True)
        scroll_ui.setFrameShape(QFrame.NoFrame)
        scroll_ui.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        ui_content = QWidget()
        ui_content_layout = QVBoxLayout(ui_content)
        ui_content_layout.setContentsMargins(0, 0, 0, 20)
        ui_content_layout.setSpacing(16)
        theme_card = QFrame()
        theme_card.setObjectName("card")
        theme_card_layout = QVBoxLayout(theme_card)
        theme_card_layout.setSpacing(12)
        theme_title = QLabel("外观主题")
        theme_title.setObjectName("card_title")
        theme_card_layout.addWidget(theme_title)
        theme_desc = QLabel("选择软件外观风格")
        theme_desc.setObjectName("setting_desc")
        theme_card_layout.addWidget(theme_desc)
        self.theme_combo = NoWheelComboBox()
        is_activated = self.activation_manager.is_activated()
        for t_id, t_info in self.theme_manager.THEMES.items():
            is_pro = self.theme_manager.is_pro_theme(t_id)
            display_name = f"🔒 {t_info['name']}" if (is_pro and not is_activated) else t_info["name"]
            self.theme_combo.addItem(display_name, t_id)
            if is_pro and not is_activated:
                self.theme_combo.model().item(self.theme_combo.count()-1).setEnabled(False)
        current_idx = self.theme_combo.findData(self.theme_manager.current_theme)
        if current_idx >= 0 and self.theme_combo.model().item(current_idx).isEnabled():
            self.theme_combo.setCurrentIndex(current_idx)
        else:
            blue_idx = self.theme_combo.findData("blue")
            if blue_idx >= 0:
                self.theme_combo.setCurrentIndex(blue_idx)
        theme_card_layout.addWidget(self.theme_combo)
        ui_content_layout.addWidget(theme_card)

        default_page_card = QFrame()
        default_page_card.setObjectName("card")
        default_page_layout = QVBoxLayout(default_page_card)
        default_page_layout.setSpacing(12)
        default_page_title = QLabel("默认工具页")
        default_page_title.setObjectName("card_title")
        default_page_layout.addWidget(default_page_title)
        default_page_desc = QLabel("设置软件启动后默认打开的页面")
        default_page_desc.setObjectName("setting_desc")
        default_page_layout.addWidget(default_page_desc)
        self.default_page_combo = NoWheelComboBox()
        self.default_page_combo.addItems(["符号处理", "表格编辑", "文本处理", "工具箱", "符号与公式助手"])
        saved_default = self.config_manager.get_config("UI", "default_page", "符号处理")
        index = self.default_page_combo.findText(saved_default)
        if index >= 0:
            self.default_page_combo.setCurrentIndex(index)
        default_page_layout.addWidget(self.default_page_combo)
        self.default_page_combo.currentIndexChanged.connect(lambda idx: self.config_manager.set_config("UI", "default_page", self.default_page_combo.itemText(idx)))
        ui_content_layout.addWidget(default_page_card)

        display_card = QFrame()
        display_card.setObjectName("card")
        display_layout = QVBoxLayout(display_card)
        display_layout.setSpacing(12)
        display_title = QLabel("显示设置")
        display_title.setObjectName("card_title")
        display_layout.addWidget(display_title)
        display_desc = QLabel("调整软件界面显示效果")
        display_desc.setObjectName("setting_desc")
        display_layout.addWidget(display_desc)

        scale_row = QHBoxLayout()
        scale_label = QLabel("窗口缩放：")
        scale_label.setMinimumWidth(100)
        scale_row.addWidget(scale_label)
        self.scale_combo = NoWheelComboBox()
        self.scale_combo.addItems(["100%", "125%", "150%", "200%"])
        saved_scale = self.config_manager.get_config("UI", "scale_factor", "100")
        idx = self.scale_combo.findText(saved_scale + "%")
        if idx >= 0:
            self.scale_combo.setCurrentIndex(idx)
        else:
            idx = self.scale_combo.findText("100%")
            if idx >= 0:
                self.scale_combo.setCurrentIndex(idx)
        scale_row.addWidget(self.scale_combo)
        scale_row.addStretch()
        display_layout.addLayout(scale_row)

        font_row = QHBoxLayout()
        font_label = QLabel("界面字体：")
        font_label.setMinimumWidth(100)
        font_row.addWidget(font_label)
        self.font_combo = NoWheelFontComboBox()
        safe_fonts = ["Microsoft YaHei", "Segoe UI", "Arial", "SimSun", "Noto Sans CJK SC", "PingFang SC", "思源黑体", "黑体"]
        for font_name in safe_fonts:
            if self.font_combo.findText(font_name) >= 0:
                self.font_combo.setCurrentIndex(self.font_combo.findText(font_name))
                break
        saved_font = self.config_manager.get_config("UI", "font_family", "微软雅黑")
        font_idx = self.font_combo.findText(saved_font)
        if font_idx >= 0:
            self.font_combo.setCurrentIndex(font_idx)
        else:
            for i in range(self.font_combo.count()):
                if "雅黑" in self.font_combo.itemText(i) or "YaHei" in self.font_combo.itemText(i):
                    self.font_combo.setCurrentIndex(i)
                    break
        font_row.addWidget(self.font_combo)
        font_size_label = QLabel("字号：")
        font_size_label.setMinimumWidth(40)
        font_row.addWidget(font_size_label)
        self.font_size_spin = NoWheelSpinBox()
        self.font_size_spin.setRange(11, 20)
        self.font_size_spin.setValue(int(self.config_manager.get_config("UI", "font_size", "10")))
        self.font_size_spin.setMinimumWidth(80)          # 加宽
        self.font_size_spin.setMinimumHeight(30)         # 加高
        self.font_size_spin.setStyleSheet("font-size: 14px;")  # 内部文字放大
        font_row.addWidget(self.font_size_spin)
        font_row.addStretch()
        display_layout.addLayout(font_row)

        self.animation_check = QCheckBox("启用界面动画（选项卡切换、弹窗渐入）")
        self.animation_check.setChecked(self.config_manager.get_config("UI", "enable_animation", "true") == "true")
        display_layout.addWidget(self.animation_check)

        layout_mode_row = QHBoxLayout()
        layout_label = QLabel("布局模式：")
        layout_label.setMinimumWidth(100)
        layout_mode_row.addWidget(layout_label)
        self.layout_mode_combo = NoWheelComboBox()
        self.layout_mode_combo.addItems(["紧凑", "宽松"])
        saved_layout = self.config_manager.get_config("UI", "layout_mode", "紧凑")
        idx = self.layout_mode_combo.findText(saved_layout)
        if idx >= 0:
            self.layout_mode_combo.setCurrentIndex(idx)
        layout_mode_row.addWidget(self.layout_mode_combo)
        layout_mode_row.addStretch()
        display_layout.addLayout(layout_mode_row)

        self.tray_icon_check = QCheckBox("显示系统托盘图标")
        self.tray_icon_check.setChecked(self.config_manager.get_config("UI", "show_tray_icon", "true") == "true")
        display_layout.addWidget(self.tray_icon_check)

        tray_behavior_row = QHBoxLayout()
        tray_label = QLabel("托盘行为：")
        tray_label.setMinimumWidth(100)
        tray_behavior_row.addWidget(tray_label)
        self.tray_behavior_combo = NoWheelComboBox()
        self.tray_behavior_combo.addItems(["点击关闭：退出程序", "点击关闭：最小化到托盘", "点击关闭：询问"])
        saved_behavior = self.config_manager.get_config("UI", "tray_behavior", "点击关闭：最小化到托盘")
        idx = self.tray_behavior_combo.findText(saved_behavior)
        if idx >= 0:
            self.tray_behavior_combo.setCurrentIndex(idx)
        tray_behavior_row.addWidget(self.tray_behavior_combo)
        tray_behavior_row.addStretch()
        display_layout.addLayout(tray_behavior_row)

        ui_content_layout.addWidget(display_card)

        scroll_ui.setWidget(ui_content)
        ui_layout.addWidget(scroll_ui)
        stacked.addWidget(ui_page)

        # ---------- 符号设置页面 ----------
        symbol_page = QWidget()
        symbol_layout = QVBoxLayout(symbol_page)
        symbol_layout.setContentsMargins(0, 0, 0, 0)
        symbol_layout.setSpacing(0)
        scroll_symbol = QScrollArea()
        scroll_symbol.setWidgetResizable(True)
        scroll_symbol.setFrameShape(QFrame.NoFrame)
        symbol_content = QWidget()
        symbol_content_layout = QVBoxLayout(symbol_content)
        symbol_content_layout.setContentsMargins(0, 0, 0, 20)
        symbol_content_layout.setSpacing(16)

        card_symbol = QFrame()
        card_symbol.setObjectName("card")
        symbol_layout_inner = QVBoxLayout(card_symbol)
        symbol_layout_inner.setSpacing(12)
        symbol_title = QLabel("符号管理")
        symbol_title.setObjectName("card_title")
        symbol_layout_inner.addWidget(symbol_title)
        symbol_desc = QLabel("管理软件符号，支持默认符号和自定义符号")
        symbol_desc.setObjectName("setting_desc")
        symbol_layout_inner.addWidget(symbol_desc)

        search_layout = QHBoxLayout()
        self.search_edit_symbol = QLineEdit()
        self.search_edit_symbol.setPlaceholderText("搜索符号或符号名称...")
        search_layout.addWidget(self.search_edit_symbol)
        self.search_btn = QPushButton(" 搜索")
        self.search_btn.setIcon(qta.icon("fa5s.search", color=text))
        search_layout.addWidget(self.search_btn)
        symbol_layout_inner.addLayout(search_layout)

        # 替换为：
        self.symbol_list = QListWidget()
        self.symbol_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.symbol_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许横向纵向扩展
        self.symbol_list.setMinimumHeight(200)  # 保证至少显示 4-5 行

        # 注意：不再在 init_ui 中调用 _refresh_symbol_list，将在 showEvent 中延迟加载
        # 但为了 UI 结构完整，仍然创建空列表，后续填充
        # self._refresh_symbol_list()  已移除

        hint_label = QLabel("💡 提示：按住 Ctrl 或 Shift 可多选，点击「删除选中」批量删除")
        hint_label.setObjectName("setting_desc")
        hint_label.setStyleSheet(f"color: {text_secondary}; font-size: 12px; padding: 4px 0;")
        symbol_layout_inner.addWidget(hint_label)

        symbol_layout_inner.addWidget(self.symbol_list)

        def on_search():
            filtered = self.search_edit_symbol.text().strip()
            self._refresh_symbol_list(filtered)
        self.search_btn.clicked.connect(on_search)
        self.search_edit_symbol.returnPressed.connect(on_search)

        divider_line = QFrame()
        divider_line.setFrameShape(QFrame.HLine)
        divider_line.setStyleSheet(f"background-color: {border};")
        symbol_layout_inner.addWidget(divider_line)

        add_section_title = QLabel("新增符号")
        add_section_title.setObjectName("setting_title")
        symbol_layout_inner.addWidget(add_section_title)

        add_symbol_layout = QHBoxLayout()
        self.symbol_name_edit = QLineEdit()
        self.symbol_name_edit.setPlaceholderText("符号名称（如：括号）")
        add_symbol_layout.addWidget(self.symbol_name_edit)
        self.symbol_value_edit = QLineEdit()
        self.symbol_value_edit.setPlaceholderText("符号内容（如：（））")
        add_symbol_layout.addWidget(self.symbol_value_edit)
        # 替换为（注意 color='white' 和 setStyleSheet）
        self.add_symbol_btn = QPushButton(" 添加")
        # 图标固定白色
        self.add_symbol_btn.setIcon(qta.icon("fa5s.plus", color='white'))
        # 不要依赖 objectName，手动写样式
        # self.add_symbol_btn.setObjectName("saveBtn")  # 删掉这行（或注释掉）
        self.add_symbol_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {primary_light};
            }}
        """)
        add_symbol_layout.addWidget(self.add_symbol_btn)
        symbol_layout_inner.addLayout(add_symbol_layout)

        list_actions_layout = QHBoxLayout()
        self.edit_btn = QPushButton(" 编辑")
        self.edit_btn.setIcon(qta.icon("fa5s.edit", color=text))
        list_actions_layout.addWidget(self.edit_btn)
        self.delete_selected_symbol_btn = QPushButton(" 删除选中")
        self.delete_selected_symbol_btn.setIcon(qta.icon("fa5s.trash-alt", color=text))
        self.delete_selected_symbol_btn.setObjectName("softDeleteBtn")
        self.delete_selected_symbol_btn.clicked.connect(self.delete_selected_symbols)
        list_actions_layout.addWidget(self.delete_selected_symbol_btn)
        list_actions_layout.addStretch()
        self.restore_all_btn = QPushButton(" 恢复所有默认符号")
        self.restore_all_btn.setIcon(qta.icon("fa5s.undo", color=text))
        list_actions_layout.addWidget(self.restore_all_btn)
        symbol_layout_inner.addLayout(list_actions_layout)

        def edit_selected_symbol():
            selected_items = self.symbol_list.selectedItems()
            if not selected_items:
                self.main_window.show_toast("请先选中要编辑的符号")
                return
            item = selected_items[0]
            item_data = item.data(Qt.UserRole)
            if not item_data:
                return
            if len(item_data) == 4:
                item_type, key, display_name, display_value = item_data
            else:
                item_type, key, value = item_data
                display_name = key
                display_value = value
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("编辑符号")
            edit_dialog.setMinimumWidth(350)
            edit_dialog.setStyleSheet(self.main_window.theme_manager.generate_stylesheet())
            edit_layout = QVBoxLayout(edit_dialog)
            name_label = QLabel("符号名称：")
            name_edit = QLineEdit(display_name)
            value_label = QLabel("符号内容：")
            value_edit = QLineEdit(display_value)
            edit_layout.addWidget(name_label)
            edit_layout.addWidget(name_edit)
            edit_layout.addWidget(value_label)
            edit_layout.addWidget(value_edit)
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("确定")
            cancel_btn = QPushButton("取消")
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(cancel_btn)
            edit_layout.addLayout(btn_layout)

            def on_ok():
                new_name = name_edit.text().strip()
                new_value = value_edit.text().strip()
                if not new_name or not new_value:
                    self.main_window.show_toast("名称和内容不能为空")
                    return
                if item_type == "custom":
                    if key in self.custom_map:
                        del self.custom_map[key]
                    if key in self.main_window.custom_map:
                        del self.main_window.custom_map[key]
                    self.custom_map[new_name] = new_value
                    self.main_window.custom_map[new_name] = new_value
                    item.setText(f"⭐ {new_name}: {new_value}")
                    item.setData(Qt.UserRole, ("custom", new_name, new_value))
                    self.main_window.reload_custom_symbol_buttons()
                    if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                        self.main_window.symbol_panel.refresh_symbol_grid()
                    self.main_window.show_toast(f"符号「{new_name}」已修改")
                else:
                    custom_defaults = self.config_manager.get_config("Symbols", "custom_defaults", "{}")
                    try:
                        custom_defaults_data = json.loads(custom_defaults)
                    except:
                        custom_defaults_data = {}
                    custom_defaults_data[key] = {"name": new_name, "value": new_value}
                    self.config_manager.set_config("Symbols", "custom_defaults", json.dumps(custom_defaults_data))
                    status = "🔒" if key in self.disabled_default_symbols else "✓"
                    item.setText(f"{status} {new_name}: {new_value}")
                    item.setData(Qt.UserRole, ("default", key, new_name, new_value))
                    self.main_window.all_symbols = self.main_window.build_all_symbols()
                    self.main_window.render_symbol_buttons()
                    if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                        self.main_window.symbol_panel.refresh_symbol_grid()
                    self.main_window.show_toast(f"符号「{new_name}」已修改")
                edit_dialog.close()

            ok_btn.clicked.connect(on_ok)
            cancel_btn.clicked.connect(edit_dialog.close)
            edit_dialog.exec()

        self.edit_btn.clicked.connect(edit_selected_symbol)

        def add_custom_symbol():
            name = self.symbol_name_edit.text().strip()
            value = self.symbol_value_edit.text().strip()
            if name and value:
                if len(value) > 2:
                    self._show_themed_message_box("格式错误", "请输入1-2个字符的符号", QMessageBox.Warning)
                    return
                exists = False
                for i in range(self.symbol_list.count()):
                    item_data = self.symbol_list.item(i).data(Qt.UserRole)
                    if item_data and item_data[0] == "custom" and item_data[1] == name:
                        exists = True
                        break
                if not exists:
                    self.custom_map[name] = value
                    self.main_window.custom_map[name] = value
                    custom_symbols_list = [(k, v) for k, v in self.custom_map.items()]
                    self.config_manager.set_config("Symbols", "custom_symbols", json.dumps(custom_symbols_list, ensure_ascii=False))
                    item = QListWidgetItem(f"⭐ {name}: {value}")
                    item.setData(Qt.UserRole, ("custom", name, value))
                    self.symbol_list.addItem(item)
                    self.symbol_name_edit.clear()
                    self.symbol_value_edit.clear()
                    self.main_window.reload_custom_symbol_buttons()
                    if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                        self.main_window.symbol_panel.refresh_symbol_grid()
                    self.main_window.show_toast(f"符号「{name}」已添加")
                else:
                    self._show_themed_message_box("重复", "该符号名称已存在", QMessageBox.Warning)
            else:
                self._show_themed_message_box("提示", "请填写完整的符号信息", QMessageBox.Warning)

        self.add_symbol_btn.clicked.connect(add_custom_symbol)

        def restore_all_symbols():
            if self._show_question("确认恢复", "确定要恢复所有默认符号吗？\n\n这将恢复：\n- 所有被隐藏的符号\n- 所有被修改的符号名称和内容"):
                self.disabled_default_symbols.clear()
                self.main_window.disabled_default_symbols.clear()
                self.main_window.save_disabled_symbols()
                self.config_manager.set_config("Symbols", "custom_defaults", "{}")
                self.main_window.all_symbols = self.main_window.build_all_symbols()
                self.main_window.render_symbol_buttons()
                self._refresh_symbol_list(self.search_edit_symbol.text())
                if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                    self.main_window.symbol_panel.refresh_symbol_grid()
                self.main_window.show_toast("已恢复所有默认符号")

        self.restore_all_btn.clicked.connect(restore_all_symbols)

        symbol_content_layout.addWidget(card_symbol)
        scroll_symbol.setWidget(symbol_content)
        symbol_layout.addWidget(scroll_symbol)
        stacked.addWidget(symbol_page)

        # ---------- 公式助手页面 ----------
        formula_page = QWidget()
        formula_layout = QVBoxLayout(formula_page)
        formula_layout.setContentsMargins(0, 0, 0, 0)
        formula_layout.setSpacing(0)

        formula_content = QWidget()
        formula_content_layout = QVBoxLayout(formula_content)
        formula_content_layout.setContentsMargins(0, 0, 0, 20)
        formula_content_layout.setSpacing(16)

        card_formula = QFrame()
        card_formula.setObjectName("card")
        formula_layout_inner = QVBoxLayout(card_formula)
        formula_layout_inner.setSpacing(12)
        formula_title = QLabel("公式管理")
        formula_title.setObjectName("card_title")
        formula_layout_inner.addWidget(formula_title)
        formula_desc = QLabel("管理Excel公式模板，支持默认公式和自定义公式")
        formula_desc.setObjectName("setting_desc")
        formula_layout_inner.addWidget(formula_desc)

        search_layout = QHBoxLayout()
        self.formula_search_edit = QLineEdit()
        self.formula_search_edit.setPlaceholderText("搜索公式名称或公式内容...")
        search_layout.addWidget(self.formula_search_edit)
        self.formula_search_btn = QPushButton(" 搜索")
        self.formula_search_btn.setIcon(qta.icon("fa5s.search", color=text))
        search_layout.addWidget(self.formula_search_btn)
        formula_layout_inner.addLayout(search_layout)

        # 替换为：
        self.formula_list = QListWidget()
        self.formula_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.formula_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许扩展
        self.formula_list.setMinimumHeight(200)  # 保证至少显示 4-5 行

        hint_label2 = QLabel("💡 提示：按住 Ctrl 或 Shift 可多选，点击「删除选中」批量删除")
        hint_label2.setObjectName("setting_desc")
        hint_label2.setStyleSheet(f"color: {text_secondary}; font-size: 12px; padding: 4px 0;")
        formula_layout_inner.addWidget(hint_label2)

        formula_layout_inner.addWidget(self.formula_list)

        formula_divider_line = QFrame()
        formula_divider_line.setFrameShape(QFrame.HLine)
        formula_divider_line.setStyleSheet(f"background-color: {border};")
        formula_layout_inner.addWidget(formula_divider_line)

        formula_add_section_title = QLabel("新增公式")
        formula_add_section_title.setObjectName("setting_title")
        formula_layout_inner.addWidget(formula_add_section_title)

        add_formula_layout = QHBoxLayout()
        self.formula_name_edit = QLineEdit()
        self.formula_name_edit.setPlaceholderText("公式名称（如：求和）")
        add_formula_layout.addWidget(self.formula_name_edit)
        self.formula_value_edit = QLineEdit()
        self.formula_value_edit.setPlaceholderText("公式内容（如：=SUM(A1:A10)）")
        add_formula_layout.addWidget(self.formula_value_edit)
        # 替换为
        self.add_formula_btn = QPushButton(" 添加")
        self.add_formula_btn.setIcon(qta.icon("fa5s.plus", color='white'))
        # self.add_formula_btn.setObjectName("saveBtn")  # 删掉这行（或注释掉）
        self.add_formula_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {primary};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {primary_light};
            }}
        """)
        add_formula_layout.addWidget(self.add_formula_btn)
        formula_layout_inner.addLayout(add_formula_layout)

        formula_list_actions_layout = QHBoxLayout()
        self.formula_edit_btn = QPushButton(" 编辑")
        self.formula_edit_btn.setIcon(qta.icon("fa5s.edit", color=text))
        formula_list_actions_layout.addWidget(self.formula_edit_btn)
        self.delete_selected_btn = QPushButton(" 删除选中")
        self.delete_selected_btn.setIcon(qta.icon("fa5s.trash-alt", color=text))
        self.delete_selected_btn.setObjectName("softDeleteBtn")
        self.delete_selected_btn.clicked.connect(self.delete_selected_formulas)
        formula_list_actions_layout.addWidget(self.delete_selected_btn)
        formula_list_actions_layout.addStretch()
        self.reset_formula_btn = QPushButton(" 重置默认公式")
        self.reset_formula_btn.setIcon(qta.icon("fa5s.undo", color=text))
        formula_list_actions_layout.addWidget(self.reset_formula_btn)
        formula_layout_inner.addLayout(formula_list_actions_layout)

        def on_formula_search():
            filtered = self.formula_search_edit.text().strip()
            self.refresh_formula_list(filtered)
        self.formula_search_btn.clicked.connect(on_formula_search)
        self.formula_search_edit.returnPressed.connect(on_formula_search)

        def add_custom_formula():
            name = self.formula_name_edit.text().strip()
            value = self.formula_value_edit.text().strip()
            if name and value:
                exists = False
                for i in range(self.formula_list.count()):
                    item_data = self.formula_list.item(i).data(Qt.UserRole)
                    if item_data and ((item_data[0] == "custom" and item_data[1] == name) or (item_data[0] == "default" and item_data[1] == name)):
                        exists = True
                        break
                if not exists:
                    self._custom_formulas.append((name, value))
                    item = QListWidgetItem(f"⭐ {name}: {value}")
                    item.setData(Qt.UserRole, ("custom", name, value))
                    self.formula_list.addItem(item)
                    self.formula_name_edit.clear()
                    self.formula_value_edit.clear()
                    # 实时保存到配置
                    custom_formulas_str = ";;".join([f"{a}|{b}" for a, b in self._custom_formulas])
                    self.config_manager.set_config("SymbolPanel", "custom_formulas", custom_formulas_str)
                    self.main_window.show_toast(f"公式「{name}」已添加")
                else:
                    self._show_themed_message_box("重复", "该公式名称已存在", QMessageBox.Warning)
            else:
                self._show_themed_message_box("提示", "请填写完整的公式信息", QMessageBox.Warning)

        self.add_formula_btn.clicked.connect(add_custom_formula)

        def edit_selected_formula():
            selected_items = self.formula_list.selectedItems()
            if not selected_items:
                self.main_window.show_toast("请先选中要编辑的公式")
                return
            item = selected_items[0]
            item_data = item.data(Qt.UserRole)
            if not item_data:
                return
            if len(item_data) == 4:
                item_type, key, display_name, display_value = item_data
            else:
                item_type, key, value = item_data
                display_name = key
                display_value = value

            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("编辑公式")
            edit_dialog.setMinimumWidth(400)
            edit_dialog.setStyleSheet(self.main_window.theme_manager.generate_stylesheet())
            edit_layout = QVBoxLayout(edit_dialog)
            name_label = QLabel("公式名称：")
            name_edit = QLineEdit(display_name)
            value_label = QLabel("公式内容：")
            value_edit = QLineEdit(display_value)
            edit_layout.addWidget(name_label)
            edit_layout.addWidget(name_edit)
            edit_layout.addWidget(value_label)
            edit_layout.addWidget(value_edit)
            btn_layout = QHBoxLayout()
            ok_btn = QPushButton("确定")
            cancel_btn = QPushButton("取消")
            btn_layout.addStretch()
            btn_layout.addWidget(ok_btn)
            btn_layout.addWidget(cancel_btn)
            edit_layout.addLayout(btn_layout)

            def on_ok():
                new_name = name_edit.text().strip()
                new_value = value_edit.text().strip()
                if not new_name or not new_value:
                    self.main_window.show_toast("名称和内容不能为空")
                    return
                if item_type == "custom":
                    self._custom_formulas = [(n, v) for n, v in self._custom_formulas if n != key]
                    self._custom_formulas.append((new_name, new_value))
                    item.setText(f"⭐ {new_name}: {new_value}")
                    item.setData(Qt.UserRole, ("custom", new_name, new_value))
                    # 实时保存到配置
                    custom_formulas_str = ";;".join([f"{a}|{b}" for a, b in self._custom_formulas])
                    self.config_manager.set_config("SymbolPanel", "custom_formulas", custom_formulas_str)
                    self.main_window.show_toast(f"公式「{new_name}」已修改")
                else:
                    if not hasattr(self, "_custom_defaults"):
                        custom_defaults_str = self.config_manager.get_config("Formulas", "custom_defaults", "{}")
                        try:
                            self._custom_defaults = json.loads(custom_defaults_str)
                        except:
                            self._custom_defaults = {}
                    self._custom_defaults[key] = {"name": new_name, "value": new_value}
                    custom_defaults_str = json.dumps(self._custom_defaults, ensure_ascii=False)
                    self.config_manager.set_config("Formulas", "custom_defaults", custom_defaults_str)
                    status = "🔒" if key in self.disabled_default_formulas else "✓"
                    item.setText(f"{status} {new_name}: {new_value}")
                    item.setData(Qt.UserRole, ("default", key, new_name, new_value))
                    self.main_window.show_toast(f"公式「{new_name}」已修改")
                edit_dialog.close()

            ok_btn.clicked.connect(on_ok)
            cancel_btn.clicked.connect(edit_dialog.close)
            edit_dialog.exec()

        self.formula_edit_btn.clicked.connect(edit_selected_formula)

        def reset_formulas():
            if self._show_question("确认重置", "确定要恢复所有默认公式吗？\n\n这将恢复：\n- 所有被隐藏的公式\n- 所有被修改的公式名称和内容"):
                self.disabled_default_formulas = []
                self.config_manager.set_config("SymbolPanel", "disabled_default_formulas", "[]")
                self.config_manager.set_config("Formulas", "custom_defaults", "{}")
                self.refresh_formula_list(self.formula_search_edit.text())
                if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                    self.main_window.symbol_panel.disabled_default_formulas = []
                    self.main_window.symbol_panel.refresh_formula_list()
                self.main_window.show_toast("已恢复所有默认公式")

        self.reset_formula_btn.clicked.connect(reset_formulas)

        formula_content_layout.addWidget(card_formula)
        scroll_formula = QScrollArea()
        scroll_formula.setWidgetResizable(True)
        scroll_formula.setFrameShape(QFrame.NoFrame)
        scroll_formula.setWidget(formula_content)
        formula_layout.addWidget(scroll_formula)
        stacked.addWidget(formula_page)

        # ---------- 备份恢复页面 ----------
        backup_page = QWidget()
        backup_layout = QVBoxLayout(backup_page)
        backup_layout.setContentsMargins(0, 0, 0, 0)
        backup_layout.setSpacing(0)
        scroll_backup = QScrollArea()
        scroll_backup.setWidgetResizable(True)
        scroll_backup.setFrameShape(QFrame.NoFrame)
        backup_content = QWidget()
        backup_content_layout = QVBoxLayout(backup_content)
        backup_content_layout.setContentsMargins(0, 0, 0, 20)
        backup_content_layout.setSpacing(0)

        card_backup = QFrame()
        card_backup.setObjectName("card")
        backup_inner_layout = QVBoxLayout(card_backup)
        backup_inner_layout.setSpacing(12)
        backup_title = QLabel("数据备份与恢复")
        backup_title.setObjectName("card_title")
        backup_inner_layout.addWidget(backup_title)
        backup_desc = QLabel("备份配置文件，防止数据丢失")
        backup_desc.setObjectName("setting_desc")
        backup_inner_layout.addWidget(backup_desc)

        module_title = QLabel("备份内容选择")
        module_title.setObjectName("setting_title")
        backup_inner_layout.addWidget(module_title)
        module_row1 = QHBoxLayout()
        self.backup_config_check = QCheckBox("配置文件")
        self.backup_config_check.setChecked(True)
        self.backup_clipboard_check = QCheckBox("剪贴板历史")
        self.backup_clipboard_check.setChecked(True)
        self.backup_symbols_check = QCheckBox("自定义符号")
        self.backup_symbols_check.setChecked(True)
        module_row1.addWidget(self.backup_config_check)
        module_row1.addWidget(self.backup_clipboard_check)
        module_row1.addWidget(self.backup_symbols_check)
        backup_inner_layout.addLayout(module_row1)
        module_row2 = QHBoxLayout()
        self.backup_formulas_check = QCheckBox("自定义公式")
        self.backup_formulas_check.setChecked(True)
        self.backup_activation_check = QCheckBox("激活信息")
        self.backup_activation_check.setChecked(True)
        module_row2.addWidget(self.backup_formulas_check)
        module_row2.addWidget(self.backup_activation_check)
        module_row2.addStretch()
        backup_inner_layout.addLayout(module_row2)

        backup_location_row = QHBoxLayout()
        backup_location_label = QLabel("备份存储位置：")
        backup_location_label.setMinimumWidth(120)
        backup_location_row.addWidget(backup_location_label)
        self.backup_location_edit = QLineEdit()
        default_backup_dir = os.path.join(self.config_manager.data_dir, "backups")
        self.backup_location_edit.setText(self.config_manager.get_config("Backup", "backup_dir", default_backup_dir))
        backup_location_row.addWidget(self.backup_location_edit)
        self.backup_location_btn = QPushButton(" 浏览")
        self.backup_location_btn.setIcon(qta.icon("fa5s.folder-open", color=text))
        self.backup_location_btn.clicked.connect(lambda: self.backup_location_edit.setText(QFileDialog.getExistingDirectory(self, "选择备份存储位置", self.backup_location_edit.text()) or self.backup_location_edit.text()))
        backup_location_row.addWidget(self.backup_location_btn)
        backup_inner_layout.addLayout(backup_location_row)

        auto_backup_row = QHBoxLayout()
        self.auto_backup_check = QCheckBox("自动备份")
        self.auto_backup_check.setChecked(self.config_manager.get_config("Backup", "auto_backup", "false") == "true")
        auto_backup_row.addWidget(self.auto_backup_check)
        auto_freq_label = QLabel("频率：")
        auto_freq_label.setMinimumWidth(50)
        auto_backup_row.addWidget(auto_freq_label)
        self.auto_backup_combo = NoWheelComboBox()
        self.auto_backup_combo.addItems(["每天", "每周", "每月"])
        saved_freq = self.config_manager.get_config("Backup", "auto_backup_freq", "每周")
        idx = self.auto_backup_combo.findText(saved_freq)
        if idx >= 0:
            self.auto_backup_combo.setCurrentIndex(idx)
        auto_backup_row.addWidget(self.auto_backup_combo)
        keep_label = QLabel("保留份数：")
        keep_label.setMinimumWidth(70)
        auto_backup_row.addWidget(keep_label)
        self.keep_backup_spin = NoWheelSpinBox()
        self.keep_backup_spin.setRange(1, 30)
        self.keep_backup_spin.setValue(int(self.config_manager.get_config("Backup", "keep_count", "5")))
        auto_backup_row.addWidget(self.keep_backup_spin)
        auto_backup_row.addStretch()
        backup_inner_layout.addLayout(auto_backup_row)

        backup_history_title = QLabel("备份历史")
        backup_history_title.setObjectName("setting_title")
        backup_inner_layout.addWidget(backup_history_title)
        # 替换为：
        self.backup_list = QListWidget()
        self.backup_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允许扩展
        self.backup_list.setMinimumHeight(120)  # 保证至少显示 3-4 行
        self.backup_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.backup_list.customContextMenuRequested.connect(self._show_backup_context_menu)
        backup_inner_layout.addWidget(self.backup_list)

        btn_row = QHBoxLayout()
        self.backup_btn = QPushButton(" 立即备份")
        self.backup_btn.setIcon(qta.icon("fa5s.hdd", color=text))
        btn_row.addWidget(self.backup_btn)
        self.restore_btn = QPushButton(" 从备份恢复")
        self.restore_btn.setIcon(qta.icon("fa5s.undo-alt", color=text))
        btn_row.addWidget(self.restore_btn)
        self.clean_backup_btn = QPushButton(" 清理旧备份")
        self.clean_backup_btn.setIcon(qta.icon("fa5s.trash-alt", color=text))
        btn_row.addWidget(self.clean_backup_btn)
        backup_inner_layout.addLayout(btn_row)
        backup_content_layout.addWidget(card_backup)

        scroll_backup.setWidget(backup_content)
        backup_layout.addWidget(scroll_backup)
        stacked.addWidget(backup_page)

        # ---------- 新手引导页面 ----------
        guide_page = QWidget()
        guide_layout = QVBoxLayout(guide_page)
        guide_layout.setContentsMargins(0, 0, 0, 0)
        guide_layout.setSpacing(0)
        scroll_guide = QScrollArea()
        scroll_guide.setWidgetResizable(True)
        scroll_guide.setFrameShape(QFrame.NoFrame)
        guide_content = QWidget()
        guide_content_layout = QVBoxLayout(guide_content)
        guide_content_layout.setContentsMargins(0, 0, 0, 20)
        guide_content_layout.setSpacing(16)

        card_guide = QFrame()
        card_guide.setObjectName("card")
        guide_inner_layout = QVBoxLayout(card_guide)
        guide_inner_layout.setSpacing(12)
        guide_title = QLabel("新手引导")
        guide_title.setObjectName("card_title")
        guide_inner_layout.addWidget(guide_title)
        guide_desc = QLabel("引导您快速了解软件的各项功能")
        guide_desc.setObjectName("setting_desc")
        guide_inner_layout.addWidget(guide_desc)
        tip_label = QLabel("💡 点击「立即体验引导」将自动保存当前设置并返回主窗口")
        tip_label.setStyleSheet("color: #409eff; font-size: 12px;")
        guide_inner_layout.addWidget(tip_label)
        self.start_guide_btn = QPushButton(" 立即体验引导")
        self.start_guide_btn.setIcon(qta.icon("fa5s.play", color=primary))

        def start_guide_and_save():
            self.auto_remove_blank_lines = self.auto_remove_blank_lines_check.isChecked()
            self.auto_remove_extra_spaces = self.auto_remove_extra_spaces_check.isChecked()
            self.auto_remove_all_whitespace = self.auto_remove_all_whitespace_check.isChecked()
            self.split_mode = self.split_combo.currentIndex()
            new_theme = self.theme_combo.currentData()
            if new_theme and new_theme != self.theme_manager.current_theme:
                if not (self.theme_manager.is_pro_theme(new_theme) and not self.activation_manager.is_activated()):
                    self.theme_manager.set_theme(new_theme)
                    self.main_window.apply_theme()
            custom_symbols_list = [(k, v) for k, v in self.custom_map.items()]
            self.config_manager.set_config("Symbols", "custom_symbols", json.dumps(custom_symbols_list, ensure_ascii=False))
            self.config_manager.set_config("Symbols", "disabled_default_symbols", json.dumps(self.disabled_default_symbols, ensure_ascii=False))
            self.config_manager.set_config("SymbolPanel", "disabled_default_formulas", json.dumps(self.disabled_default_formulas))
            self.config_manager.set_config("Experience", "auto_remove_blank_lines", str(self.auto_remove_blank_lines).lower())
            self.config_manager.set_config("Experience", "auto_remove_extra_spaces", str(self.auto_remove_extra_spaces).lower())
            self.config_manager.set_config("Experience", "auto_remove_all_whitespace", str(self.auto_remove_all_whitespace).lower())
            self.config_manager.set_config("App", "split_mode", str(self.split_mode))
            self.config_manager.set_config("App", "theme", self.theme_manager.current_theme)
            self.main_window.reload_custom_symbol_buttons()
            # 重置所有标签页的引导状态，准备开始新的引导流程
            self.main_window.guide_manager.reset_guide(tab_index=None)
            self.accept()

            def do_post_updates():
                self.main_window.raise_()
                self.main_window.activateWindow()
                # 显示当前标签页的引导（设置页面关闭时的当前标签页）
                current_tab = self.main_window.tab_widget.currentIndex()
                self.main_window.guide_manager.show_guide_for_tab(current_tab)
                if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
                    self.main_window.symbol_panel.load_custom_formulas()
                    self.main_window.symbol_panel.load_disabled_default_formulas()
                    self.main_window.symbol_panel.refresh_symbol_grid()
                    self.main_window.symbol_panel.refresh_formula_list()
                self.main_window.all_symbols = self.main_window.build_all_symbols()
                self.main_window.render_symbol_buttons()
                self.main_window._load_disabled_formulas()
            QTimer.singleShot(0, do_post_updates)

        self.start_guide_btn.clicked.connect(start_guide_and_save)
        guide_inner_layout.addWidget(self.start_guide_btn)
        guide_content_layout.addWidget(card_guide)

        card_features = QFrame()
        card_features.setObjectName("card")
        features_layout = QVBoxLayout(card_features)
        features_layout.setSpacing(12)
        features_title = QLabel("功能介绍")
        features_title.setObjectName("card_title")
        features_layout.addWidget(features_title)
        features_list = QTextEdit()
        features_list.setReadOnly(True)
        features_list.setStyleSheet("background-color: transparent; border: none;")
        features_list.setPlainText("""主要功能：
    • 符号面板：快速输入常用符号
    • Excel编辑：查看和编辑Excel表格
    • 文本处理：查看和编辑文档
    • 符号与公式助手：在后台快速输入常用符号和公式
    • 工具箱：批量重命名、格式转换等工具
""")
   
        features_layout.addWidget(features_list)
        guide_content_layout.addWidget(card_features)

        scroll_guide.setWidget(guide_content)
        guide_layout.addWidget(scroll_guide)
        stacked.addWidget(guide_page)

        # ---------- 关于软件页面 ----------
        about_page = QWidget()
        about_layout = QVBoxLayout(about_page)
        about_layout.setContentsMargins(0, 0, 0, 0)
        about_layout.setSpacing(0)
        scroll_about = QScrollArea()
        scroll_about.setWidgetResizable(True)
        scroll_about.setFrameShape(QFrame.NoFrame)
        about_content = QWidget()
        about_content_layout = QVBoxLayout(about_content)
        about_content_layout.setContentsMargins(0, 0, 0, 20)
        about_content_layout.setSpacing(0)

        card_about = QFrame()
        card_about.setObjectName("card")
        about_inner_layout = QVBoxLayout(card_about)
        about_inner_layout.setSpacing(12)
        about_title = QLabel("关于软件")
        about_title.setObjectName("card_title")
        about_inner_layout.addWidget(about_title)
        version_label = QLabel(f"版本号：{APP_NAME} {VERSION}")
        version_label.setObjectName("setting_desc")
        about_inner_layout.addWidget(version_label)
        build_info = QLabel("构建日期：2026-05-26 | 许可证：MIT")
        build_info.setObjectName("setting_desc")
        about_inner_layout.addWidget(build_info)
        copy_info = QLabel("© 2026 小雨办公工具 版权所有")
        copy_info.setObjectName("setting_desc")
        about_inner_layout.addWidget(copy_info)
        contact_label = QLabel("📞 微信 fangbaby2233 | QQ 2818491757")
        contact_label.setObjectName("setting_desc")
        about_inner_layout.addWidget(contact_label)
        about_content_layout.addWidget(card_about)

        card_deps = QFrame()
        card_deps.setObjectName("card")
        deps_layout = QVBoxLayout(card_deps)
        deps_layout.setSpacing(12)
        deps_title = QLabel("第三方依赖")
        deps_title.setObjectName("card_title")
        deps_layout.addWidget(deps_title)
        deps_desc = QLabel("本软件使用的开源库及其许可证")
        deps_desc.setObjectName("setting_desc")
        deps_layout.addWidget(deps_desc)
        self.deps_list = QListWidget()
        dependencies = [("PySide6", "LGPL"), ("openpyxl", "MIT"), ("python-docx", "MIT"), ("Pillow", "HPIED"), ("pytesseract", "Apache 2.0"), ("python-dotenv", "BSD"), ("cryptography", "Apache 2.0 / BSD"), ("qtawesome", "MIT"), ("jieba", "MIT")]
        for name, license in dependencies:
            self.deps_list.addItem(f"{name} ({license})")
        deps_layout.addWidget(self.deps_list)
        about_content_layout.addWidget(card_deps)

        card_actions = QFrame()
        card_actions.setObjectName("card")
        actions_layout = QVBoxLayout(card_actions)
        actions_layout.setSpacing(12)
        actions_title = QLabel("实用工具")
        actions_title.setObjectName("card_title")
        actions_layout.addWidget(actions_title)
        actions_btn_row = QHBoxLayout()
        self.open_config_btn = QPushButton(" 打开配置文件夹")
        self.open_config_btn.setIcon(qta.icon("fa5s.folder-open", color=text))
        self.open_config_btn.clicked.connect(self._open_config_folder)
        self.open_log_btn = QPushButton(" 查看日志")
        self.open_log_btn.setIcon(qta.icon("fa5s.file-alt", color=text))
        self.open_log_btn.clicked.connect(self._open_log_folder)
        actions_btn_row.addWidget(self.open_config_btn)
        actions_btn_row.addWidget(self.open_log_btn)
        actions_layout.addLayout(actions_btn_row)
        about_content_layout.addWidget(card_actions)

        scroll_about.setWidget(about_content)
        about_layout.addWidget(scroll_about)
        stacked.addWidget(about_page)

        # 左侧导航栏
        nav_list = QListWidget()
        nav_list.setObjectName("sidebar")
        nav_list.setFixedWidth(190)
        nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        nav_items = [
            ("通用设置", "cog", general_page),
            ("界面设置", "palette", ui_page),
            ("符号设置", "plus-circle", symbol_page),
            ("公式助手", "calculator", formula_page),
            ("备份恢复", "hdd", backup_page),
            ("新手引导", "lightbulb", guide_page),
            ("关于软件", "info-circle", about_page),
        ]
        for name, icon, page in nav_items:
            item = QListWidgetItem(qta.icon(f"fa5s.{icon}", color=text), name)
            nav_list.addItem(item)
        nav_list.setCurrentRow(0)

        def on_nav_changed(current, previous):
            if current is None:
                return
            idx = nav_list.row(current)
            if 0 <= idx < stacked.count():
                stacked.setCurrentIndex(idx)
                if idx == 4:  # 备份恢复页面的索引
                    self._refresh_backup_list()
        nav_list.currentItemChanged.connect(on_nav_changed)

        right_header = QWidget()
        right_header_layout = QHBoxLayout(right_header)
        right_header_layout.setContentsMargins(0, 0, 0, 0)
        right_header_label = QLabel("设置")
        right_header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 8px;")
        right_header_layout.addWidget(right_header_label)
        right_header_layout.addStretch()

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 20, 0, 0)
        bottom_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        save_btn = QPushButton("保存")
        save_btn.setObjectName("saveBtn")
        save_btn.setCursor(Qt.PointingHandCursor)
        bottom_layout.addWidget(cancel_btn)
        bottom_layout.addWidget(save_btn)
        bottom_widget.setFixedHeight(70)

        right_container = QWidget()
        right_container_layout = QVBoxLayout(right_container)
        right_container_layout.setContentsMargins(0, 0, 0, 0)
        right_container_layout.setSpacing(0)
        right_container_layout.addWidget(right_header, 0)
        right_container_layout.addWidget(stacked, 1)
        right_container_layout.addWidget(bottom_widget, 0)

        main_layout.addWidget(nav_list)
        main_layout.addWidget(right_container, 1)

        # ===== 关键修改：不在这里调用 _refresh_symbol_list 和 refresh_formula_list =====
        # 改为在 showEvent 中延迟加载
        # 修改为：
        # 在 init_ui 末尾
        QTimer.singleShot(0, self._refresh_symbol_list)   # 加载符号列表
        QTimer.singleShot(0, self.refresh_formula_list)   # 加载公式列表
        QTimer.singleShot(100, self.adjustSize)

        # ---------- 备份恢复相关函数 ----------
        def _do_backup():
            backup_dir = self.backup_location_edit.text().strip()
            if not backup_dir:
                self._show_themed_message_box("错误", "请先设置备份存储位置", QMessageBox.Warning)
                return
            try:
                os.makedirs(backup_dir, exist_ok=True)
            except Exception as e:
                self._show_themed_message_box("错误", f"无法创建备份目录：{str(e)}", QMessageBox.Critical)
                return
            import shutil
            from datetime import datetime
            config_path = self.config_manager.config_path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"config_backup_{timestamp}.ini")
            try:
                shutil.copy(config_path, backup_path)
                self._refresh_backup_list()
                self.main_window.show_toast("备份成功！")
            except Exception as e:
                self._show_themed_message_box("错误", f"备份失败：{str(e)}", QMessageBox.Critical)

        self.backup_btn.clicked.connect(_do_backup)

        def _do_restore():
            selected = self.backup_list.currentItem()
            if not selected:
                self._show_themed_message_box("提示", "请先在备份历史中选择一个备份", QMessageBox.Warning)
                return
            text = selected.text()
            fname = text.split("|")[-1].strip()
            backup_dir = self.backup_location_edit.text().strip()
            backup_path = os.path.join(backup_dir, fname)
            if os.path.exists(backup_path):
                if self._show_question("确认恢复", "恢复将覆盖当前配置，确定继续？"):
                    import shutil
                    shutil.copy(backup_path, self.config_manager.config_path)
                    self.main_window.show_toast("已恢复配置，请重启程序")
            else:
                self._show_themed_message_box("错误", f"备份文件不存在：{backup_path}", QMessageBox.Critical)

        self.restore_btn.clicked.connect(_do_restore)

        def _do_clean_backup():
            if self._show_question("确认清理", "确定要清理所有备份文件吗？"):
                backup_dir = self.backup_location_edit.text().strip()
                if os.path.exists(backup_dir):
                    import shutil
                    shutil.rmtree(backup_dir, ignore_errors=True)
                    os.makedirs(backup_dir, exist_ok=True)
                self._refresh_backup_list()
                self.main_window.show_toast("已清理所有备份")

        self.clean_backup_btn.clicked.connect(_do_clean_backup)

        save_btn.clicked.connect(self.save_all_settings)
        cancel_btn.clicked.connect(self.reject)

    def showEvent(self, event):
        """窗口显示后调整大小，不再重复加载数据"""
        super().showEvent(event)
        QTimer.singleShot(150, self.adjustSize)
        # 移除 _delayed_load 调用，避免数据重复加载导致冲突

    def _delayed_load(self):
        """延迟加载符号和公式列表"""
        self._refresh_symbol_list()
        self.refresh_formula_list()
        QTimer.singleShot(50, self.adjustSize)

    def _refresh_symbol_list(self, filter_text=""):
        self.symbol_list.setUpdatesEnabled(False)
        self.symbol_list.clear()
        custom_defaults = self.config_manager.get_config("Symbols", "custom_defaults", "{}")
        try:
            custom_defaults_data = json.loads(custom_defaults)
        except:
            custom_defaults_data = {}

        current_lang = "zh"
        if hasattr(self.main_window, 'text_processor'):
            current_lang = self.main_window.text_processor.language
        elif hasattr(self.main_window, 'language'):
            current_lang = self.main_window.language

        # 逐个添加，确保 item 不被回收
        for key, sym_info in self.DEFAULT_SYMBOL_NAMES.items():
            if key in self.disabled_default_symbols:
                continue
            display_name = sym_info["name"]
            if current_lang == "en":
                display_value = sym_info["en"]
            else:
                display_value = sym_info["zh"]
            if key in custom_defaults_data:
                if "name" in custom_defaults_data[key]:
                    display_name = custom_defaults_data[key]["name"]
                if "value" in custom_defaults_data[key]:
                    display_value = custom_defaults_data[key]["value"]
            if filter_text:
                filter_lower = filter_text.lower()
                if filter_lower not in display_name.lower() and filter_lower not in display_value.lower():
                    continue
            item_text = f"✓ {display_name}: {display_value}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, ('default', key, display_name, display_value))
            self.symbol_list.addItem(item)  # ✅ 逐个添加

        for key, value in self.custom_map.items():
            if filter_text:
                filter_lower = filter_text.lower()
                if filter_lower not in key.lower() and filter_lower not in value.lower():
                    continue
            item_text = f"⭐ {key}: {value}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, ('custom', key, value))
            self.symbol_list.addItem(item)  # ✅ 逐个添加

        self.symbol_list.setUpdatesEnabled(True)

    def delete_selected_symbols(self):
        selected_items = self.symbol_list.selectedItems()
        if not selected_items:
            self.main_window.show_toast("请先选中要删除的符号")
            return

        to_disable_default = []
        to_remove_custom = []
        rows_to_remove = []

        for item in selected_items:
            row = self.symbol_list.row(item)
            item_data = item.data(Qt.UserRole)
            if not item_data:
                continue
            if len(item_data) == 4:
                _, key, display_name, _ = item_data
                if key not in self.disabled_default_symbols:
                    to_disable_default.append((key, display_name))
                    rows_to_remove.append(row)
            else:
                _, key, value = item_data
                to_remove_custom.append((key, row))
                rows_to_remove.append(row)

        if not rows_to_remove:
            self.main_window.show_toast("未选中有效的符号")
            return

        if to_disable_default:
            for key, _ in to_disable_default:
                self.disabled_default_symbols.append(key)

        if to_remove_custom:
            for key, _ in to_remove_custom:
                if key in self.custom_map:
                    del self.custom_map[key]

        rows_to_remove.sort(reverse=True)
        for row in rows_to_remove:
            self.symbol_list.takeItem(row)

        self.main_window.show_toast(f"已删除 {len(selected_items)} 个符号（需点击保存生效）")

    def delete_selected_formulas(self):
        try:
            selected_items = self.formula_list.selectedItems()
            if not selected_items:
                self.main_window.show_toast("请先选择要删除的公式")
                return

            to_disable_default = []
            to_remove_custom = []
            rows_to_remove = []

            for item in selected_items:
                row = self.formula_list.row(item)
                item_data = item.data(Qt.UserRole)
                if not item_data:
                    continue
                if len(item_data) == 4:
                    _, key, display_name, _ = item_data
                    if key not in self.disabled_default_formulas:
                        to_disable_default.append((key, display_name))
                        rows_to_remove.append(row)
                else:
                    _, name, _ = item_data
                    to_remove_custom.append((name, row))
                    rows_to_remove.append(row)

            if not rows_to_remove:
                self.main_window.show_toast("未选中有效的公式")
                return

            if to_disable_default:
                for key, _ in to_disable_default:
                    if key not in self.disabled_default_formulas:
                        self.disabled_default_formulas.append(key)

            if to_remove_custom:
                custom_formulas_str = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
                self._custom_formulas = [tuple(f.split("|")) for f in custom_formulas_str.split(";;") if f] if custom_formulas_str else []
                names_to_remove = [name for name, _ in to_remove_custom]
                self._custom_formulas = [(n, v) for n, v in self._custom_formulas if n not in names_to_remove]

            rows_to_remove.sort(reverse=True)
            for row in rows_to_remove:
                self.formula_list.takeItem(row)

            self.main_window.show_toast(f"已删除 {len(selected_items)} 个公式（需点击保存生效）")
        except Exception as e:
            print(f"删除公式异常: {e}")
            self.main_window.show_toast("删除公式失败，请重试")

    def refresh_formula_list(self, filter_text=""):
        """刷新公式列表（使用逐个添加，避免垃圾回收问题）"""
        self.formula_list.setUpdatesEnabled(False)
        self.formula_list.clear()
        from ui.symbol_panel import SymbolPanel

        custom_defaults = self.config_manager.get_config("Formulas", "custom_defaults", "{}")
        try:
            custom_defaults_data = json.loads(custom_defaults)
        except:
            custom_defaults_data = {}

        # 逐个添加默认公式
        for default_name, default_value in SymbolPanel.DEFAULT_FORMULAS:
            if default_name in self.disabled_default_formulas:
                continue
            name = default_name
            value = default_value
            if default_name in custom_defaults_data:
                if "name" in custom_defaults_data[default_name]:
                    name = custom_defaults_data[default_name]["name"]
                if "value" in custom_defaults_data[default_name]:
                    value = custom_defaults_data[default_name]["value"]
            item_text = f"✓ {name}: {value}"
            if filter_text:
                if filter_text.lower() not in name.lower() and filter_text.lower() not in value.lower():
                    continue
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, ("default", default_name, name, value))
            self.formula_list.addItem(item)  # ✅ 逐个添加

        # 逐个添加自定义公式
        custom_formulas_str = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
        custom_formulas = [tuple(f.split("|")) for f in custom_formulas_str.split(";;") if f] if custom_formulas_str else []
        for name, value in custom_formulas:
            item_text = f"⭐ {name}: {value}"
            if filter_text:
                if filter_text.lower() not in name.lower() and filter_text.lower() not in value.lower():
                    continue
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, ("custom", name, value))
            self.formula_list.addItem(item)  # ✅ 逐个添加

        self.formula_list.setUpdatesEnabled(True)

    def save_all_settings(self):
        self.main_window.auto_remove_blank_lines = self.auto_remove_blank_lines_check.isChecked()
        self.main_window.auto_remove_extra_spaces = self.auto_remove_extra_spaces_check.isChecked()
        self.main_window.auto_remove_all_whitespace = self.auto_remove_all_whitespace_check.isChecked()
        self.main_window.skip_empty_cells = self.skip_empty_cells_check.isChecked()
        self.main_window.split_mode = self.split_combo.currentIndex()

        new_theme = self.theme_combo.currentData()
        theme_changed = False
        if new_theme and new_theme != self.theme_manager.current_theme:
            if not self.activation_manager.is_activated() and new_theme != "blue":
                self._show_themed_message_box("权限不足", "该主题为 Pro 版专属，请先升级。\n升级后可畅享所有主题及更多高级功能。", QMessageBox.Warning)
                idx = self.theme_combo.findData(self.theme_manager.current_theme)
                if idx >= 0:
                    self.theme_combo.setCurrentIndex(idx)
            else:
                self.theme_manager.set_theme(new_theme)
                theme_changed = True
                self.main_window.show_toast(f"已切换为「{self.theme_manager.THEMES[new_theme]['name']}」主题")
        # ✅ 在这里加上这一行：
        self._theme_changed = theme_changed

        custom_symbols_list = [(key, value) for key, value in self.custom_map.items()]

        custom_formulas_str = ";;".join([f"{a}|{b}" for a, b in self._custom_formulas])

        if hasattr(self, "_custom_defaults"):
            custom_defaults_str = json.dumps(self._custom_defaults, ensure_ascii=False)
        else:
            custom_defaults_str = self.config_manager.get_config("Formulas", "custom_defaults", "{}")

        config_list = [
            ("Symbols", "custom_symbols", json.dumps(custom_symbols_list, ensure_ascii=False)),
            ("Symbols", "disabled_default_symbols", json.dumps(self.disabled_default_symbols, ensure_ascii=False)),
            ("SymbolPanel", "disabled_default_formulas", json.dumps(self.disabled_default_formulas)),
            ("SymbolPanel", "custom_formulas", custom_formulas_str),
            ("Formulas", "custom_defaults", custom_defaults_str),
            ("UI", "default_page", self.default_page_combo.currentText()),
            # 缩放和字体
            ("UI", "scale_factor", self.scale_combo.currentText().replace("%", "")),
            ("UI", "font_family", self.font_combo.currentFont().family()),
            ("UI", "font_size", str(self.font_size_spin.value())),
            ("UI", "enable_animation", str(self.animation_check.isChecked()).lower()),
            ("UI", "layout_mode", self.layout_mode_combo.currentText()),
            ("UI", "show_tray_icon", str(self.tray_icon_check.isChecked()).lower()),
            ("UI", "tray_behavior", self.tray_behavior_combo.currentText()),
            ("Backup", "backup_dir", self.backup_location_edit.text()),
            ("Backup", "auto_backup", str(self.auto_backup_check.isChecked()).lower()),
            ("Backup", "auto_backup_freq", self.auto_backup_combo.currentText()),
            ("Backup", "keep_count", str(self.keep_backup_spin.value())),
            ("File", "default_path", self.path_edit.text()),
            ("File", "default_encoding", self.encoding_combo.currentText()),
            ("Experience", "auto_remove_blank_lines", str(self.main_window.auto_remove_blank_lines).lower()),
            ("Experience", "auto_remove_extra_spaces", str(self.main_window.auto_remove_extra_spaces).lower()),
            ("Experience", "auto_remove_all_whitespace", str(self.main_window.auto_remove_all_whitespace).lower()),
            ("Experience", "skip_empty_cells", str(self.main_window.skip_empty_cells).lower()),
            ("App", "split_mode", str(self.main_window.split_mode)),
            ("App", "theme", self.theme_manager.current_theme),
        ]

        self.config_manager.batch_set_config(config_list, validate=False)
        self.main_window.apply_font(self.font_combo.currentFont().family(), str(self.font_size_spin.value()))
        self.do_post_updates()
        # 更新分隔模式和跳过空白单元格设置
        new_split_mode = self.split_combo.currentIndex()
        if hasattr(self.main_window, 'update_split_mode'):
            self.main_window.update_split_mode(new_split_mode)
        new_skip_empty = self.skip_empty_cells_check.isChecked()
        if hasattr(self.main_window, 'excel_widget') and hasattr(self.main_window.excel_widget, 'update_skip_empty_cells'):
            self.main_window.excel_widget.update_skip_empty_cells(new_skip_empty)
        self.accept()
        self.main_window.show_toast("设置已保存")

        # 强制刷新符号面板（如果存在）
        if self.main_window.symbol_panel:
            self.main_window.symbol_panel.load_custom_formulas()
            self.main_window.symbol_panel.load_disabled_default_formulas()
            self.main_window.symbol_panel.refresh_formula_list()
            self.main_window.symbol_panel.refresh_symbol_grid()

        # 刷新主窗口的符号按钮和符号数据
        self.main_window.all_symbols = self.main_window.build_all_symbols()
        self.main_window.render_symbol_buttons()
        self.main_window.reload_custom_symbol_buttons()

    def do_post_updates(self):
        # 使用 self._theme_changed 保存主题变化状态
        if hasattr(self, '_theme_changed') and self._theme_changed:
            self.main_window.apply_theme()
        # 提醒功能已移除，不再调用 _setup_reminder
        if hasattr(self.main_window, "apply_scale_factor"):
            self.main_window.apply_scale_factor(self.scale_combo.currentText())
        if hasattr(self.main_window, "apply_font"):
            self.main_window.apply_font(
                self.font_combo.currentFont().family(),
                str(self.font_size_spin.value())
            )
        if hasattr(self.main_window, "apply_animation"):
            self.main_window.apply_animation(self.animation_check.isChecked())
        if hasattr(self.main_window, "apply_layout_mode"):
            self.main_window.apply_layout_mode(self.layout_mode_combo.currentText())
        if hasattr(self.main_window, "apply_tray_behavior"):
            self.main_window.apply_tray_behavior(self.tray_behavior_combo.currentText())
        if hasattr(self.main_window, "update_tray_icon_visibility"):
            self.main_window.update_tray_icon_visibility()
        self.main_window.load_disabled_symbols()
        self.main_window.load_custom_symbols_into_list()
        if hasattr(self.main_window, "symbol_panel") and self.main_window.symbol_panel:
            self.main_window.symbol_panel.load_custom_formulas()
            self.main_window.symbol_panel.load_disabled_default_formulas()
            self.main_window.symbol_panel.refresh_symbol_grid()
            self.main_window.symbol_panel.refresh_formula_list()
        self.main_window.all_symbols = self.main_window.build_all_symbols()
        self.main_window.render_symbol_buttons()
        self.main_window._load_disabled_formulas()
