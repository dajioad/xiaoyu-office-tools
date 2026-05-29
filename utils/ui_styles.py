"""
统一UI样式系统
提供一套完整的样式配置，用于整个应用的UI优化
"""

class ThemeColors:
    """主题颜色配置"""
    
    # 浅色主题
    LIGHT = {
        "primary": "#409EFF",
        "primary_hover": "#66B1FF",
        "primary_pressed": "#337ECC",
        "success": "#67C23A",
        "warning": "#E6A23C",
        "danger": "#F56C6C",
        "info": "#909399",
        "text_primary": "#303133",
        "text_secondary": "#606266",
        "text_hint": "#909399",
        "border": "#DCDFE6",
        "border_light": "#E4E7ED",
        "bg_page": "#F5F7FA",
        "bg_card": "#FFFFFF",
        "bg_hover": "#F5F7FA",
        "shadow": "0 2px 12px 0 rgba(0, 0, 0, 0.05)"
    }
    
    # 深色主题
    DARK = {
        "primary": "#60A5FA",
        "primary_hover": "#93C5FD",
        "primary_pressed": "#3B82F6",
        "success": "#34D399",
        "warning": "#FBBF24",
        "danger": "#F87171",
        "info": "#9CA3AF",
        "text_primary": "#F3F4F6",
        "text_secondary": "#D1D5DB",
        "text_hint": "#9CA3AF",
        "border": "#374151",
        "border_light": "#4B5563",
        "bg_page": "#0F172A",
        "bg_card": "#1E293B",
        "bg_hover": "#334155",
        "shadow": "0 2px 12px 0 rgba(0, 0, 0, 0.3)"
    }


