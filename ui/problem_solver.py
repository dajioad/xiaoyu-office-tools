# ui/problem_solver.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel, QLineEdit,
    QComboBox, QListWidget, QFrame, QTextEdit, QPushButton
)
from PySide6.QtCore import Qt
import qtawesome as qta


class ProblemSolverWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.config_manager = main_window.config_manager
        self.theme_manager = main_window.theme_manager
        
        self.help_data = []
        self.init_ui()
        self.init_help_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 页面标题（带图标）+ 新手引导按钮
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(8)
        title_icon = QLabel()
        title_icon.setPixmap(qta.icon('fa5s.question-circle', color='#409eff').pixmap(24, 24))
        title_layout.addWidget(title_icon)
        title_label = QLabel("功能说明 & 帮助")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加新手引导按钮
        self.guide_btn = QPushButton(" 新手引导")
        self.guide_btn.setIcon(qta.icon('fa5s.lightbulb', color='#409eff'))
        self.guide_btn.setCursor(Qt.PointingHandCursor)
        self.guide_btn.clicked.connect(self.show_guide)
        title_layout.addWidget(self.guide_btn)
        
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
        self.help_search = QLineEdit()
        self.help_search.setPlaceholderText("搜索功能或问题...")
        self.help_search.textChanged.connect(self.filter_help_items)
        search_layout.addWidget(self.help_search)
        left_layout.addLayout(search_layout)
        
        # 分类下拉框
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("分类:"))
        self.help_category_combo = QComboBox()
        self.help_category_combo.addItems(["全部", "符号处理", "表格编辑", "文本处理", "工具箱", "激活相关", "设置相关"])
        self.help_category_combo.currentTextChanged.connect(self.filter_help_items)
        category_layout.addWidget(self.help_category_combo)
        category_layout.addStretch()
        left_layout.addLayout(category_layout)
        
        self.help_list_widget = QListWidget()
        self.help_list_widget.setSpacing(4)
        self.help_list_widget.currentRowChanged.connect(self.show_help_detail)
        left_layout.addWidget(self.help_list_widget, stretch=1)
        
        splitter.addWidget(left_widget)
        
        # 右侧：详情卡片
        right_widget = QFrame()
        right_widget.setProperty("class", "main-card")
        self.detail_layout = QVBoxLayout(right_widget)
        self.detail_layout.setContentsMargins(20, 20, 20, 20)
        self.detail_layout.setSpacing(16)
        
        # 右侧标题
        self.help_detail_title = QLabel("请从左侧选择一个功能")
        self.help_detail_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #409eff;")
        self.detail_layout.addWidget(self.help_detail_title)
        
        self.help_detail_content = QTextEdit()
        self.help_detail_content.setReadOnly(True)
        base_style = """
            QTextEdit {
                background-color: transparent;
                border: none;
                font-size: 15px;
                line-height: 1.8;
                color: #000000;
            }
            QTextEdit::selection {
                background-color: #409eff;
                color: white;
            }
        """
        self.help_detail_content.setStyleSheet(base_style)
        self.detail_layout.addWidget(self.help_detail_content, stretch=1)
        
        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        
        layout.addWidget(splitter, stretch=1)
    
    def init_help_data(self):
        # 帮助数据（每个项目添加category字段）
        self.help_data = [
            # 新增：关于软件
            {
                "name": "💝 关于软件",
                "category": "设置相关",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 20px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <h4 style="color: #409eff; margin-bottom: 15px; font-size: 18px;">🌟 开发初衷</h4>
                        <p style="margin: 10px 0; line-height: 1.8;">
                            还记得刚开始学习 Excel 函数的时候，每次处理数据都特别繁琐。就拿简单的字符串转数组来说，输入「ABCDEF」，要手动变成「"A","B","C","D","E","F"」这样的格式，重复枯燥的工作让我萌生了开发一款工具的想法。
                        </p>
                        <p style="margin: 10px 0; line-height: 1.8;">
                            于是，基于 PySide6，我开始了这款办公工具的开发。希望它能让日常办公中那些麻烦的小事情变得简单高效，帮大家节省宝贵的时间。
                        </p>
                    </div>
                    
                    
                    <div style="background-color: #fff7e6; padding: 15px 20px; border-radius: 8px; border-left: 4px solid #e6a23c; margin: 15px 0;">
                        <h4 style="color: #e6a23c; margin-bottom: 12px; font-size: 18px;">❤️ 感谢支持</h4>
                        <p style="margin: 8px 0; line-height: 1.8;">
                            如果这款工具对你有帮助，欢迎分享给身边的朋友。您的支持是我持续优化的动力！
                        </p>
                        <p style="margin: 8px 0; line-height: 1.8;">
                            如果有功能建议或遇到问题，可以通过以下方式联系：
                        </p>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 6px 0;">💬 微信：fangbaby2233</li>
                            <li style="margin: 6px 0;">🐧 QQ：2818491757</li>
                        </ul>
                    </div>
                """
            },
            # 符号与公式助手（移至前面）
            {
                "name": "🔢 符号与公式助手",
                "category": "符号处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <h4 style="color: #409eff; margin-bottom: 10px;">📋 功能概述</h4>
                        <p>符号与公式助手是一个强大的文本处理工具，支持快速插入符号、公式，并对文本进行各种格式化处理。</p>
                        
                        <h4 style="color: #409eff; margin: 15px 0 10px 0;">🚀 打开方式</h4>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>系统托盘</strong><br>
                            最小化窗口后，鼠标右键点击托盘图标 → 选择「符号与公式助手」</li>
                        </ul>
                        
                        <h4 style="color: #409eff; margin: 15px 0 10px 0;">📝 使用方法详解</h4>
                        
                        <div style="background-color: #e8f4ff; padding: 12px 15px; border-radius: 6px; margin: 10px 0;">
                            <strong>方法一：双击插入公式，单击插入符号。</strong>
                            <p style="margin: 8px 0;">在符号列表或公式列表中，<strong>双击或单击</strong>任意公式或符号，即可直接插入到输入文本框中。</p>
                            <p style="margin: 0; color: #666;">示例：双击求和公式，输入框会显示：<code>SUM(A1:A10)</code></p>
                            <p style="margin: 0; color: #666;">单击「书名号」符号，输入框会显示：《测试文本》</p>
                        </div>
                        
                        <div style="background-color: #e8f4ff; padding: 12px 15px; border-radius: 6px; margin: 10px 0;">
                            <strong>方法二：选中文本 + 符号 + 插入方式</strong>
                            <p style="margin: 8px 0;">这是最常用的操作流程：</p>
                            <ol style="margin: 8px 0; padding-left: 20px;">
                                <li style="margin: 6px 0;"><strong>第一步：输入文本</strong><br>
                                在输入文本框中输入或粘贴需要处理的文本，例如：<code>测试文本</code></li>
                                
                                <li style="margin: 6px 0;"><strong>第二步：选中文本</strong><br>
                                用鼠标<strong>选中</strong>需要处理的文字部分，例如选中「测试」两个字</li>
                                
                                <li style="margin: 6px 0;"><strong>第三步：选择符号</strong><br>
                                在符号列表中<strong>单击</strong>选择一个符号，例如选择「书名号」《》</li>
                                
                                <li style="margin: 6px 0;"><strong>第四步：选择插入方式</strong><br>
                                选择符号的插入位置：
                                <ul style="margin: 6px 0; padding-left: 20px;">
                                    <li><strong>头部</strong>：在选中文字前添加符号 → 《测试文本</li>
                                    <li><strong>尾部</strong>：在选中文字后添加符号 → 测试文本《</li>
                                    <li><strong>两端</strong>：在选中文字两侧添加符号 → 《测试》文本</li>
                                    <li><strong>分隔</strong>：在每个字符间插入符号 → 测《试</li>
                                </ul>
                                </li>
                                
                                <li style="margin: 6px 0;"><strong>第五步：点击「选中」按钮</strong><br>
                                点击「选中」按钮，鼠标选中的区域处理结果会显示在文本框中</li>
                            </ol>
                        </div>
                        
                        <div style="background-color: #e8f4ff; padding: 12px 15px; border-radius: 6px; margin: 10px 0;">
                            <strong>方法三：全部输出（处理整个文本框）</strong>
                            <p style="margin: 8px 0;">「全部输出」会对输入文本框中的<strong>全部内容</strong>进行处理：</p>
                            <ol style="margin: 8px 0; padding-left: 20px;">
                                <li style="margin: 6px 0;">在输入文本框中输入完整文本</li>
                                <li style="margin: 6px 0;">选择要应用的符号</li>
                                <li style="margin: 6px 0;">选择插入方式（头部/尾部/两端/分隔）</li>
                                <li style="margin: 6px 0;">点击「全部输出」按钮</li>
                            </ol>
                            <p style="margin: 0; color: #666;">示例：输入「你好世界」，选择书名号，选择「两端」，点击全部输出 → 《你好世界》</p>
                        </div>
                        
                    </div>
                    <div style="background-color: #fef0f0; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #f56c6c; margin: 10px 0;">
                        <strong>⚠️ 注意</strong>：符号与公式助手需要 Pro 版才能使用完整功能。
                    </div>
                """
            },
            # 截图功能（移至前面）
            {
                "name": "📷 截图功能",
                "category": "工具箱",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <h4 style="color: #409eff; margin-bottom: 10px;">📸 功能概述</h4>
                        <p>截图功能支持全屏截图、区域截图、窗口截图三种模式，截图后可直接进行复制或保存。</p>
                        
                        <h4 style="color: #409eff; margin: 15px 0 10px 0;">🎯 使用方法</h4>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>系统托盘</strong><br>
                            最小化窗口后，鼠标右键点击托盘图标 → 选择「截图」 → 选择截图模式</li>
                        </ul>
                        
                        <h4 style="color: #409eff; margin: 15px 0 10px 0;">✂️ 截图操作</h4>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>区域截图</strong>：鼠标拖动选择区域，松开完成截图</li>
                            <li style="margin: 8px 0;"><strong>全屏截图</strong>：系统托盘直接点击全屏按钮</li>
                            <li style="margin: 8px 0;"><strong>取消截图</strong>：按 Esc 键退出</li>
                        </ul>
                        
                        <h4 style="color: #409eff; margin: 15px 0 10px 0;">💾 保存与分享</h4>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>复制到剪贴板</strong>：点击复制按钮</li>
                            <li style="margin: 8px 0;"><strong>保存为文件</strong>：点击保存按钮，支持 PNG/JPG 格式</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 提示</strong>：截图会自动保存到自定义的位置。
                    </div>
                """
            },
            {
                "name": "🎨 符号处理",
                "category": "符号处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>多种常用符号</strong>：引号、括号、书名号、省略号等</li>
                            <li style="margin: 8px 0;"><strong>4种插入方式</strong>：
                                <ul>
                                    <li>头部：在文本前添加符号</li>
                                    <li>尾部：在文本后添加符号</li>
                                    <li>两端：在文本两侧添加符号</li>
                                    <li>分隔：在每个字符间插入符号</li>
                                </ul>
                            </li>
                            <li style="margin: 8px 0;"><strong>符号叠加</strong>：可以在一次符号处理的基础上继续叠加。比如：先选择符号，再选择插入方式，最后点击"应用叠加"可将结果保存到成品区，等待下一次追加符号处理。输入123，选择双引号，插入分隔（逗号数组模式），点击应用叠加，结果为："1","2","3"再选择书名号两端，应用叠加结果是：《"1","2","3"》。</li>
                            <li style="margin: 8px 0;"><strong>中英切换</strong>：一键切换中文/英文符号，需要注意结果是否需要转换为英文符号。</li>
                            <li style="margin: 8px 0;"><strong>自定义符号</strong>：在设置中添加您常用的符号</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 使用技巧</strong>：预览区是实时显示当前选择的符号，成品区显示的是最终符号叠加的结果。

                    </div>
                    <h4 style="color: #000000; margin-top: 20px;">⚠️ 常见问题</h4>
                    <div style="background-color: #fef0f0; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #f56c6c;">
                        <p><strong>Q: 自定义符号怎么添加？</strong><br>
                        A: 打开设置→符号设置，在自定义符号中添加即可。</p>
                    </div>
                """
            },
            {
                "name": "📊 表格编辑",
                "category": "表格编辑",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>文件操作</strong>：打开、编辑、保存Excel文件（.xlsx, .xls）</li>
                            <li style="margin: 8px 0;"><strong>数据编辑</strong>：双击单元格直接编辑内容</li>
                            <li style="margin: 8px 0;"><strong>查找替换</strong>：快速查找并替换数据</li>
                            <li style="margin: 8px 0;"><strong>行列管理</strong>：冻结行、删除行列、调整列宽</li>
                            <li style="margin: 8px 0;"><strong>公式计算</strong>：支持常用公式，自动计算结果</li>
                        </ul>
                    </div>
                    <div style="background-color: #fef0f0; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #f56c6c; margin: 10px 0;">
                        <strong>⚠️ 注意</strong>：免费版仅支持查看Excel，Pro版才能编辑和保存！
                    </div>
                    <h4 style="color: #000000; margin-top: 20px;">⚠️ 常见问题</h4>
                    <div style="background-color: #fef0f0; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #f56c6c;">
                        <p><strong>Q: Excel编辑不了？</strong><br>
                        A: 免费版只能查看Excel，Pro版才能编辑和保存。</p>
                    </div>
                """
            },
            {
                "name": "📝 文本处理",
                "category": "文本处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>富文本编辑器</strong>：支持加粗、斜体、下划线、字体颜色等</li>
                            <li style="margin: 8px 0;"><strong>右键菜单</strong>：快速插入符号（如书名号、引号等）</li>
                            <li style="margin: 8px 0;"><strong>格式设置</strong>：字体、字号、对齐方式等</li>
                            <li style="margin: 8px 0;"><strong>保存为Word</strong>：将编辑的内容保存为.docx文件</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 提示</strong>：使用Ctrl+B、Ctrl+I等快捷键可以快速格式化文本。
                    </div>
                """
            },
            {
                "name": "🧰 工具箱",
                "category": "工具箱",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>剪贴板历史</strong>：自动记录复制过的内容，随时找回。启用过滤可过滤身份证、银行卡、手机号等敏感信息。</li>
                            <li style="margin: 8px 0;"><strong>批量文件处理</strong>：快速重命名、替换内容改后缀</li>
                            <li style="margin: 8px 0;"><strong>图片工具</strong>：压缩、图片格式转换、ICO图标生成</li>
                            <li style="margin: 8px 0;"><strong>压缩解压</strong>：打包解压、批量ZIP</li>
                            <li style="margin: 8px 0;"><strong>批量文字提取</strong>：Word/Excel/PDF/TXT/图片提取文字</li>
                            <li style="margin: 8px 0;"><strong>图片OCR</strong>：图片文字识别</li>
                            <li style="margin: 8px 0;"><strong>文本格式化</strong>：JSON/SQL/Markdown等文本进行一键排版</li>
                            <li style="margin: 8px 0;"><strong>格式互转</strong>：Word/Excel互转</li>
                            <li style="margin: 8px 0;"><strong>音频转换</strong>：音频转MP3/WAV/FLAC/AAC/OGG/opus</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 提示</strong>：工具箱中的功能需要Pro版才能使用。
                    </div>
                """
            },
            {
                "name": "📖 函数教程",
                "category": "符号处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p>内置了丰富的Excel函数教程，包括：</p>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;"><strong>数学与统计函数</strong>：SUM、AVERAGE、MAX、MIN等</li>
                            <li style="margin: 8px 0;"><strong>文本处理函数</strong>：CONCATENATE、LEFT、RIGHT、MID等</li>
                            <li style="margin: 8px 0;"><strong>查找与引用函数</strong>：VLOOKUP、INDEX、MATCH等</li>
                            <li style="margin: 8px 0;"><strong>逻辑函数</strong>：IF、IFERROR等</li>
                            <li style="margin: 8px 0;"><strong>日期与时间函数</strong>：TODAY、NOW、YEAR等</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 使用技巧</strong>：点击左侧"函数教程"标签，选择具体函数查看详细说明！
                    </div>
                """
            },
            {
                "name": "❓ 问题解决",
                "category": "符号处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>Q: 如何激活Pro版？</strong><br>
                        A: 点击"激活"按钮，输入激活码即可。</p>
                        
                        <p><strong>Q: 符号面板怎么打不开？</strong><br>
                        A: 需要先激活Pro版才能使用符号与公式助手。</p>
                        
                        <p><strong>Q: Excel编辑不了？</strong><br>
                        A: 免费版只能查看Excel，Pro版才能编辑和保存。</p>
                        
                        <p><strong>Q: 自定义符号怎么添加？</strong><br>
                        A: 打开设置→符号设置，在自定义符号中添加即可。</p>
                        
                        <p><strong>Q: 如何备份配置？</strong><br>
                        A: 打开设置→备份恢复，选择备份内容和位置，点击备份。</p>
                    </div>
                """
            },
            {
                "name": "🎭 主题系统",
                "category": "设置相关",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p>6种精美主题，一键切换：</p>
                        <ul style="margin: 8px 0; padding-left: 20px;">
                            <li style="margin: 8px 0;">默认蓝色 - 清新优雅</li>
                            <li style="margin: 8px 0;">活力橙色 - 热情奔放</li>
                            <li style="margin: 8px 0;">商务深蓝 - 专业稳重</li>
                            <li style="margin: 8px 0;">护眼豆沙绿 - 保护视力</li>
                            <li style="margin: 8px 0;">樱花粉 - 温馨甜美</li>
                            <li style="margin: 8px 0;">暗黑模式 - 夜间友好。</li>
                        </ul>
                    </div>
                    <div style="background-color: #fff7e6; padding: 12px 15px; border-radius: 6px; border-left: 4px solid #e6a23c; margin: 10px 0;">
                        <strong>💡 提示</strong>：免费版只能使用默认蓝色主题，升级Pro版可解锁全部主题！如果感觉晚上单元格颜色刺眼可以调低屏幕亮度。
                    </div>
                """
            },
            # 新增：激活与升级
            {
                "name": "🔑 激活与升级",
                "category": "激活相关",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>如何升级到 Pro 版？</strong><br>
                        点击主窗口右上角的「Pro版」按钮，在弹出的对话框中复制设备编码并发送给客服（微信 fangbaby2233 或 QQ 2818491757），获取激活码后粘贴到对话框即可激活。</p>
                        <p><strong>激活后有哪些功能？</strong><br>
                        • 无限制编辑 Excel/Word<br>
                        • 使用所有主题（暗黑、樱花粉等）<br>
                        • 完整的工具箱（批量处理、OCR、音频转换等）<br>
                        • 符号面板和公式助手全功能<br>
                    </div>
                """
            },
            # 新增：自定义符号
            {
                "name": "⚙️ 自定义符号",
                "category": "符号处理",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>如何添加自定义符号？</strong><br>
                        打开「设置」→「符号设置」，在下方"新增符号"区域输入符号名称（如"括号"）和符号内容（如"（）"），点击添加即可。添加后会自动出现在符号选择区。</p>
                        <p><strong>如何修改或删除自定义符号？</strong><br>
                        在符号列表中选中目标符号，点击「编辑」或「删除选中」按钮。注意：默认符号只能隐藏或修改内容（通过编辑覆盖），不能删除。</p>
                        <p><strong>如何恢复所有默认符号？</strong><br>
                        在符号设置页面点击「恢复所有默认符号」即可。</p>
                    </div>
                """
            },
            # 新增：Excel/Word常见问题
            {
                "name": "📂 Excel/Word 编辑常见问题",
                "category": "表格编辑",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>为什么我无法编辑单元格？</strong><br>
                        免费版只能查看 Excel，编辑功能需要 Pro 版。请升级后重新打开文件。</p>
                        <p><strong>Word 文档打开后格式乱了怎么办？</strong><br>
                        本软件目前主要支持纯文本和基础格式（加粗、颜色等），复杂表格、图片可能无法完美保留。建议使用 Word 本身进行复杂排版。</p>
                        <p><strong>保存时提示文件被占用？</strong><br>
                        请关闭 Excel 或 Word 中打开的同名文件，然后再保存。</p>
                    </div>
                """
            },
            # 新增：备份与恢复
            {
                "name": "💾 备份与恢复",
                "category": "设置相关",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>如何备份我的配置？</strong><br>
                        打开「设置」→「备份恢复」，选择要备份的内容（配置文件、自定义符号、剪贴板历史等），设置备份位置，点击「立即备份」。</p>
                        <p><strong>如何从备份恢复？</strong><br>
                        在备份列表中选择一个备份文件，点击「从备份恢复」。恢复后需要重启软件生效。</p>
                        <p><strong>自动备份如何设置？</strong><br>
                        勾选「自动备份」，选择频率和保留份数，软件会在后台定期自动备份。</p>
                    </div>
                """
            },
            # 新增：主题与界面
            {
                "name": "🎨 主题与界面",
                "category": "设置相关",
                "icon": "",
                "content": """
                    <div style="background-color: #f5f7fa; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #409eff;">
                        <p><strong>如何切换主题？</strong><br>
                        打开「设置」→「界面设置」，在"外观主题"下拉框中选择喜欢的主题。部分主题需要 Pro 版才能使用。</p>
                        <p><strong>字体和缩放怎么调整？</strong><br>
                        在同一页面可以设置界面字体、字号以及窗口缩放比例。</p>
                        <p><strong>暗黑模式怎么开启？</strong><br>
                        选择「暗黑模式」主题即可。</p>
                        <p><strong>字体怎么设置？</strong><br>
                        在"字体"下拉框中选择喜欢的字体，字号在"字号"下拉框中选择。推荐微软雅黑字体，字号建议12-14px，缩放125%，布局模式宽松。</p>
                    </div>
                """
            }
        ]
        # 填充列表
        self.help_list_widget.clear()
        for item in self.help_data:
            self.help_list_widget.addItem(item["name"])
        if self.help_list_widget.count() > 0:
            self.help_list_widget.setCurrentRow(0)
    
    def filter_help_items(self):
        search_text = self.help_search.text().lower()
        category = self.help_category_combo.currentText()
        for i in range(self.help_list_widget.count()):
            item = self.help_list_widget.item(i)
            help_item = self.help_data[i]
            show = True
            if category != "全部" and help_item.get("category") != category:
                show = False
            if search_text:
                if (search_text not in help_item["name"].lower() and
                    search_text not in help_item["content"].lower()):
                    show = False
            item.setHidden(not show)
    
    def show_help_detail(self, index):
        if index < 0 or index >= len(self.help_data):
            return
        help_item = self.help_data[index]
        # 设置右侧唯一标题
        self.help_detail_title.setText(f"{help_item.get('icon', '')} {help_item['name']}")
        self.help_detail_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {self.theme_manager.get_theme()['primary']};")
        
        # 获取当前主题的颜色
        theme = self.theme_manager.get_theme()
        card_bg = theme["card"]
        text_color = theme["text"]
        text_secondary = theme["text_secondary"]
        border = theme["border"]
        primary = theme["primary"]
        
        # 提取原始 HTML 内容
        content = help_item['content']
        
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
        
        # 自动替换所有颜色
        for old_color, new_color in color_map.items():
            content = content.replace(old_color, new_color)
        
        # 生成最终 HTML
        final_html = f"""
        <div style="font-family: 'Microsoft YaHei', sans-serif; font-size: 16px; line-height: 1.8; color: {text_color}; background-color: {card_bg};">
            {content}
        </div>
        """
        self.help_detail_content.setHtml(final_html)
    
    def show_guide(self):
        """启动问题解决页面的新手引导"""
        if self.main_window and hasattr(self.main_window, 'guide_manager'):
            self.main_window.guide_manager.show_guide_for_tab(5)
    
    def apply_theme(self):
        if self.theme_manager:
            theme = self.theme_manager.get_theme()
            self.setStyleSheet(f"QFrame.main-card {{ background-color: {theme['card']}; border: 1px solid {theme['border']}; }}")
            current_row = self.help_list_widget.currentRow()
            if current_row >= 0:
                self.show_help_detail(current_row)
