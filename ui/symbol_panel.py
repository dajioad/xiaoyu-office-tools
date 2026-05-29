# ui/symbol_panel.py
import json
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton,
    QLabel, QTextEdit, QApplication, QFrame, QListWidget,
    QListWidgetItem, QMessageBox, QDialog, QLineEdit, QScrollArea, QAbstractItemView
)
import qtawesome as qta


class SymbolPanel(QWidget):
    """现代化符号与公式助手面板，支持独立主题切换"""

    DEFAULT_FORMULAS = [
        ("求和", "=SUM(范围)"),
        ("条件判断", "=IF(条件, 真值, 假值)"),
        ("垂直查找", "=VLOOKUP(查找值, 表格, 列号, 匹配方式)"),
        ("返回指定位置的值", "=INDEX(数组, 行号, 列号)"),
        ("查找位置", "=MATCH(查找值, 范围, 匹配类型)"),
        ("条件计数", "=COUNTIF(范围, 条件)"),
        ("条件求和", "=SUMIF(范围, 条件, 求和范围)"),
        ("平均值", "=AVERAGE(范围)"),
        ("最大值", "=MAX(范围)"),
        ("最小值", "=MIN(范围)"),
        ("文本合并", "=CONCATENATE(文本1, 文本2)"),
        ("左侧截取", "=LEFT(文本, 字符数)"),
        ("右侧截取", "=RIGHT(文本, 字符数)"),
        ("中间截取", "=MID(文本, 起始位置, 字符数)"),
        ("文本长度", "=LEN(文本)"),
        ("去除空格", "=TRIM(文本)"),
        ("四舍五入", "=ROUND(数值, 小数位数)"),
        ("当前日期", "=TODAY()"),
        ("当前时间", "=NOW()"),
        ("格式化数字", "=TEXT(数值, 格式)"),
    ]

    def __init__(self, main_window):
        super().__init__(None)
        self.main_window = main_window
        self.config_manager = main_window.config_manager if main_window else None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(720, 600)
        self.setMinimumSize(620, 520)

        # 状态变量
        self.current_position = None
        self.last_symbol_left = None
        self.last_symbol_right = None
        self.current_symbol_key = None
        self.drag_pos = None

        # 撤销/重做栈
        self.undo_stack = []
        self.redo_stack = []

        # 公式模板管理
        self.custom_formulas = []
        self.disabled_default_formulas = []

        # 面板自身主题（独立于主窗口）
        self.current_theme = "light"
        self.load_panel_theme()

        self.init_ui()
        self.load_custom_formulas()
        self.load_disabled_default_formulas()
        self.refresh_formula_list()
        self.apply_panel_theme()
        self.hide()

    # ==================== UI 构建 ====================
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # 标题栏（可拖动）
        title_frame = QFrame()
        title_frame.setObjectName("title_frame")
        title_frame.setFixedHeight(45)
        title_frame.setCursor(Qt.SizeAllCursor)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 0, 15, 0)

        # 标题图标
        title_icon = qta.icon('fa5s.square-root-alt', color='#409eff')
        title_icon_label = QLabel()
        title_icon_label.setPixmap(title_icon.pixmap(22, 22))
        title_layout.addWidget(title_icon_label)
        title_label = QLabel("符号与公式助手")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-left: 5px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 主题切换按钮（内置）
        self.theme_toggle_btn = QPushButton()
        self.theme_toggle_btn.setFixedSize(32, 32)
        self.theme_toggle_btn.setCursor(Qt.PointingHandCursor)
        self.theme_toggle_btn.setToolTip("切换主题")
        self.theme_toggle_btn.clicked.connect(self.toggle_panel_theme)
        title_layout.addWidget(self.theme_toggle_btn)

        # 最小化按钮
        minimize_btn = QPushButton()
        minimize_btn.setIcon(qta.icon('fa5s.minus', color='#909399'))
        minimize_btn.setIconSize(QSize(18, 18))
        minimize_btn.setFixedSize(32, 32)
        minimize_btn.setCursor(Qt.PointingHandCursor)
        minimize_btn.setToolTip("最小化")
        minimize_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(minimize_btn)

        # 关闭按钮
        close_btn = QPushButton()
        close_btn.setIcon(qta.icon('fa5s.times', color='#909399'))
        close_btn.setIconSize(QSize(18, 18))
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip("关闭 (ESC)")
        close_btn.clicked.connect(self.hide)
        title_layout.addWidget(close_btn)

        main_layout.addWidget(title_frame)

        # 标题栏拖动事件
        title_frame.mousePressEvent = self.title_mouse_press
        title_frame.mouseMoveEvent = self.title_mouse_move
        title_frame.mouseReleaseEvent = self.title_mouse_release

        # ---------- 左右分栏 ----------
        content = QHBoxLayout()
        content.setSpacing(18)

        # ===== 左侧：公式模板 =====
        left = QWidget()
        left.setFixedWidth(120)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        formula_title_layout = QHBoxLayout()
        formula_icon = qta.icon('fa5s.book', color='#606266')
        formula_icon_label = QLabel()
        formula_icon_label.setPixmap(formula_icon.pixmap(18, 18))
        formula_title_layout.addWidget(formula_icon_label)
        formula_title_layout.addWidget(QLabel("公式模板"))
        left_layout.addLayout(formula_title_layout)

        self.formula_list = QListWidget()
        self.formula_list.setWordWrap(True)
        self.formula_list.setSpacing(4)
        self.formula_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.formula_list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        left_layout.addWidget(self.formula_list, stretch=1)

        # ===== 右侧：核心操作区 =====
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(14)

        # 输入区域
        input_header = QHBoxLayout()
        input_icon = qta.icon('fa5s.edit', color='#606266')
        input_icon_label = QLabel()
        input_icon_label.setPixmap(input_icon.pixmap(18, 18))
        input_header.addWidget(input_icon_label)
        input_header.addWidget(QLabel("输入文本"))
        input_header.addStretch()

        self.clear_btn = QPushButton("清空")
        self.clear_btn.setIcon(qta.icon('fa5s.eraser', color='#606266'))
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_input_text)
        input_header.addWidget(self.clear_btn)

        self.copy_btn = QPushButton("复制")
        self.copy_btn.setIcon(qta.icon('fa5s.copy', color='#606266'))
        self.copy_btn.setCursor(Qt.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_input_text)
        input_header.addWidget(self.copy_btn)

        # 撤销按钮
        self.undo_btn = QPushButton()
        self.undo_btn.setIcon(qta.icon('fa5s.undo', color='#606266'))
        self.undo_btn.setIconSize(QSize(18, 18))
        self.undo_btn.setFixedSize(32, 32)
        self.undo_btn.setCursor(Qt.PointingHandCursor)
        self.undo_btn.setToolTip("撤销")
        self.undo_btn.clicked.connect(self.undo)
        input_header.addWidget(self.undo_btn)

        # 重做按钮
        self.redo_btn = QPushButton()
        self.redo_btn.setIcon(qta.icon('fa5s.redo', color='#606266'))
        self.redo_btn.setIconSize(QSize(18, 18))
        self.redo_btn.setFixedSize(32, 32)
        self.redo_btn.setCursor(Qt.PointingHandCursor)
        self.redo_btn.setToolTip("重做")
        self.redo_btn.clicked.connect(self.redo)
        input_header.addWidget(self.redo_btn)

        right_layout.addLayout(input_header)

        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText(
            "在此输入文本或公式，可选中部分内容。\n"
            "⚠️ 必须先单击选中符号和插入方式，两者都高亮才能处理数据。"
        )
        self.input_text.setMaximumHeight(120)
        right_layout.addWidget(self.input_text)

        # 符号区
        symbol_header = QHBoxLayout()
        symbol_icon = qta.icon('fa5s.hashtag', color='#606266')
        symbol_icon_label = QLabel()
        symbol_icon_label.setPixmap(symbol_icon.pixmap(18, 18))
        symbol_header.addWidget(symbol_icon_label)
        symbol_header.addWidget(QLabel("常用符号"))
        symbol_header.addStretch()

        self.lang_btn = QPushButton("中文符号")
        self.lang_btn.setIcon(qta.icon('fa5s.language', color='#606266'))
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self.toggle_language)
        symbol_header.addWidget(self.lang_btn)

        right_layout.addLayout(symbol_header)

        # 符号滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.symbol_grid_widget = QWidget()
        self.symbol_grid = QGridLayout(self.symbol_grid_widget)
        self.symbol_grid.setSpacing(12)
        self.symbol_grid.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.symbol_grid_widget)
        right_layout.addWidget(scroll, stretch=1)

        # 插入方式
        pos_header = QHBoxLayout()
        pos_icon = qta.icon('fa5s.location-arrow', color='#606266')
        pos_icon_label = QLabel()
        pos_icon_label.setPixmap(pos_icon.pixmap(18, 18))
        pos_header.addWidget(pos_icon_label)
        pos_header.addWidget(QLabel("插入方式"))
        pos_header.addStretch()
        right_layout.addLayout(pos_header)

        pos_btn_layout = QHBoxLayout()
        pos_btn_layout.setSpacing(12)
        self.pos_buttons = {}
        positions = [
            ("头部", "head", "在文本前添加符号"),
            ("尾部", "tail", "在文本后添加符号"),
            ("两端", "both", "在文本两端包裹符号"),
            ("分隔", "split", "在每个字符之间插入符号")
        ]
        for name, key, tip in positions:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tip)
            btn.clicked.connect(lambda _, k=key: self.toggle_position(k))
            pos_btn_layout.addWidget(btn)
            self.pos_buttons[key] = btn
        right_layout.addLayout(pos_btn_layout)

        # 输出按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self.apply_selected_btn = QPushButton(" 选中输出")
        self.apply_selected_btn.setIcon(qta.icon('fa5s.i-cursor', color='white'))
        self.apply_selected_btn.clicked.connect(self.apply_to_selected)
        btn_row.addWidget(self.apply_selected_btn)

        self.apply_all_btn = QPushButton(" 全部输出")
        self.apply_all_btn.setIcon(qta.icon('fa5s.file-alt', color='white'))
        self.apply_all_btn.clicked.connect(self.apply_to_all)
        btn_row.addWidget(self.apply_all_btn)

        right_layout.addLayout(btn_row)

        content.addWidget(left, stretch=0)
        content.addWidget(right, stretch=1)
        main_layout.addLayout(content)

        # 连接公式双击信号
        self.formula_list.itemDoubleClicked.connect(self.on_formula_clicked)
        self.refresh_symbol_grid()

    # ==================== 主题管理 ====================
    def load_panel_theme(self):
        if self.config_manager:
            theme = self.config_manager.get_config("SymbolPanel", "theme", "light")
            self.current_theme = theme if theme in ["light", "dark"] else "light"
        else:
            self.current_theme = "light"

    def save_panel_theme(self):
        if self.config_manager:
            self.config_manager.set_config("SymbolPanel", "theme", self.current_theme)

    def apply_panel_theme(self):
        """根据当前主题应用样式表"""
        if self.current_theme == "light":
            self.setStyleSheet("""
                QWidget {
                    background: rgba(255, 255, 255, 0.96);
                    border-radius: 16px;
                    border: 1px solid #e4e7ed;
                }
                QPushButton {
                    background: white;
                    border: 1px solid #dcdfe6;
                    border-radius: 8px;
                    padding: 8px;
                    color: #606266;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background: #ecf5ff;
                    border-color: #409eff;
                    color: #409eff;
                }
                QPushButton:checked {
                    background: #409eff;
                    color: white;
                    border-color: #409eff;
                }
                QListWidget {
                    background: white;
                    color: #1e293b;
                    border: 1px solid #e4e7ed;
                    border-radius: 8px;
                    padding: 4px;
                    font-size: 14px;
                    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                }
                QListWidget::item {
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    min-height: 28px;
                }
                QListWidget::item:selected {
                    background: #409eff;
                    color: white;
                }
                QListWidget::item:hover {
                    background: #ecf5ff;
                    color: #409eff;
                }
                QTextEdit {
                    background: white;
                    color: #1e293b;
                    border: 1px solid #dcdfe6;
                    border-radius: 8px;
                    font-size: 14px;
                    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                    padding: 8px;
                }
                QTextEdit:focus {
                    border-color: #409eff;
                    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
                }
                QLabel {
                    color: #2c3e50;
                }
                QFrame#title_frame {
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 10px;
                }
                QScrollArea {
                    background: transparent;
                    border: none;
                }
            """)
            self.theme_toggle_btn.setIcon(qta.icon('fa5s.moon', color='#606266'))
            self.theme_toggle_btn.setToolTip("切换到深色模式")
        else:
            self.setStyleSheet("""
                QWidget {
                    background: rgba(30, 41, 59, 0.96);
                    border-radius: 16px;
                    border: 1px solid #475569;
                }
                QPushButton {
                    background: #334155;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    padding: 8px;
                    color: #f1f5f9;
                    font-size: 13px;
                    transition: all 0.2s;
                }
                QPushButton:hover {
                    background: #60a5fa;
                    border-color: #60a5fa;
                    color: white;
                    box-shadow: 0 2px 8px rgba(96, 165, 250, 0.3);
                }
                QPushButton:checked {
                    background: #60a5fa;
                    color: white;
                    border-color: #60a5fa;
                    box-shadow: 0 0 12px rgba(96, 165, 250, 0.4);
                }
                QListWidget {
                    background: #334155;
                    color: #f8fafc;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    padding: 4px;
                    font-size: 14px;
                    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                }
                QListWidget::item {
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 2px;
                    min-height: 28px;
                    color: #f1f5f9;
                }
                QListWidget::item:selected {
                    background: #3b82f6;
                    color: white;
                }
                QListWidget::item:hover {
                    background: #475569;
                    color: #93c5fd;
                }
                QTextEdit {
                    background: #1e293b;
                    color: #e2e8f0;
                    border: 1px solid #475569;
                    border-radius: 8px;
                    font-size: 14px;
                    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
                    padding: 8px;
                }
                QTextEdit:focus {
                    border-color: #60a5fa;
                    box-shadow: 0 0 0 2px rgba(96, 165, 250, 0.25);
                }
                QLabel {
                    color: #f1f5f9;
                }
                QFrame#title_frame {
                    background: rgba(30, 41, 59, 0.9);
                    border-radius: 10px;
                }
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    width: 10px;
                    background: transparent;
                    margin: 4px;
                }
                QScrollBar::handle:vertical {
                    background: #475569;
                    border-radius: 5px;
                    min-height: 40px;
                    margin: 2px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #60a5fa;
                }
                QScrollBar:horizontal {
                    height: 10px;
                    background: transparent;
                    margin: 4px;
                }
                QScrollBar::handle:horizontal {
                    background: #475569;
                    border-radius: 5px;
                    min-width: 40px;
                    margin: 2px;
                }
                QScrollBar::handle:horizontal:hover {
                    background: #60a5fa;
                }
            """)
            self.theme_toggle_btn.setIcon(qta.icon('fa5s.sun', color='#fbbf24'))
            self.theme_toggle_btn.setToolTip("切换到浅色模式")

    def toggle_panel_theme(self):
        """切换面板自身主题"""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_panel_theme()
        self.apply_panel_theme()
        # 通知主窗口更新托盘图标
        if self.main_window and hasattr(self.main_window, 'update_dark_mode_action_icon'):
            self.main_window.update_dark_mode_action_icon()

    # ==================== 公式模板管理 ====================
    def load_custom_formulas(self):
        if not self.config_manager:
            self.custom_formulas = []
        else:
            s = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
            self.custom_formulas = [tuple(f.split('|')) for f in s.split(';;') if f] if s else []

    def save_custom_formulas(self):
        if self.config_manager:
            s = ";;".join([f"{a}|{b}" for a, b in self.custom_formulas])
            self.config_manager.set_config("SymbolPanel", "custom_formulas", s)

    def load_disabled_default_formulas(self):
        if not self.config_manager:
            self.disabled_default_formulas = []
        else:
            s = self.config_manager.get_config("SymbolPanel", "disabled_default_formulas", "[]")
            try:
                self.disabled_default_formulas = json.loads(s)
            except:
                self.disabled_default_formulas = []
            if not isinstance(self.disabled_default_formulas, list):
                self.disabled_default_formulas = []

    def save_disabled_default_formulas(self):
        if self.config_manager:
            s = json.dumps(self.disabled_default_formulas)
            self.config_manager.set_config("SymbolPanel", "disabled_default_formulas", s)

    def refresh_formula_list(self, filter_text=""):
        """刷新公式列表，UserRole 存储公式内容，UserRole+1 存储元数据"""
        self.formula_list.clear()
        
        # 1. 重新加载自定义公式（已有）
        custom_formulas_str = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
        self.custom_formulas = [tuple(f.split('|')) for f in custom_formulas_str.split(';;') if f] if custom_formulas_str else []
        
        # 2. 重新加载禁用列表
        disabled_str = self.config_manager.get_config("SymbolPanel", "disabled_default_formulas", "[]")
        try:
            self.disabled_default_formulas = json.loads(disabled_str)
        except:
            self.disabled_default_formulas = []
        
        # 3. 重新加载默认公式的覆盖配置（custom_defaults）
        custom_defaults_str = self.config_manager.get_config("Formulas", "custom_defaults", "{}")
        try:
            custom_defaults_data = json.loads(custom_defaults_str)
        except:
            custom_defaults_data = {}
        
        # 4. 添加默认公式（应用覆盖和禁用）
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
            # 去掉前面的 "✓ "，只显示名称和内容
            item_text = f"{name}: {value}"
            if filter_text:
                if filter_text.lower() not in name.lower() and filter_text.lower() not in value.lower():
                    continue
            item = QListWidgetItem(item_text)
            # 不设置 sizeHint，让 QListWidget 根据内容自动计算高度
            # UserRole 保存公式内容（用于插入）
            item.setData(Qt.UserRole, value)
            # UserRole+1 保存元数据（类型，键，显示名称）
            item.setData(Qt.UserRole + 1, ("default", default_name, name))
            self.formula_list.addItem(item)
        
        # 5. 添加自定义公式
        for name, value in self.custom_formulas:
            item_text = f"{name}: {value}"
            if filter_text:
                if filter_text.lower() not in name.lower() and filter_text.lower() not in value.lower():
                    continue
            item = QListWidgetItem(item_text)
            # 不设置 sizeHint，让 QListWidget 根据内容自动计算高度
            item.setData(Qt.UserRole, value)
            item.setData(Qt.UserRole + 1, ("custom", name, value))
            self.formula_list.addItem(item)

    def manage_formulas(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("管理公式模板")
        dlg.setMinimumSize(400, 400)
        lay = QVBoxLayout(dlg)
        lw = QListWidget()

        def ref():
            lw.clear()
            for disp, ins in self.DEFAULT_FORMULAS:
                if disp in self.disabled_default_formulas:
                    text = f"🔒 {disp} → {ins} (已禁用)"
                else:
                    text = f"{disp} → {ins}"
                item = QListWidgetItem(text)
                # UserRole 保存公式内容，UserRole+1 保存元数据
                item.setData(Qt.UserRole, ins)
                item.setData(Qt.UserRole + 1, ("default", disp, disp, ins))
                lw.addItem(item)
            for disp, ins in self.custom_formulas:
                item = QListWidgetItem(f"✏️ {disp} → {ins}")
                item.setData(Qt.UserRole, ins)
                item.setData(Qt.UserRole + 1, ("custom", disp, ins))
                lw.addItem(item)
        ref()
        lay.addWidget(lw)

        # 添加自定义公式
        add_frame = QFrame()
        add_layout = QHBoxLayout(add_frame)
        add_layout.setContentsMargins(0, 0, 0, 0)
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("显示名称")
        value_edit = QLineEdit()
        value_edit.setPlaceholderText("公式内容")
        add_btn = QPushButton("添加")
        add_layout.addWidget(QLabel("名称:"))
        add_layout.addWidget(name_edit)
        add_layout.addWidget(QLabel("内容:"))
        add_layout.addWidget(value_edit)
        add_layout.addWidget(add_btn)
        lay.addWidget(add_frame)

        def add_formula():
            name = name_edit.text().strip()
            value = value_edit.text().strip()
            if not name or not value:
                QMessageBox.warning(dlg, "提示", "请填写完整")
                return
            for disp, _ in self.DEFAULT_FORMULAS:
                if disp == name:
                    QMessageBox.warning(dlg, "提示", "默认公式已存在此名称")
                    return
            for disp, _ in self.custom_formulas:
                if disp == name:
                    QMessageBox.warning(dlg, "提示", "自定义公式已存在此名称")
                    return
            self.custom_formulas.append((name, value))
            self.save_custom_formulas()
            self.refresh_formula_list()
            ref()
            name_edit.clear()
            value_edit.clear()
            QMessageBox.information(dlg, "成功", "已添加")
        add_btn.clicked.connect(add_formula)

        # 删除/禁用选中的公式
        delete_btn = QPushButton("删除/禁用选中")
        lay.addWidget(delete_btn)

        def delete_or_disable():
            cur = lw.currentItem()
            if not cur:
                return
            data = cur.data(Qt.UserRole + 1)  # 获取元数据
            if not data:
                return
            typ = data[0]
            if typ == "default":
                disp = data[1]
                if disp not in self.disabled_default_formulas:
                    self.disabled_default_formulas.append(disp)
                    self.save_disabled_default_formulas()
                    self.refresh_formula_list()
                    ref()
                    QMessageBox.information(dlg, "成功", f"已禁用默认公式「{disp}」")
                else:
                    QMessageBox.information(dlg, "提示", "该公式已被禁用")
            else:
                disp = data[1]
                self.custom_formulas = [f for f in self.custom_formulas if f[0] != disp]
                self.save_custom_formulas()
                self.refresh_formula_list()
                ref()
                QMessageBox.information(dlg, "成功", f"已删除自定义公式「{disp}」")
        delete_btn.clicked.connect(delete_or_disable)

        # 重置默认公式
        reset_btn = QPushButton("重置所有默认公式")
        lay.addWidget(reset_btn)

        def reset_defaults():
            if self.disabled_default_formulas:
                self.disabled_default_formulas.clear()
                self.save_disabled_default_formulas()
                self.refresh_formula_list()
                ref()
                QMessageBox.information(dlg, "成功", "已恢复所有默认公式")
            else:
                QMessageBox.information(dlg, "提示", "没有禁用的默认公式")
        reset_btn.clicked.connect(reset_defaults)

        dlg.exec()

    def on_formula_clicked(self, item):
        formula_text = item.data(Qt.UserRole)  # 现在是一个字符串
        if not isinstance(formula_text, str):
            # 兼容旧数据，尝试从元组中提取公式
            if isinstance(formula_text, tuple) and len(formula_text) >= 2:
                formula_text = formula_text[-1]
            else:
                return
        cursor = self.input_text.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        cursor.insertText(formula_text)
        self.input_text.setFocus()
        self.show_msg(f"已插入公式：{formula_text}")

    # ==================== 符号和插入方式交互 ====================
    def refresh_symbol_grid(self):
        try:
            if not self.main_window:
                return
            cfg = self.main_window.get_symbol_config()
            # 安全清理旧控件
            for i in reversed(range(self.symbol_grid.count())):
                item = self.symbol_grid.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    widget.deleteLater()
                    self.symbol_grid.removeWidget(widget)
            row, col = 0, 0
            max_col = 4
            self.symbol_buttons = {}
            for sym_key, (left, right, name, chinese_name) in cfg.items():
                # 转义 & 符号
                display_text = name.replace("&", "&&")
                btn = QPushButton(display_text)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setToolTip(f"{chinese_name} ({left}...{right})")
                btn.setCheckable(True)
                btn.clicked.connect(lambda checked, k=sym_key, l=left, r=right: self.toggle_symbol(k, l, r))
                self.symbol_grid.addWidget(btn, row, col)
                self.symbol_buttons[sym_key] = btn
                col += 1
                if col >= max_col:
                    col = 0
                    row += 1
        except Exception as e:
            print(f"刷新符号面板异常: {e}")

    def toggle_symbol(self, sym_key, left, right):
        if self.current_symbol_key == sym_key:
            self.current_symbol_key = None
            self.last_symbol_left = None
            self.last_symbol_right = None
            self.symbol_buttons[sym_key].setChecked(False)
            self.show_msg("已取消符号选择")
        else:
            if self.current_symbol_key is not None:
                self.symbol_buttons[self.current_symbol_key].setChecked(False)
            self.current_symbol_key = sym_key
            self.last_symbol_left = left
            self.last_symbol_right = right
            self.symbol_buttons[sym_key].setChecked(True)
            self.show_msg(f"已选择符号：{self.symbol_buttons[sym_key].text()}")

    def toggle_position(self, key):
        if self.current_position == key:
            self.current_position = None
            self.pos_buttons[key].setChecked(False)
            self.show_msg("已取消插入方式选择")
        else:
            self.current_position = key
            for k, btn in self.pos_buttons.items():
                btn.setChecked(k == key)
            self.show_msg(f"已选择插入方式：{self.pos_buttons[key].text()}")

    def toggle_language(self):
        if self.main_window:
            self.main_window.toggle_symbol_language()
            self.refresh_symbol_grid()
            if self.main_window.text_processor.language == "zh":
                self.lang_btn.setText("中文符号")
            else:
                self.lang_btn.setText("英文符号")

    # ==================== 核心处理 ====================
    def _apply_to_text(self, text):
        if not self.last_symbol_left or not self.current_position:
            self.show_msg("⚠️ 请先选择符号和插入方式（两者都需高亮）")
            return None
        l = self.last_symbol_left or ""
        r = self.last_symbol_right or ""
        p = self.current_position

        if p == "head":
            return l + text
        elif p == "tail":
            return text + r
        elif p == "both":
            return l + text + r
        elif p == "split":
            pure = text.strip()
            if not pure:
                return text
            chars = list(pure)
            # 从主窗口获取最新的 split_mode
            split_mode = getattr(self.main_window, 'split_mode', 0)
            if split_mode == 0:
                return l.join(chars)
            elif split_mode == 1:
                return "".join([f"{l}{c}{r}" for c in chars])
            elif split_mode == 2:
                return ",".join([f"{l}{c}{r}" for c in chars])
            else:
                return l.join(chars) + r
        return text

    def apply_to_selected(self):
        cursor = self.input_text.textCursor()
        if not cursor.hasSelection():
            self.show_msg("请先选中要处理的文本")
            return
        selected = cursor.selectedText()
        if not selected:
            return
        
        # 保存当前状态到撤销栈
        self.save_undo_state()
        
        result = self._apply_to_text(selected)
        if result is not None:
            cursor.insertText(result)
            self.show_msg("已处理选中区域")

    def apply_to_all(self):
        txt = self.input_text.toPlainText()
        if not txt:
            self.show_msg("输入框为空")
            return
        
        # 保存当前状态到撤销栈
        self.save_undo_state()
        
        result = self._apply_to_text(txt)
        if result is not None:
            self.input_text.setText(result)
            QApplication.clipboard().setText(result)
            self.show_msg("已处理全部文本并复制到剪贴板")

    def save_undo_state(self):
        """保存当前文本状态到撤销栈"""
        current_text = self.input_text.toPlainText()
        if current_text:
            self.undo_stack.append(current_text)
            # 限制撤销栈大小
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
            # 每次新操作清空重做栈
            self.redo_stack = []

    def undo(self):
        """撤销操作"""
        if not self.undo_stack:
            self.show_msg("没有可撤销的操作")
            return
        
        # 保存当前状态到重做栈
        current_text = self.input_text.toPlainText()
        self.redo_stack.append(current_text)
        
        # 恢复上一个状态
        previous_text = self.undo_stack.pop()
        self.input_text.setText(previous_text)
        self.show_msg("已撤销")

    def redo(self):
        """重做操作"""
        if not self.redo_stack:
            self.show_msg("没有可重做的操作")
            return
        
        # 保存当前状态到撤销栈
        current_text = self.input_text.toPlainText()
        self.undo_stack.append(current_text)
        
        # 恢复下一个状态
        next_text = self.redo_stack.pop()
        self.input_text.setText(next_text)
        self.show_msg("已重做")

    def copy_input_text(self):
        t = self.input_text.toPlainText()
        if t:
            QApplication.clipboard().setText(t)
            self.show_msg("已复制")
        else:
            self.show_msg("输入框为空")

    def clear_input_text(self):
        # 保存当前状态到撤销栈
        self.save_undo_state()
        self.input_text.clear()
        self.show_msg("输入框已清空")

    def show_msg(self, msg):
        if self.main_window and hasattr(self.main_window, 'show_toast'):
            self.main_window.show_toast(msg)
        else:
            toast = QLabel(msg, self)
            toast.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
            toast.setStyleSheet("background:rgba(0,0,0,0.85);color:white;padding:10px;border-radius:8px;")
            toast.show()
            QTimer.singleShot(2000, toast.close)

    # ==================== 拖动逻辑 ====================
    def title_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            gp = event.globalPosition().toPoint() if hasattr(event, 'globalPosition') else event.globalPos()
            self.drag_pos = gp - self.frameGeometry().topLeft()
            event.accept()

    def title_mouse_move(self, event):
        if self.drag_pos and event.buttons() == Qt.LeftButton:
            gp = event.globalPosition().toPoint() if hasattr(event, 'globalPosition') else event.globalPos()
            new_pos = gp - self.drag_pos
            screen = QApplication.primaryScreen().availableGeometry()
            new_pos.setX(max(screen.left(), min(new_pos.x(), screen.right() - self.width())))
            new_pos.setY(max(screen.top(), min(new_pos.y(), screen.bottom() - self.height())))
            self.move(new_pos)
            event.accept()

    def title_mouse_release(self, event):
        self.drag_pos = None
        event.accept()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()
        else:
            super().keyPressEvent(e)
    
    def showEvent(self, event):
        """在面板显示时刷新最新配置"""
        try:
            super().showEvent(event)
            # 刷新配置，延迟一点时间避免卡顿
            QTimer.singleShot(50, self._refresh_on_show)
        except Exception as e:
            print(f"显示面板异常: {e}")
    
    def _refresh_on_show(self):
        print("=== _refresh_on_show called ===")
        custom_formulas_str = self.config_manager.get_config("SymbolPanel", "custom_formulas", "")
        print(f"custom_formulas from config: {custom_formulas_str}")
        self.load_custom_formulas()
        self.load_disabled_default_formulas()
        self.refresh_symbol_grid()
        self.refresh_formula_list()