class UIStyleSystem:
    """统一的UI样式系统 - 支持浅色/深色主题"""
    
    # 当前主题（默认浅色）
    current_theme = "light"
    
    # 全局间距配置
    SPACING = {
        "xs": 4,
        "sm": 8,
        "md": 12,
        "lg": 16,
        "xl": 24,
        "xxl": 32
    }
    
    # 圆角配置
    BORDER_RADIUS = {
        "sm": 4,
        "md": 8,
        "lg": 12,
        "xl": 16,
        "circle": 999
    }
    
    # 字体配置
    FONTS = {
        "family": "Microsoft YaHei, 微软雅黑, Arial, sans-serif",
        "size_xs": 12,
        "size_sm": 13,
        "size_md": 14,
        "size_lg": 16,
        "size_xl": 18,
        "size_xxl": 20
    }
    
    @classmethod
    def get_colors(cls):
        """获取当前主题的颜色配置"""
        if cls.current_theme == "dark":
            return ThemeColors.DARK
        return ThemeColors.LIGHT
    
    @classmethod
    def set_theme(cls, theme_name):
        """设置主题"""
        if theme_name in ["light", "dark"]:
            cls.current_theme = theme_name
    
    # 按钮样式
    @classmethod
    def get_button_style(cls, style_type="primary"):
        """获取按钮样式"""
        colors = cls.get_colors()
        styles = {
            "primary": f"""
                QPushButton {{
                    background: {colors['primary']};
                    color: white;
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['lg']}px;
                    font-size: {cls.FONTS['size_md']}px;
                    font-family: {cls.FONTS['family']};
                }}
                QPushButton:hover {{
                    background: {colors['primary_hover']};
                }}
                QPushButton:pressed {{
                    background: {colors['primary_pressed']};
                }}
                QPushButton:disabled {{
                    background: {colors['text_hint']};
                }}
            """,
            "default": f"""
                QPushButton {{
                    background: {colors['bg_card']};
                    color: {colors['text_primary']};
                    border: 1px solid {colors['border']};
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['lg']}px;
                    font-size: {cls.FONTS['size_md']}px;
                    font-family: {cls.FONTS['family']};
                }}
                QPushButton:hover {{
                    border-color: {colors['primary']};
                    color: {colors['primary']};
                }}
                QPushButton:pressed {{
                    background: {colors['bg_hover']};
                }}
            """,
            "text": f"""
                QPushButton {{
                    background: transparent;
                    color: {colors['text_primary']};
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['sm']}px;
                    padding: {cls.SPACING['xs']}px {cls.SPACING['sm']}px;
                    font-size: {cls.FONTS['size_md']}px;
                }}
                QPushButton:hover {{
                    background: {colors['bg_hover']};
                }}
            """,
            "danger": f"""
                QPushButton {{
                    background: {colors['danger']};
                    color: white;
                    border: none;
                    border-radius: {cls.BORDER_RADIUS['md']}px;
                    padding: {cls.SPACING['sm']}px {cls.SPACING['lg']}px;
                    font-size: {cls.FONTS['size_md']}px;
                }}
                QPushButton:hover {{
                    background: {colors['danger']};
                    opacity: 0.8;
                }}
            """
        }
        return styles.get(style_type, styles["default"])
    
    # 输入框样式
    @classmethod
    def get_input_style(cls):
        """获取输入框样式"""
        colors = cls.get_colors()
        return f"""
            QLineEdit, QTextEdit {{
                background: {colors['bg_card']};
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_md']}px;
                font-family: {cls.FONTS['family']};
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
            QLineEdit:hover, QTextEdit:hover {{
                border-color: {colors['primary']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border-color: {colors['primary']};
            }}
            QTextEdit {{
                padding: {cls.SPACING['md']}px;
            }}
        """
    
    # 卡片样式
    @classmethod
    def get_card_style(cls):
        """获取卡片样式"""
        colors = cls.get_colors()
        return f"""
            QFrame[class="card"] {{
                background: {colors['bg_card']};
                border-radius: {cls.BORDER_RADIUS['lg']}px;
                border: 1px solid {colors['border_light']};
            }}
        """
    
    # 标签页样式
    @classmethod
    def get_tab_style(cls):
        """获取标签页样式"""
        colors = cls.get_colors()
        return f"""
            QTabWidget::pane {{
                border: 1px solid {colors['border_light']};
                background: {colors['bg_page']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {colors['text_secondary']};
                padding: {cls.SPACING['sm']}px {cls.SPACING['lg']}px;
                border: none;
                border-top-left-radius: {cls.BORDER_RADIUS['md']}px;
                border-top-right-radius: {cls.BORDER_RADIUS['md']}px;
                font-size: {cls.FONTS['size_md']}px;
                font-family: {cls.FONTS['family']};
                margin-right: 2px;
            }}
            QTabBar::tab:hover {{
                color: {colors['primary']};
                background: {colors['bg_hover']};
            }}
            QTabBar::tab:selected {{
                background: {colors['bg_card']};
                color: {colors['primary']};
                font-weight: 600;
            }}
        """
    
    # 组合框样式
    @classmethod
    def get_combo_style(cls):
        """获取下拉框样式"""
        colors = cls.get_colors()
        return f"""
            QComboBox {{
                background: {colors['bg_card']};
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_md']}px;
                min-height: 24px;
            }}
            QComboBox:hover {{
                border-color: {colors['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {colors['text_secondary']};
                width: 0;
                height: 0;
            }}
            QComboBox QAbstractItemView {{
                background: {colors['bg_card']};
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                padding: {cls.SPACING['xs']}px;
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
        """
    
    # 滚动条样式
    @classmethod
    def get_scrollbar_style(cls):
        """获取滚动条样式"""
        colors = cls.get_colors()
        return f"""
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['text_hint']};
                border-radius: 4px;
                min-height: 30px;
                margin: 0;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {colors['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 8px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {colors['text_hint']};
                border-radius: 4px;
                min-width: 30px;
                margin: 0;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {colors['text_secondary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """
    
    # 工具卡片样式
    @classmethod
    def get_tool_card_style(cls):
        """获取工具箱卡片样式"""
        colors = cls.get_colors()
        return f"""
            QFrame[class="tool-card"] {{
                background: {colors['bg_card']};
                border: 1px solid {colors['border_light']};
                border-radius: {cls.BORDER_RADIUS['lg']}px;
                padding: {cls.SPACING['xl']}px;
            }}
            QFrame[class="tool-card"]:hover {{
                border-color: {colors['primary']};
                background: {colors['bg_hover']};
            }}
        """
    
    # 标签样式
    @classmethod
    def get_label_style(cls, is_hint=False):
        """获取标签样式"""
        colors = cls.get_colors()
        if is_hint:
            return f"""
                QLabel {{
                    color: {colors['text_hint']};
                    font-size: {cls.FONTS['size_sm']}px;
                    font-family: {cls.FONTS['family']};
                }}
            """
        return f"""
            QLabel {{
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_md']}px;
                font-family: {cls.FONTS['family']};
            }}
        """
    
    # 分组框样式
    @classmethod
    def get_groupbox_style(cls):
        """获取分组框样式"""
        colors = cls.get_colors()
        return f"""
            QGroupBox {{
                border: 1px solid {colors['border_light']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                margin-top: {cls.SPACING['lg']}px;
                padding-top: {cls.SPACING['md']}px;
                font-weight: 600;
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_md']}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {cls.SPACING['lg']}px;
                padding: 0 {cls.SPACING['sm']}px;
            }}
        """
    
    # 列表样式
    @classmethod
    def get_list_style(cls):
        """获取列表控件样式"""
        colors = cls.get_colors()
        return f"""
            QListWidget {{
                background: {colors['bg_card']};
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                padding: {cls.SPACING['xs']}px;
                outline: none;
            }}
            QListWidget::item {{
                padding: {cls.SPACING['sm']}px {cls.SPACING['md']}px;
                border-radius: {cls.BORDER_RADIUS['sm']}px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background: {colors['primary']};
                color: white;
                font-weight: 600;
            }}
            QListWidget::item:hover:!selected {{
                background: {colors['bg_hover']};
            }}
        """
    
    # 侧边栏导航样式
    @classmethod
    def get_sidebar_style(cls):
        """获取侧边栏导航样式"""
        colors = cls.get_colors()
        return f"""
            QListWidget[class="sidebar"] {{
                background: {colors['bg_card']};
                border: none;
                border-radius: {cls.BORDER_RADIUS['lg']}px;
                padding: {cls.SPACING['sm']}px;
            }}
            QListWidget[class="sidebar"]::item {{
                padding: {cls.SPACING['md']}px {cls.SPACING['lg']}px;
                border-radius: {cls.BORDER_RADIUS['md']}px;
                margin: 2px 0;
                color: {colors['text_secondary']};
                font-size: {cls.FONTS['size_md']}px;
            }}
            QListWidget[class="sidebar"]::item:selected {{
                background: {colors['primary']};
                color: white;
                font-weight: 600;
            }}
            QListWidget[class="sidebar"]::item:hover:!selected {{
                background: {colors['bg_hover']};
                color: {colors['text_primary']};
            }}
        """
    
    # 弱化的删除按钮样式
    @classmethod
    def get_soft_danger_button_style(cls):
        """获取弱化的删除按钮样式"""
        colors = cls.get_colors()
        return f"""
            QPushButton {{
                background: {colors['bg_card']};
                color: {colors['danger']};
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['md']}px;
                padding: {cls.SPACING['sm']}px {cls.SPACING['lg']}px;
                font-size: {cls.FONTS['size_md']}px;
            }}
            QPushButton:hover {{
                background: {colors['danger']};
                color: white;
                border-color: {colors['danger']};
            }}
        """
    
    # PRO按钮立体风格样式
    @classmethod
    def get_pro_button_style(cls):
        """获取PRO按钮立体风格样式"""
        colors = cls.get_colors()
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:0.5 #FFC107, stop:1 #FF9800);
                color: #8B4513;
                border: 2px solid #DAA520;
                border-radius: {cls.BORDER_RADIUS['lg']}px;
                padding: {cls.SPACING['md']}px {cls.SPACING['xl']}px;
                font-size: {cls.FONTS['size_md']}px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFE066, stop:0.5 #FFD54F, stop:1 #FFB74D);
                color: #7B3B00;
                border-color: #B8860B;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #E6B800, stop:0.5 #D4A600, stop:1 #C29400);
            }}
        """
    
    # 全局样式表
    @classmethod
    def get_global_stylesheet(cls):
        """获取全局样式表"""
        colors = cls.get_colors()
        return f"""
            /* 全局基础样式 */
            * {{
                font-family: {cls.FONTS['family']};
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
            
            QMainWindow {{
                background: {colors['bg_page']};
            }}
            
            QWidget {{
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_md']}px;
            }}
            
            /* 提示标签 */
            QLabel[class="hint-label"] {{
                color: {colors['text_hint']};
                font-size: {cls.FONTS['size_sm']}px;
            }}
            
            /* 卡片标题 */
            QLabel[class="card-title"] {{
                color: {colors['text_primary']};
                font-size: {cls.FONTS['size_lg']}px;
                font-weight: 600;
            }}
            
            /* 分隔线 */
            QFrame[class="divider"] {{
                background: {colors['border_light']};
                height: 1px;
            }}
            
            /* 进度条 */
            QProgressBar {{
                border: 1px solid {colors['border']};
                border-radius: {cls.BORDER_RADIUS['sm']}px;
                background: {colors['bg_hover']};
                height: 16px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: {colors['primary']};
                border-radius: {cls.BORDER_RADIUS['sm']}px;
            }}
            
            {cls.get_scrollbar_style()}
        """

# 常用标签页emoji映射
TAB_EMOJIS = {
    "symbol": "📑",
    "excel": "📊",
    "word": "📄",
    "pdf": "📕",
    "toolbox": "🧰",
    "shortcut": "⌨️",
    "function": "📚",
    "problem": "🛠️"
}

TAB_NAMES = {
    "symbol": "符号处理",
    "excel": "表格编辑",
    "word": "文本处理",
    "pdf": "PDF处理",
    "toolbox": "工具箱",
    "shortcut": "快捷键",
    "function": "函数教程",
    "problem": "问题解决"
}
