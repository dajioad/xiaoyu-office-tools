# ui/guide.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect, QFrame, QSizePolicy, QTextEdit, QScrollArea
)
from PySide6.QtCore import Qt, QPoint, QTimer, QRect, QEvent, Signal
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
import shiboken6


class GuideOverlay(QWidget):
    guide_complete = Signal()
    guide_skipped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: transparent;")

        self.target_widget = None
        self.highlight_rect = QRect()
        self.arrow_direction = "bottom"
        self.steps = []
        self.current_idx = 0
        self.parent_window = parent

        self.card = QFrame(self)
        self.card.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)
        self.card.setAttribute(Qt.WA_StyledBackground, True)
        self.card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.card.setMinimumWidth(300)
        self.card.setMaximumWidth(500)

        self.apply_theme()

    def apply_theme(self):
        default_theme = {
            'bg': '#F5F7FA', 'card': '#FFFFFF', 'text': '#303133',
            'text_secondary': '#606266', 'border': '#dcdfe6',
            'primary': '#409eff', 'primary_light': '#66b1ff',
            'primary_dark': '#3088ff', 'shadow': 'rgba(0,0,0,0.05)'
        }

        theme = default_theme.copy()
        if self.parent_window and hasattr(self.parent_window, 'theme_manager'):
            try:
                parent_theme = self.parent_window.theme_manager.get_theme()
                theme.update(parent_theme)
            except:
                pass

        card_bg = theme.get('card', '#ffffff')
        border_color = theme.get('border', '#dcdfe6')
        text_color = theme.get('text', '#303133')
        text_secondary = theme.get('text_secondary', '#606266')
        primary = theme.get('primary', '#409eff')
        primary_light = theme.get('primary_light', '#66b1ff')
        bg_secondary = theme.get('bg_secondary', '#f5f7fa')
        text_placeholder = theme.get('text_placeholder', text_secondary)

        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: {card_bg};
                border-radius: 12px;
                border: 1px solid {border_color};
            }}
            QLabel#title {{
                font-size: 16px;
                font-weight: bold;
                color: {text_color};
            }}
            QLabel#desc {{
                font-size: 13px;
                color: {text_secondary};
                line-height: 1.5;
            }}
            QPushButton {{
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton#next {{
                background-color: {primary};
                color: white;
            }}
            QPushButton#next:hover {{ background-color: {primary_light}; }}
            QPushButton#prev {{
                background-color: {bg_secondary};
                color: {text_placeholder};
            }}
            QPushButton#prev:hover {{ background-color: {border_color}; }}
            QPushButton#skip {{
                background-color: transparent;
                color: {text_secondary};
            }}
            QPushButton#skip:hover {{ color: {primary}; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        card_layout.addWidget(self.title_label)

        self.desc_label = QLabel()
        self.desc_label.setObjectName("desc")
        self.desc_label.setWordWrap(True)
        self.desc_label.setMinimumWidth(260)
        card_layout.addWidget(self.desc_label)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        self.skip_btn = QPushButton("跳过引导")
        self.skip_btn.setObjectName("skip")
        self.prev_btn = QPushButton("上一步")
        self.prev_btn.setObjectName("prev")
        self.next_btn = QPushButton("下一步")
        self.next_btn.setObjectName("next")

        btn_layout.addWidget(self.skip_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.prev_btn)
        btn_layout.addWidget(self.next_btn)

        card_layout.addLayout(btn_layout)

        self.card.show()
        self.card.raise_()

        self.skip_btn.clicked.connect(self._on_skip)
        self.prev_btn.clicked.connect(self._on_prev)
        self.next_btn.clicked.connect(self._on_next)

        if self.parent_window:
            self.parent_window.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.parent_window and event.type() in (QEvent.Resize, QEvent.Move, QEvent.Show):
            QTimer.singleShot(10, self._update_geometry_and_position)
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        self._update_geometry_and_position()
        super().showEvent(event)

    def _update_geometry_and_position(self):
        if self.parent_window:
            self.setGeometry(self.parent_window.geometry())
            self.update_position()
            self.update()

    def set_steps(self, steps):
        self.steps = steps
        self.current_idx = 0
        self.show_step(0)

    def _is_widget_valid(self, widget):
        if widget is None:
            return False
        try:
            return shiboken6.isValid(widget) and widget.isVisible()
        except RuntimeError:
            return False

    def _ensure_widget_visible(self, widget):
        """确保目标控件在滚动区域内可见"""
        if not widget:
            return
        parent = widget.parent()
        while parent:
            if isinstance(parent, QScrollArea):
                parent.ensureWidgetVisible(widget)
                break
            parent = parent.parent()

    def show_step(self, idx):
        if idx < 0 or idx >= len(self.steps):
            return
        self.current_idx = idx
        step = self.steps[idx]
        self.title_label.setText(step.get("title", ""))
        self.desc_label.setText(step.get("desc", ""))
        self.target_widget = step.get("target_widget")
        self.arrow_direction = step.get("arrow", "bottom")

        self.card.adjustSize()

        widget_valid = False
        if self.target_widget is not None:
            try:
                widget_valid = shiboken6.isValid(self.target_widget) and self.target_widget.isVisible()
            except (RuntimeError, AttributeError):
                widget_valid = False

        if not widget_valid:
            QTimer.singleShot(300, self.update_position)
        else:
            # 确保控件在视口内
            self._ensure_widget_visible(self.target_widget)
            self.update_position()
        self.update()

        self.prev_btn.setVisible(idx > 0)
        self.next_btn.setText("完成" if idx == len(self.steps)-1 else "下一步")
        self.skip_btn.setVisible(idx < len(self.steps)-1)

    def update_position(self):
        if not self._is_widget_valid(self.target_widget):
            if self.parent_window:
                parent_rect = self.parent_window.rect()
                card_size = self.card.sizeHint()
                self.card.move(
                    (parent_rect.width() - card_size.width()) // 2,
                    (parent_rect.height() - card_size.height()) // 2
                )
                self.highlight_rect = QRect()
            return

        global_rect = self.target_widget.geometry()
        global_top_left = self.target_widget.mapToGlobal(QPoint(0, 0))
        global_rect.moveTopLeft(global_top_left)

        local_rect = QRect(self.mapFromGlobal(global_top_left), global_rect.size())
        self.highlight_rect = local_rect

        card_size = self.card.sizeHint()
        card_w = card_size.width()
        card_h = card_size.height()
        margin = 10
        parent_rect = self.parent_window.rect()

        def try_direction(direction):
            if direction == "bottom":
                y = global_rect.bottom() + margin
                if y + card_h <= parent_rect.height():
                    x = global_rect.center().x() - card_w // 2
                    x = max(margin, min(x, parent_rect.width() - card_w - margin))
                    return QPoint(x, y)
            elif direction == "top":
                y = global_rect.top() - card_h - margin
                if y >= 0:
                    x = global_rect.center().x() - card_w // 2
                    x = max(margin, min(x, parent_rect.width() - card_w - margin))
                    return QPoint(x, y)
            elif direction == "left":
                x = global_rect.left() - card_w - margin
                if x >= 0:
                    y = global_rect.center().y() - card_h // 2
                    y = max(margin, min(y, parent_rect.height() - card_h - margin))
                    return QPoint(x, y)
            elif direction == "right":
                x = global_rect.right() + margin
                if x + card_w <= parent_rect.width():
                    y = global_rect.center().y() - card_h // 2
                    y = max(margin, min(y, parent_rect.height() - card_h - margin))
                    return QPoint(x, y)
            return None

        priority_order = [self.arrow_direction]
        if self.arrow_direction == "left":
            priority_order.extend(["top", "bottom", "right"])
        elif self.arrow_direction == "right":
            priority_order.extend(["top", "bottom", "left"])
        elif self.arrow_direction == "top":
            priority_order.extend(["left", "right", "bottom"])
        else:
            priority_order.extend(["left", "right", "top"])

        for direction in priority_order:
            pos = try_direction(direction)
            if pos is not None:
                self.card.move(pos)
                return

        self.card.move(
            (parent_rect.width() - card_w) // 2,
            (parent_rect.height() - card_h) // 2
        )

    def paintEvent(self, event):
        if self.highlight_rect.isNull():
            painter = QPainter(self)
            painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())
            painter.end()
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        path = QPainterPath()
        path.addRoundedRect(self.highlight_rect, 8, 8)
        painter.fillPath(path, QBrush(Qt.transparent))

        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.setPen(QPen(QColor("#3b82f6"), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(self.highlight_rect, 8, 8)

        painter.setPen(QPen(QColor("#60a5fa"), 1))
        outer_rect = self.highlight_rect.adjusted(-2, -2, 2, 2)
        painter.drawRoundedRect(outer_rect, 10, 10)

        painter.end()

    def _on_next(self):
        if self.current_idx >= len(self.steps) - 1:
            self.guide_complete.emit()
            self.close()
        else:
            self.show_step(self.current_idx + 1)

    def _on_prev(self):
        if self.current_idx > 0:
            self.show_step(self.current_idx - 1)

    def _on_skip(self):
        self.guide_skipped.emit()
        self.close()

    def closeEvent(self, event):
        if self.parent_window:
            try:
                self.parent_window.removeEventFilter(self)
            except:
                pass
        try:
            if self.card:
                self.card.hide()
                self.card.deleteLater()
        except:
            pass
        super().closeEvent(event)


class GuideManager:
    def __init__(self, config_manager, parent):
        self.config = config_manager
        self.parent = parent
        self.overlay = None

    def should_show_guide(self, tab_index=None):
        if tab_index is None:
            return self.config.get_config("App", "guide_shown", "false") != "true"
        else:
            key = f"guide_{tab_index}"
            return self.config.get_config("Guide", key, "false") != "true"

    def mark_guide_done(self, tab_index=None):
        if tab_index is None:
            self.config.set_config("App", "guide_shown", "true")
        else:
            key = f"guide_{tab_index}"
            self.config.set_config("Guide", key, "true")

    def reset_guide(self, tab_index=None):
        if tab_index is None:
            self.config.set_config("App", "guide_shown", "false")
            for i in range(6):
                self.config.set_config("Guide", f"guide_{i}", "false")
            self.config.set_config("Guide", "guide_symbol_panel", "false")
        else:
            key = f"guide_{tab_index}"
            self.config.set_config("Guide", key, "false")

    def show_guide(self, tab_index=None):
        if tab_index is None:
            tab_index = self.parent.tab_widget.currentIndex()
        self.show_guide_for_tab(tab_index)

    def show_guide_for_tab(self, tab_index, retry_count=0):
        if self.overlay is not None:
            return
        if not self.should_show_guide(tab_index):
            return

        # 符号处理标签页特殊处理：如果没有符号按钮则提示并跳过
        if tab_index == 0:
            if not hasattr(self.parent, 'symbol_buttons') or not self.parent.symbol_buttons:
                if retry_count < 3:
                    QTimer.singleShot(300, lambda: self.show_guide_for_tab(tab_index, retry_count + 1))
                else:
                    self.parent.show_toast("⚠️ 未找到符号按钮，请先在设置中恢复默认符号或添加自定义符号")
                    self.mark_guide_done(tab_index)
                return
            has_visible = any(btn.isVisible() for btn in self.parent.symbol_buttons.values())
            if not has_visible:
                self.parent.show_toast("⚠️ 所有符号已被隐藏，请先在设置中恢复默认符号")
                self.mark_guide_done(tab_index)
                return
        
        # Excel表格编辑标签页：等待懒加载完成
        elif tab_index == 1:
            if not hasattr(self.parent, 'excel_widget') or self.parent.excel_widget is None:
                if retry_count < 5:
                    QTimer.singleShot(300, lambda: self.show_guide_for_tab(tab_index, retry_count + 1))
                else:
                    self.mark_guide_done(tab_index)
                return
        
        # 文本处理标签页：等待懒加载完成
        elif tab_index == 2:
            if not hasattr(self.parent, 'word_widget') or self.parent.word_widget is None:
                if retry_count < 5:
                    QTimer.singleShot(300, lambda: self.show_guide_for_tab(tab_index, retry_count + 1))
                else:
                    self.mark_guide_done(tab_index)
                return
        
        # 工具箱标签页：等待懒加载完成
        elif tab_index == 3:
            if not hasattr(self.parent, 'toolbox_widget') or self.parent.toolbox_widget is None:
                if retry_count < 5:
                    QTimer.singleShot(300, lambda: self.show_guide_for_tab(tab_index, retry_count + 1))
                else:
                    self.mark_guide_done(tab_index)
                return

        steps = self._generate_steps_for_tab(tab_index)
        if steps:
            self._start(steps, tab_index)
        else:
            self.mark_guide_done(tab_index)

    def _generate_steps_for_tab(self, tab_index):
        steps = []
        # 符号处理标签页
        if tab_index == 0:
            if not hasattr(self.parent, 'input_text'):
                return []
            # 第二步：使用符号滚动区域而不是单个按钮（更稳定）
            symbol_scroll = getattr(self.parent, 'symbol_scroll', None)
            pos_btn = None
            if hasattr(self.parent, 'position_buttons'):
                pos_btn = self.parent.position_buttons.get("head")
            steps = [
                {"title": "📝 第一步：输入文本", "desc": "在左侧输入框中输入或粘贴需要处理的文本（例如：你好世界）",
                 "target_widget": self.parent.input_text, "arrow": "bottom"},
                {"title": "🔣 第二步：选择符号", "desc": "点击下方任意符号按钮（如「双引号」「书名号」等）",
                 "target_widget": symbol_scroll if symbol_scroll else self.parent.symbol_grid_widget, "arrow": "top"},
                {"title": "📍 第三步：选择插入方式", "desc": "选择「头部」「尾部」「两端」或「分隔」",
                 "target_widget": pos_btn, "arrow": "top"},
                {"title": "✅ 第四步：应用叠加", "desc": "点击「应用叠加」按钮，将当前符号效果添加到成品区",
                 "target_widget": getattr(self.parent, 'overlay_btn', None), "arrow": "top"},  # 改为 top 避免遮挡
                {"title": "📋 第五步：复制成品", "desc": "点击「复制成品」按钮，将最终结果复制到剪贴板",
                 "target_widget": getattr(self.parent, 'ui_final_result', None), "arrow": "bottom"},
            ]
        # Excel 表格编辑标签页
        elif tab_index == 1:
            if not hasattr(self.parent, 'excel_widget'):
                return []
            excel = self.parent.excel_widget
            if not hasattr(excel, 'file_btn') or not excel.file_btn:
                return []
            steps = [
                {"title": "📂 打开 Excel 文件", "desc": "点击「文件」按钮，选择「打开...」，即可导入 .xlsx 或 .xls 文件",
                 "target_widget": excel.file_btn, "arrow": "bottom"},
                {"title": "✏️ 编辑单元格", "desc": "双击任意单元格直接编辑内容，支持公式计算（Pro 版专属）",
                 "target_widget": excel.table, "arrow": "top"},
                {"title": "📌 冻结行", "desc": "选中某行，点击「冻结选中行」按钮，滚动时该行保持可见",
                 "target_widget": excel.btn_freeze_row, "arrow": "top"},
                {"title": "🔍 查找替换", "desc": "使用「查找替换」按钮快速搜索和替换单元格内容",
                 "target_widget": excel.btn_find, "arrow": "top"},
                {"title": "💾 保存修改", "desc": "编辑完成后点击「保存修改」按钮保存文件",
                 "target_widget": excel.btn_save, "arrow": "top"},
            ]
        # 文本处理标签页
        elif tab_index == 2:
            if not hasattr(self.parent, 'word_widget'):
                return []
            word = self.parent.word_widget
            toolbar = getattr(word, 'toolbar', None)
            # 查找替换按钮 - 从工具栏的 actions 中获取对应的控件
            find_btn_widget = None
            if toolbar:
                for action in toolbar.actions():
                    if action.text() == "查找替换":
                        btn_widget = toolbar.widgetForAction(action)
                        if btn_widget:
                            find_btn_widget = btn_widget
                            break
            # 菜单栏
            menubar = getattr(word, 'menubar', None)
            if not menubar:
                # 尝试从主窗口获取菜单栏
                menubar = self.parent.menuBar()
            steps = [
                {"title": "📄 文档编辑区", "desc": "这里可以输入和编辑文本内容，支持富文本格式",
                "target_widget": getattr(word, 'text_edit', None), "arrow": "bottom"},
                {"title": "🎨 工具栏", "desc": "提供格式设置功能：保存、加粗、斜体、颜色、对齐等",
                "target_widget": toolbar if toolbar else getattr(word, 'text_edit', None), "arrow": "bottom"},
                {"title": "🔍 查找替换", "desc": "点击「查找替换」按钮或按 Ctrl+F 搜索并替换文本",
                "target_widget": find_btn_widget if find_btn_widget else toolbar, "arrow": "left"},  # 改为 left 避免遮挡
                {"title": "📂 文件操作", "desc": "点击左上角「文件」菜单，可以打开或保存 .docx 文档",
                "target_widget": menubar if menubar else getattr(word, 'text_edit', None), "arrow": "bottom"},
            ]
        # 工具箱标签页 - 动态匹配卡片
        elif tab_index == 3:
            if not hasattr(self.parent, 'toolbox_widget'):
                return []
            toolbox = self.parent.toolbox_widget
            # 步骤标题与卡片标题的映射
            card_titles = {
                "📋 剪贴板历史": "剪贴板历史",
                "📁 批量文件处理": "批量文件处理",
                "🖼️ 图片工具": "图片工具",
                "📷 截图功能": "截图功能",
                "📊 OCR识别": "图片OCR",
                "📝 文本格式化": "文本格式化",
            }
            steps = []
            # 为每个功能单独生成步骤，避免所有步骤指向同一个卡片
            for step_title, target_title in card_titles.items():
                target_card = None
                if hasattr(toolbox, 'tool_cards'):
                    for card in toolbox.tool_cards:
                        # 查找卡片内的标题标签
                        for child in card.findChildren(QLabel):
                            if child.objectName() == "toolCardTitle" and child.text() == target_title:
                                target_card = card
                                break
                        if target_card:
                            break
                if target_card:
                    steps.append({
                        "title": step_title,
                        "desc": f"点击「{target_title}」卡片打开对应工具",
                        "target_widget": target_card,
                        "arrow": "bottom"
                    })
            if not steps:
                # 后备：使用第一个可见卡片
                first_card = None
                if hasattr(toolbox, 'tool_cards') and toolbox.tool_cards:
                    for card in toolbox.tool_cards:
                        if card and card.isVisible():
                            first_card = card
                            break
                if first_card:
                    steps = [{"title": "🧰 工具箱", "desc": "点击任意卡片使用工具", "target_widget": first_card, "arrow": "bottom"}]
        # 函数教程标签页
        elif tab_index == 4:
            if not hasattr(self.parent, 'tab_widget'):
                return []
            function_tab = self.parent.tab_widget.widget(4)
            if function_tab:
                text_edit = function_tab.findChild(QTextEdit)
                if text_edit:
                    steps = [{"title": "📖 函数教程", "desc": "查看常用 Excel 函数及示例", "target_widget": text_edit, "arrow": "top"}]
        # 问题解决标签页
        elif tab_index == 5:
            if not hasattr(self.parent, 'tab_widget'):
                return []
            problem_tab = self.parent.tab_widget.widget(5)
            if problem_tab:
                help_search = getattr(problem_tab, 'help_search', None)
                help_category_combo = getattr(problem_tab, 'help_category_combo', None)
                help_list_widget = getattr(problem_tab, 'help_list_widget', None)
                help_detail_content = getattr(problem_tab, 'help_detail_content', None)
                steps = [
                    {"title": "🔍 搜索功能", "desc": "输入关键词快速查找问题", "target_widget": help_search, "arrow": "bottom"},
                    {"title": "📂 分类筛选", "desc": "按类别筛选帮助条目", "target_widget": help_category_combo, "arrow": "bottom"},
                    {"title": "📋 选择条目", "desc": "点击左侧列表中的条目查看详情", "target_widget": help_list_widget, "arrow": "top"},
                    {"title": "📖 查看详情", "desc": "右侧显示完整帮助内容", "target_widget": help_detail_content, "arrow": "left"},
                ]
                steps = [s for s in steps if s["target_widget"] is not None]
        return steps

    def show_guide_for_symbol_panel(self, symbol_panel):
        if self.overlay is not None:
            return
        if not self.should_show_guide("symbol_panel"):
            return
        steps = self._generate_symbol_panel_steps(symbol_panel)
        if steps:
            self._start(steps, "symbol_panel", target_window=symbol_panel)

    def _generate_symbol_panel_steps(self, panel):
        steps = []
        if hasattr(panel, 'input_text') and panel.input_text:
            steps.append({
                "title": "📝 输入文本",
                "desc": "在左侧输入框中输入或粘贴需要处理的文本。",
                "target_widget": panel.input_text,
                "arrow": "bottom"
            })
        # 符号区域
        symbol_scroll = None
        if hasattr(panel, 'symbol_grid_widget'):
            # 获取符号区域的父滚动区域
            parent = panel.symbol_grid_widget.parent()
            while parent:
                if isinstance(parent, QScrollArea):
                    symbol_scroll = parent
                    break
                parent = parent.parent()
        if symbol_scroll:
            steps.append({
                "title": "🔣 选择符号",
                "desc": "点击任意符号按钮，例如「双引号」「书名号」等。",
                "target_widget": symbol_scroll,
                "arrow": "top"
            })
        pos_btn = None
        if hasattr(panel, 'pos_buttons') and panel.pos_buttons:
            for btn in panel.pos_buttons.values():
                if btn and btn.isVisible():
                    pos_btn = btn
                    break
        if pos_btn:
            steps.append({
                "title": "📍 选择插入方式",
                "desc": "选择「头部」「尾部」「两端」或「分隔」。",
                "target_widget": pos_btn,
                "arrow": "top"
            })
        if hasattr(panel, 'apply_all_btn') and panel.apply_all_btn:
            steps.append({
                "title": "✅ 全部输出",
                "desc": "点击「全部输出」按钮，将处理后的文本复制到剪贴板。",
                "target_widget": panel.apply_all_btn,
                "arrow": "right"
            })
        if steps:
            steps.append({
                "title": "🎉 引导完成",
                "desc": "您已学会使用符号面板。更多功能请探索右键菜单和公式模板。",
                "target_widget": panel,
                "arrow": "bottom"
            })
        return steps

    def _start(self, steps, tab_index=None, target_window=None):
        if self.overlay is not None:
            try:
                self.overlay.guide_complete.disconnect()
                self.overlay.guide_skipped.disconnect()
                self.overlay.close()
                self.overlay.deleteLater()
            except:
                pass
            self.overlay = None

        parent = target_window if target_window else self.parent
        self.overlay = GuideOverlay(parent)
        self.overlay.set_steps(steps)
        self.overlay.guide_complete.connect(lambda: self._done(tab_index))
        self.overlay.guide_skipped.connect(lambda: self._done(tab_index))
        self.overlay._update_geometry_and_position()
        self.overlay.show()
        self.overlay.raise_()

    def _done(self, tab_index):
        self.mark_guide_done(tab_index)
        if self.overlay:
            self.overlay.close()
            self.overlay.deleteLater()
            self.overlay = None

    def apply_theme(self):
        pass