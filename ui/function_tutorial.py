# ui/function_tutorial.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QLineEdit,
    QComboBox, QListWidget, QFrame, QTextEdit, QPushButton, QApplication
)
from PySide6.QtCore import Qt
import qtawesome as qta


class FunctionTutorialWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.theme_manager = main_window.theme_manager
        
        self.function_data = []
        self.function_detail_content = None
        self.copy_example_btn = None
        
        self.init_ui()
        self.init_function_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 页面标题（带图标）
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.book', color='#409eff').pixmap(24, 24))
        title_layout.addWidget(title_icon)
        title_label = QLabel("Excel函数教程")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addWidget(title_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：搜索 + 分类 + 列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_icon = QLabel()
        search_icon.setPixmap(qta.icon('fa5s.search', color='#909399').pixmap(16, 16))
        search_layout.addWidget(search_icon)
        self.function_search = QLineEdit()
        self.function_search.setPlaceholderText("搜索函数名称或描述...")
        self.function_search.textChanged.connect(self.filter_functions)
        search_layout.addWidget(self.function_search)
        left_layout.addLayout(search_layout)
        
        # 分类下拉框
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "数学与统计", "文本处理", "查找与引用", "逻辑函数", "日期与时间", "信息函数", "工程函数"])
        self.category_combo.currentTextChanged.connect(self.filter_functions)
        category_layout.addWidget(self.category_combo)
        category_layout.addStretch()
        left_layout.addLayout(category_layout)
        
        self.function_list_widget = QListWidget()
        self.function_list_widget.setSpacing(4)
        self.function_list_widget.currentRowChanged.connect(self.show_function_detail)
        left_layout.addWidget(self.function_list_widget, stretch=1)
        
        splitter.addWidget(left_widget)
        
        # 右侧：详情卡片
        right_widget = QFrame()
        right_widget.setProperty("class", "main-card")
        self.detail_layout = QVBoxLayout(right_widget)
        self.detail_layout.setContentsMargins(20, 20, 20, 20)
        self.detail_layout.setSpacing(16)
        
        # 右侧标题（只保留这一个）
        self.function_detail_title = QLabel("请从左侧选择一个函数")
        self.function_detail_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #409eff;")
        self.detail_layout.addWidget(self.function_detail_title)
        
        self.function_detail_content = QTextEdit()
        self.function_detail_content.setReadOnly(True)
        base_style = """
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 15px;
                line-height: 1.6;
                color: #000000;
            }
            QTextEdit::selection {
                background-color: #409eff;
                color: white;
            }
        """
        self.function_detail_content.setStyleSheet(base_style)
        self.detail_layout.addWidget(self.function_detail_content, stretch=1)
        
        self.copy_example_btn = QPushButton(" 复制示例")
        self.copy_example_btn.setIcon(qta.icon('fa5s.copy', color='white'))
        self.copy_example_btn.clicked.connect(self.copy_function_example)
        self.copy_example_btn.setEnabled(False)
        self.detail_layout.addWidget(self.copy_example_btn)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter, stretch=1)
    
    def init_function_data(self):
        # 函数数据（30个常用Excel函数，通用知识，无侵权风险）
        self.function_data = [
            # === 数学与统计 (8个) ===
            {
                "name": "SUM - 求和",
                "category": "数学与统计",
                "description": "计算一组数字的总和。",
                "examples": [
                    "=SUM(A1:A10)  → 计算A1到A10所有数字的和",
                    "=SUM(A1, B2, C3)  → 计算三个单独单元格的和",
                    "=SUM(10, 20, 30)  → 直接输入数字求和，结果为60"
                ],
                "note": "忽略文本和空单元格，只计算数字。"
            },
            {
                "name": "AVERAGE - 平均值",
                "category": "数学与统计",
                "description": "计算一组数字的平均值。",
                "examples": [
                    "=AVERAGE(A1:A10)  → 计算A1到A10的平均值",
                    "=AVERAGE(B1:B5, C1:C5)  → 计算两个范围的平均值",
                    "=AVERAGE(10, 20, 30)  → 直接输入数字，结果为20"
                ],
                "note": "忽略文本和空单元格。若需计算包含文本的计数，请用 COUNTA。"
            },
            {
                "name": "COUNT - 计数",
                "category": "数学与统计",
                "description": "计算包含数字的单元格数量。",
                "examples": [
                    "=COUNT(A:A)  → 计算A列有多少个数字",
                    "=COUNT(B1:B10)  → 计算B1到B10中数字的个数",
                    "=COUNT(1, 2, \"文本\", 3)  → 结果为3（忽略文本）"
                ],
                "note": "COUNT只计算数字；COUNTA计算所有非空单元格。"
            },
            {
                "name": "MAX / MIN - 最大值/最小值",
                "category": "数学与统计",
                "description": "找出一组数字中的最大值或最小值。",
                "examples": [
                    "=MAX(A1:A10)  → 返回A1到A10中的最大值",
                    "=MIN(B1:B10)  → 返回B1到B10中的最小值",
                    "=MAX(10, 20, 5)  → 结果为20"
                ],
                "note": "忽略文本和空单元格。"
            },
            {
                "name": "COUNTIF - 条件计数",
                "category": "数学与统计",
                "description": "计算满足指定条件的单元格数量。",
                "examples": [
                    "=COUNTIF(A1:A10, \">60\")  → 计算大于60的单元格数量",
                    "=COUNTIF(B1:B10, \"张三\")  → 计算等于\"张三\"的单元格数量",
                    "=COUNTIF(C1:C10, \"<>\")  → 计算非空单元格数量"
                ],
                "note": "条件可以是数字、文本或表达式。"
            },
            {
                "name": "SUMIF - 条件求和",
                "category": "数学与统计",
                "description": "对满足指定条件的单元格求和。",
                "examples": [
                    "=SUMIF(A1:A10, \">60\", B1:B10)  → 对A列>60对应的B列求和",
                    "=SUMIF(C1:C10, \"水果\", D1:D10)  → 对C列为\"水果\"对应的D列求和",
                    "=SUMIF(E1:E10, \"<>\", F1:F10)  → 对E列非空对应的F列求和"
                ],
                "note": "条件区域和求和区域应大小一致。"
            },
            {
                "name": "ROUND - 四舍五入",
                "category": "数学与统计",
                "description": "将数字四舍五入到指定的小数位数。",
                "examples": [
                    "=ROUND(3.14159, 2)  → 结果为3.14",
                    "=ROUND(1234.5678, -2)  → 结果为1200",
                    "=ROUND(2.71828, 0)  → 结果为3"
                ],
                "note": "第二位参数为正数表示小数位数，负数表示整数位数。"
            },
            {
                "name": "RAND / RANDBETWEEN - 随机数",
                "category": "数学与统计",
                "description": "生成随机数。RAND()返回0~1之间的小数，RANDBETWEEN返回指定整数区间内的随机整数。",
                "examples": [
                    "=RAND()  → 生成0~1之间的随机小数",
                    "=RANDBETWEEN(1, 100)  → 生成1~100之间的随机整数",
                    "=RANDBETWEEN(10, 20)  → 每次刷新表格时变化"
                ],
                "note": "RAND和RANDBETWEEN是易变函数，每次工作表重算都会变化。"
            },
            # === 文本处理 (6个) ===
            {
                "name": "CONCATENATE / & - 文本合并",
                "category": "文本处理",
                "description": "将多个文本合并为一个。",
                "examples": [
                    "=CONCATENATE(A1, B1)  → 合并A1和B1的内容",
                    "=A1 & \"-\" & B1  → 使用&符号连接，效果相同",
                    "=CONCATENATE(\"Hello\", \" \", \"World\")  → 结果为\"Hello World\""
                ],
                "note": "&符号更加灵活，建议使用。"
            },
            {
                "name": "LEFT / RIGHT / MID - 文本截取",
                "category": "文本处理",
                "description": "从文本中提取部分内容。",
                "examples": [
                    "=LEFT(\"HelloWorld\", 5)  → 提取左侧5个字符 → \"Hello\"",
                    "=RIGHT(\"HelloWorld\", 5)  → 提取右侧5个字符 → \"World\"",
                    "=MID(\"HelloWorld\", 6, 5)  → 从第6位开始，提取5个字符 → \"World\""
                ],
                "note": "MID的第二个参数是起始位置（从1开始），第三个是长度。"
            },
            {
                "name": "LEN - 文本长度",
                "category": "文本处理",
                "description": "计算文本包含的字符数量。",
                "examples": [
                    "=LEN(\"Excel\")  → 结果为5",
                    "=LEN(A1)  → 计算A1单元格的字符数",
                    "=LEN(\"你好 世界\")  → 结果为5（包括空格）"
                ],
                "note": "空格也会被计算在内。"
            },
            {
                "name": "TRIM - 去除空格",
                "category": "文本处理",
                "description": "去除文本首尾的空格，以及中间多余的空格。",
                "examples": [
                    "=TRIM(\"  Excel  \")  → 结果为\"Excel\"",
                    "=TRIM(\"Hello   World\")  → 结果为\"Hello World\"",
                    "=TRIM(A1)  → 清理A1中的多余空格"
                ],
                "note": "单词之间只保留一个空格。"
            },
            {
                "name": "TEXT - 格式化数字",
                "category": "文本处理",
                "description": "将数字转换为指定格式的文本。",
                "examples": [
                    "=TEXT(1234.56, \"$0.00\")  → 结果为\"$1234.56\"",
                    "=TEXT(0.85, \"0%\")  → 结果为\"85%\"",
                    "=TEXT(TODAY(), \"yyyy年mm月dd日\")  → 显示当前日期为中文格式"
                ],
                "note": "常用于配合报表输出。"
            },
            {
                "name": "TEXTJOIN - 智能合并",
                "category": "文本处理",
                "description": "将多个文本用指定分隔符连接，可选择忽略空单元格。",
                "examples": [
                    "=TEXTJOIN(\", \", TRUE, A1:A5)  → 用逗号空格连接A1到A5的非空单元格",
                    "=TEXTJOIN(\"-\", FALSE, B1:B3)  → 用-连接所有单元格，包含空值",
                    "=TEXTJOIN(\" \", TRUE, C1:C10)  → 用空格连接C列中所有非空内容"
                ],
                "note": "第二个参数为TRUE时忽略空单元格，为FALSE时保留空单元格。"
            },
            # === 查找与引用 (4个) ===
            {
                "name": "VLOOKUP - 垂直查找",
                "category": "查找与引用",
                "description": "在表格中查找指定的值，并返回对应位置的数据。",
                "examples": [
                    "=VLOOKUP(A2, B:D, 2, FALSE)  → 在B列查找A2的值，返回C列对应值",
                    "=VLOOKUP(1001, E:G, 3, FALSE)  → 在E列查找1001，返回G列值",
                    "=VLOOKUP(\"Apple\", A1:B10, 2, TRUE)  → 近似匹配，用于区间查找"
                ],
                "note": "FALSE表示精确匹配，TRUE表示近似匹配。查找值必须在查找范围的第一列。"
            },
            {
                "name": "INDEX - 返回指定位置的值",
                "category": "查找与引用",
                "description": "返回表格中指定行和列的值。",
                "examples": [
                    "=INDEX(A1:C10, 2, 3)  → 返回第2行第3列的值",
                    "=INDEX(A:A, 5)  → 返回A列第5行的值",
                    "=INDEX(B2:D5, 3, 2)  → 返回B2:D5区域中第3行第2列的值"
                ],
                "note": "通常和MATCH配合使用实现动态查找。"
            },
            {
                "name": "MATCH - 查找位置",
                "category": "查找与引用",
                "description": "查找值在列表中的位置。",
                "examples": [
                    "=MATCH(A2, B:B, 0)  → 查找A2在B列的位置",
                    "=MATCH(100, C1:C10, 1)  → 在升序列表中查找小于等于100的最大值位置",
                    "=MATCH(\"Apple\", A1:A5, -1)  → 在降序列表中查找大于等于\"Apple\"的最小值位置"
                ],
                "note": "0表示精确匹配，1表示升序近似匹配，-1表示降序近似匹配。"
            },
            {
                "name": "XLOOKUP - 现代查找函数",
                "category": "查找与引用",
                "description": "在数组中查找指定值并返回对应结果，支持横向和纵向查找。",
                "examples": [
                    "=XLOOKUP(A2, B:B, C:C)  → 在B列查找A2，返回C列对应值",
                    "=XLOOKUP(\"Apple\", A1:A10, B1:B10, \"未找到\")  → 未找到时返回\"未找到\"",
                    "=XLOOKUP(100, E1:E5, F1:F5, \"\", 1)  → 使用近似匹配"
                ],
                "note": "XLOOKUP比VLOOKUP更灵活，不需要查找列在第一列。"
            },
            # === 逻辑函数 (3个) ===
            {
                "name": "IF - 条件判断",
                "category": "逻辑函数",
                "description": "根据条件返回不同的值。",
                "examples": [
                    "=IF(A1>60, \"及格\", \"不及格\")  → 根据分数判断及格/不及格",
                    "=IF(A1=\"\", \"空\", \"非空\")  → 判断单元格是否为空",
                    "=IF(AND(A1>0, A1<100), \"有效\", \"无效\")  → 结合AND函数进行多条件判断"
                ],
                "note": "可以多层嵌套IF，也可以使用IFS函数简化多层判断。"
            },
            {
                "name": "IFERROR - 错误处理",
                "category": "逻辑函数",
                "description": "如果公式出错，显示指定值。",
                "examples": [
                    "=IFERROR(A1/B1, \"除数不能为0\")  → 除数为0时显示提示",
                    "=IFERROR(VLOOKUP(A2, B:C, 2, FALSE), \"未找到\")  → 查找失败时显示\"未找到\"",
                    "=IFERROR(1/0, \"错误\")  → 结果为\"错误\""
                ],
                "note": "可以处理#N/A、#DIV/0!、#VALUE!等各种错误。"
            },
            {
                "name": "IFS - 多条件判断",
                "category": "逻辑函数",
                "description": "依次判断多个条件，返回第一个满足条件的值。",
                "examples": [
                    "=IFS(A1>90, \"优秀\", A1>80, \"良好\", A1>60, \"及格\", TRUE, \"不及格\")",
                    "=IFS(B1=\"A\", 100, B1=\"B\", 80, B1=\"C\", 60, TRUE, 0)",
                    "=IFS(C1>0, \"正数\", C1<0, \"负数\", TRUE, \"零\")"
                ],
                "note": "最后一个条件通常用TRUE作为默认值。"
            },
            # === 日期与时间 (5个) ===
            {
                "name": "TODAY - 当前日期",
                "category": "日期与时间",
                "description": "获取当天的日期。",
                "examples": [
                    "=TODAY()  → 显示今天的日期",
                    "=TODAY()+7  → 显示一周后的日期",
                    "=YEAR(TODAY())  → 提取当前年份"
                ],
                "note": "日期会每天自动更新。"
            },
            {
                "name": "NOW - 当前时间",
                "category": "日期与时间",
                "description": "获取当前日期和时间。",
                "examples": [
                    "=NOW()  → 显示当前日期和时间",
                    "=HOUR(NOW())  → 提取当前小时",
                    "=NOW()-TODAY()  → 计算当前时间占一天的比值"
                ],
                "note": "时间会实时更新，每次计算都会变化。"
            },
            {
                "name": "YEAR / MONTH / DAY - 提取日期",
                "category": "日期与时间",
                "description": "从日期中提取年份、月份或日期。",
                "examples": [
                    "=YEAR(A1)  → 提取A1的年份",
                    "=MONTH(A1)  → 提取A1的月份",
                    "=DAY(A1)  → 提取A1的日期"
                ],
                "note": "需要A1包含有效的日期格式。"
            },
            {
                "name": "DATEDIF - 计算日期差",
                "category": "日期与时间",
                "description": "计算两个日期之间的天数、月数或年数。",
                "examples": [
                    "=DATEDIF(A1, B1, \"d\")  → 计算A1到B1的天数",
                    "=DATEDIF(A1, B1, \"m\")  → 计算A1到B1的整月数",
                    "=DATEDIF(A1, B1, \"y\")  → 计算A1到B1的整年数"
                ],
                "note": "第三个参数支持\"d\"(天)、\"m\"(月)、\"y\"(年)、\"md\"(忽略月)等。"
            },
            {
                "name": "NETWORKDAYS - 工作日天数",
                "category": "日期与时间",
                "description": "计算两个日期之间的工作日天数，可指定假期。",
                "examples": [
                    "=NETWORKDAYS(A1, B1)  → 计算A1到B1的工作日",
                    "=NETWORKDAYS(A1, B1, C1:C5)  → 排除C1到C5的假期",
                    "=NETWORKDAYS(TODAY(), TODAY()+30)  → 计算未来30天的工作日"
                ],
                "note": "工作日不包括周六和周日。"
            },
            # === 信息函数 (1个) ===
            {
                "name": "ISERROR / ISBLANK - 信息判断",
                "category": "信息函数",
                "description": "判断单元格是否为错误值或空值。",
                "examples": [
                    "=ISERROR(A1)  → 如果A1是错误值则返回TRUE",
                    "=ISBLANK(A1)  → 如果A1为空则返回TRUE",
                    "=IF(ISBLANK(A1), \"空\", \"有内容\")  → 判断单元格是否为空"
                ],
                "note": "常用于错误处理和数据清洗。"
            },
            # === 工程函数 (1个) ===
            {
                "name": "CONVERT - 单位转换",
                "category": "工程函数",
                "description": "将数字从一种单位转换为另一种单位。",
                "examples": [
                    "=CONVERT(1, \"m\", \"ft\")  → 1米等于多少英尺（约3.2808）",
                    "=CONVERT(100, \"C\", \"F\")  → 100摄氏度转换为华氏度（212°F）",
                    "=CONVERT(1, \"lbm\", \"kg\")  → 1磅等于多少千克（约0.4536）"
                ],
                "note": "支持长度、重量、温度、时间等数十种单位。"
            }
        ]
        # 填充列表
        self.function_list_widget.clear()
        for func in self.function_data:
            self.function_list_widget.addItem(func["name"])
        if self.function_list_widget.count() > 0:
            self.function_list_widget.setCurrentRow(0)
    
    def filter_functions(self):
        search_text = self.function_search.text().lower()
        category = self.category_combo.currentText()
        for i in range(self.function_list_widget.count()):
            item = self.function_list_widget.item(i)
            func = self.function_data[i]
            show = True
            if category != "全部" and func["category"] != category:
                show = False
            if search_text:
                if (search_text not in func["name"].lower() and
                    search_text not in func["category"].lower() and
                    search_text not in func["description"].lower()):
                    show = False
            item.setHidden(not show)
    
    def show_function_detail(self, index):
        if index < 0 or index >= len(self.function_data):
            return
        func = self.function_data[index]
        # 设置右侧唯一标题
        self.function_detail_title.setText(f"📖 {func['name']}")
        self.function_detail_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme_manager.get_theme()['primary']};")
        
        # 获取当前主题的颜色
        theme = self.theme_manager.get_theme()
        primary = theme["primary"]
        card_bg = theme["card"]
        text_color = theme["text"]
        text_secondary = theme["text_secondary"]
        border = theme["border"]
        
        # 定义颜色映射字典
        color_map = {
            "#409eff": primary,
            "#f5f7fa": card_bg,
            "#fff7e6": card_bg,
            "#fef0f0": card_bg,
            "#000000": text_color,
            "#e6a23c": text_secondary,
            "#f56c6c": text_secondary,
            "#f0f0f0": card_bg,
            "#dcdfe6": border,
            "#e8f4ff": card_bg,
            "#666666": text_secondary,
        }
        
        # 使用动态颜色的 HTML 模板（不再包含标题 h3）
        html = f"""
        <div style="font-family: 'Microsoft YaHei', sans-serif; font-size: 16px; line-height: 1.8; color: {text_color}; background-color: {card_bg};">
            <div style="background-color: {card_bg}; padding: 16px 20px; border-radius: 8px; margin: 16px 0; border-left: 4px solid {primary}; font-size: 15px; color: {text_color};">
                <strong style="color: {primary};">📂 分类：</strong>{func['category']}
            </div>
            
            <div style="background-color: {card_bg}; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid {primary};">
                <h4 style="color: {primary}; margin: 0 0 12px 0; font-size: 17px;">📌 功能说明</h4>
                <p style="line-height: 1.8; color: {text_color}; font-size: 15px; margin: 0;">{func['description']}</p>
            </div>
            
            <div style="background-color: {card_bg}; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid {text_secondary};">
                <h4 style="color: {text_secondary}; margin: 0 0 12px 0; font-size: 17px;">💡 使用示例</h4>
        """
        for example in func['examples']:
            html += f'<p style="font-family: Consolas, monospace; color: {text_secondary}; margin: 8px 0; font-size: 15px;">{example}</p>'
        html += f"""
            </div>
            
            <div style="background-color: {card_bg}; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid {text_secondary};">
                <h4 style="color: {text_secondary}; margin: 0 0 12px 0; font-size: 17px;">⚠️ 注意事项</h4>
                <p style="color: {text_color}; margin: 0;">{func['note']}</p>
            </div>
        </div>
        """
        self.function_detail_content.setHtml(html)
        
        # 启用复制按钮，并连接复制功能
        self.copy_example_btn.setEnabled(True)
        try:
            self.copy_example_btn.clicked.disconnect()
        except:
            pass
        if func.get("examples") and len(func["examples"]) > 0:
            self.copy_example_btn.clicked.connect(
                lambda: QApplication.clipboard().setText(func["examples"][0])
            )
    
    def copy_function_example(self):
        pass
    
    def apply_theme(self):
        """应用主题，由主窗口调用"""
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            self.setStyleSheet(f"QFrame.main-card {{ background-color: {theme['card']}; border: 1px solid {theme['border']}; }}")
            # 刷新当前显示的内容（如果有选中项）
            current_row = self.function_list_widget.currentRow()
            if current_row >= 0:
                self.show_function_detail(current_row)