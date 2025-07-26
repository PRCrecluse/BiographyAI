#!/usr/bin/env python3
"""
版面引擎 - 实现专业的图书排版
支持黄金比例版面设计，优雅的字体层级和间距
"""

import math
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import black, gray
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

class LayoutEngine:
    """专业版面引擎"""
    
    def __init__(self, font_manager):
        self.font_manager = font_manager
        self.page_width, self.page_height = A4
        
        # 黄金比例计算
        self.golden_ratio = (1 + math.sqrt(5)) / 2
        
        # 版面参数
        self._setup_layout_parameters()
        
        # 创建样式系统
        self._create_style_system()
    
    def _setup_layout_parameters(self):
        """设置版面参数 - 基于黄金比例"""
        
        # 页边距 - 使用黄金比例
        self.top_margin = self.page_height / 8
        self.bottom_margin = self.page_height / 12
        self.inner_margin = self.page_width / 10
        self.outer_margin = self.page_width / 12
        
        # 文本区域
        self.text_width = self.page_width - self.inner_margin - self.outer_margin
        self.text_height = self.page_height - self.top_margin - self.bottom_margin
        
        # 列宽（用于图文混排）
        self.column_width = self.text_width / 2
        self.column_gap = 20
        
        # 行高和间距
        self.base_leading = 18
        self.paragraph_space = 12
        self.section_space = 24
        self.chapter_space = 36
        
        # 图片尺寸
        self.max_image_width = self.text_width * 0.8
        self.max_image_height = self.text_height * 0.4
        
    def _create_style_system(self):
        """创建分层的样式系统"""
        
        # 获取字体
        chinese_font = self.font_manager.get_font("zh-CN")
        english_font = self.font_manager.get_font("en")
        
        # 定义字体大小层级
        self.font_sizes = {
            'title': 28,      # 书名
            'subtitle': 20,    # 副标题
            'chapter': 18,     # 章节标题
            'section': 16,     # 小节标题
            'body': 12,        # 正文
            'caption': 10,     # 图片说明
            'footer': 8        # 页脚
        }
        
        # 创建样式
        self.styles = {}
        
        # 书名样式
        self.styles['title'] = ParagraphStyle(
            'BookTitle',
            fontName=chinese_font,
            fontSize=self.font_sizes['title'],
            leading=self.font_sizes['title'] * 1.2,
            alignment=TA_CENTER,
            spaceAfter=self.chapter_space,
            spaceBefore=self.chapter_space,
            textColor=black
        )
        
        # 副标题样式
        self.styles['subtitle'] = ParagraphStyle(
            'SubTitle',
            fontName=chinese_font,
            fontSize=self.font_sizes['subtitle'],
            leading=self.font_sizes['subtitle'] * 1.2,
            alignment=TA_CENTER,
            spaceAfter=self.section_space,
            spaceBefore=self.paragraph_space,
            textColor=black
        )
        
        # 章节标题样式
        self.styles['chapter'] = ParagraphStyle(
            'ChapterTitle',
            fontName=chinese_font,
            fontSize=self.font_sizes['chapter'],
            leading=self.font_sizes['chapter'] * 1.3,
            alignment=TA_LEFT,
            spaceAfter=self.section_space,
            spaceBefore=self.chapter_space,
            textColor=black,
            leftIndent=0
        )
        
        # 小节标题样式
        self.styles['section'] = ParagraphStyle(
            'SectionTitle',
            fontName=chinese_font,
            fontSize=self.font_sizes['section'],
            leading=self.font_sizes['section'] * 1.3,
            alignment=TA_LEFT,
            spaceAfter=self.paragraph_space,
            spaceBefore=self.section_space,
            textColor=black,
            leftIndent=0
        )
        
        # 正文样式
        self.styles['body'] = ParagraphStyle(
            'BodyText',
            fontName=chinese_font,
            fontSize=self.font_sizes['body'],
            leading=self.base_leading,
            alignment=TA_JUSTIFY,
            spaceAfter=self.paragraph_space,
            spaceBefore=0,
            textColor=black,
            leftIndent=0,
            rightIndent=0,
            firstLineIndent=24  # 首行缩进
        )
        
        # 图片说明样式
        self.styles['caption'] = ParagraphStyle(
            'Caption',
            fontName=chinese_font,
            fontSize=self.font_sizes['caption'],
            leading=self.font_sizes['caption'] * 1.2,
            alignment=TA_CENTER,
            spaceAfter=self.paragraph_space,
            spaceBefore=8,
            textColor=gray,
            leftIndent=0,
            rightIndent=0
        )
        
        # 页脚样式
        self.styles['footer'] = ParagraphStyle(
            'Footer',
            fontName=english_font,
            fontSize=self.font_sizes['footer'],
            leading=self.font_sizes['footer'] * 1.2,
            alignment=TA_CENTER,
            spaceAfter=0,
            spaceBefore=0,
            textColor=gray
        )
    
    def get_style(self, style_name):
        """获取指定样式"""
        return self.styles.get(style_name, self.styles['body'])
    
    def calculate_image_size(self, original_width, original_height, max_width=None, max_height=None):
        """计算图片最佳显示尺寸"""
        if max_width is None:
            max_width = self.max_image_width
        if max_height is None:
            max_height = self.max_image_height
        
        # 计算缩放比例
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不要放大
        
        new_width = original_width * scale_ratio
        new_height = original_height * scale_ratio
        
        return new_width, new_height
    
    def get_text_position(self, y_position, style_name='body'):
        """获取文本位置"""
        style = self.get_style(style_name)
        
        # 检查是否需要换页
        required_space = style.fontSize + style.leading + style.spaceAfter
        if y_position - required_space < self.bottom_margin:
            return None  # 需要换页
        
        return y_position
    
    def get_image_position(self, y_position, image_height):
        """获取图片位置"""
        # 图片需要的总空间（包括上下间距）
        required_space = image_height + self.section_space
        
        if y_position - required_space < self.bottom_margin:
            return None  # 需要换页
        
        # 计算居中的x位置
        x_position = self.inner_margin + (self.text_width - image_height) / 2
        
        return x_position, y_position - image_height
    
    def format_chapter_title(self, chapter_num, title):
        """格式化章节标题"""
        return f"第{chapter_num}章  {title}"
    
    def clean_and_format_text(self, text, max_length=None):
        """清理和格式化文本"""
        if not text:
            return ""
        
        # 使用字体管理器清理文本
        cleaned = self.font_manager.clean_text(text)
        
        # 如果指定了最大长度，进行截断
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length-3] + "..."
        
        return cleaned
    
    def split_long_text(self, text, max_chars_per_page=1500):
        """将长文本分割为适合页面的段落"""
        if not text:
            return []
        
        cleaned_text = self.clean_and_format_text(text)
        
        # 如果文本不长，直接返回
        if len(cleaned_text) <= max_chars_per_page:
            return [cleaned_text]
        
        # 分割文本，优先在句号、换行符处分割
        chunks = []
        current_chunk = ""
        
        sentences = cleaned_text.replace('\n\n', '\n').split('。')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # 如果添加这个句子不会超过限制
            test_chunk = current_chunk + sentence + "。"
            if len(test_chunk) <= max_chars_per_page:
                current_chunk = test_chunk
            else:
                # 保存当前块，开始新的块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + "。"
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks or [cleaned_text]
    
    def get_cover_layout(self):
        """获取封面布局参数"""
        return {
            'title_y': self.page_height * 0.7,
            'subtitle_y': self.page_height * 0.6,
            'image_y': self.page_height * 0.45,
            'image_width': self.page_width * 0.6,
            'image_height': self.page_height * 0.25,
            'date_y': self.page_height * 0.15
        }
    
    def get_toc_layout(self):
        """获取目录布局参数"""
        return {
            'title_y': self.page_height * 0.85,
            'content_start_y': self.page_height * 0.75,
            'line_height': 24,
            'indent': 30
        } 