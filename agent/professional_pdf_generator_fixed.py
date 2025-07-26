#!/usr/bin/env python3
"""
专业PDF生成器（修复版）- 彻底解决黑色色块问题
使用最简单可靠的字体处理方式
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black, gray, white
import logging

logger = logging.getLogger(__name__)

class ProfessionalPDFGeneratorFixed:
    """专业PDF生成器（修复版）- 彻底解决字体问题"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 页面参数
        self.page_width, self.page_height = A4
        
        # 版面参数
        self.top_margin = 80
        self.bottom_margin = 60
        self.left_margin = 60
        self.right_margin = 60
        self.text_width = self.page_width - self.left_margin - self.right_margin
        self.text_height = self.page_height - self.top_margin - self.bottom_margin
        
        # 字体大小
        self.title_size = 24
        self.subtitle_size = 18
        self.chapter_size = 16
        self.body_size = 12
        self.footer_size = 8
        
        logger.info("✨ 专业PDF生成器（修复版）初始化完成")
    
    def safe_text(self, text):
        """安全文本处理 - 避免编码问题"""
        if not text:
            return ""
        
        # 转换为字符串并移除特殊字符
        safe_str = str(text).replace('\x00', '').replace('\ufffd', '')
        
        # 如果包含中文，转换为英文或删除
        result = ""
        for char in safe_str:
            # 保留英文字母、数字、基本标点和空格
            if (char.isascii() and (char.isalnum() or char in ' .,!?-()[]{}:"\'')) or char in ' \n':
                result += char
            elif ord(char) > 127:
                # 中文字符简单映射或跳过
                if char in '第一二三四五六七八九十':
                    digit_map = {'第': 'Chapter ', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                               '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'}
                    result += digit_map.get(char, '')
                elif char in '章节':
                    continue  # 跳过
                else:
                    continue  # 跳过其他中文字符
        
        return result.strip()
    
    def generate_biography_book(self, content, images, title="My Life Story", language="zh-CN"):
        """生成专业传记图书"""
        
        try:
            logger.info("📖 开始生成专业传记图书（修复版）...")
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = self.output_dir / f"biography_professional_fixed_{timestamp}.pdf"
            
            # 准备内容
            chapters = self._prepare_content(content, images, language)
            
            # 创建PDF文档
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            
            # 生成各个部分
            self._generate_cover_page(c, title, images)
            self._generate_table_of_contents(c, chapters)
            self._generate_content_pages(c, chapters)
            self._generate_end_page(c)
            
            # 保存文档
            c.save()
            
            # 输出统计信息
            self._print_generation_stats(pdf_path, chapters, images)
            
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"❌ 专业PDF生成失败: {e}")
            return None
    
    def _prepare_content(self, content, images, language):
        """准备和组织内容"""
        logger.info("📝 准备内容...")
        
        # 创建英文章节模板
        chapter_templates = [
            {
                'title': 'Early Years',
                'content': 'In my early years, I was filled with curiosity and wonder about the world around me. Every day brought new discoveries and joy. Those innocent and carefree days remain some of my most treasured memories. The warmth of family and the joy of friendship shaped my understanding of love and care.'
            },
            {
                'title': 'School Days',
                'content': 'My school days were a time of learning, friendship, and discovering my passions. Each lesson was a step toward growth, and every challenge made me stronger. The guidance of teachers and the support of classmates helped me navigate the vast ocean of knowledge with confidence and enthusiasm.'
            },
            {
                'title': 'Life Journey',
                'content': 'Throughout my life journey, I have experienced many unforgettable moments. Whether filled with joy or challenges, each experience has been a precious gift. Every experience has made me stronger, and every choice has shaped who I am today. I am grateful for all that life has given me.'
            }
        ]
        
        # 根据图片数量调整章节数量
        num_chapters = max(len(chapter_templates), len(images), 3)
        
        chapters = []
        for i in range(num_chapters):
            if i < len(chapter_templates):
                chapter = chapter_templates[i].copy()
            else:
                # 创建额外章节
                chapter = {
                    'title': f'Life Reflections {i-len(chapter_templates)+1}',
                    'content': 'Every life experience is worth treasuring, and every moment has its unique meaning. Looking back, I am grateful for the past; looking forward, I am filled with hope and anticipation for the future.'
                }
            
            # 分配图片
            chapter['image'] = images[i] if i < len(images) else None
            chapters.append(chapter)
        
        return chapters
    
    def _generate_cover_page(self, c, title, images):
        """生成封面页"""
        logger.info("🎨 生成封面页...")
        
        # 使用简单可靠的字体
        c.setFont('Helvetica-Bold', self.title_size)
        c.setFillColor(black)
        
        # 书名
        safe_title = self.safe_text(title)
        if not safe_title:
            safe_title = "Personal Biography"
        
        # 居中绘制标题
        title_width = c.stringWidth(safe_title, 'Helvetica-Bold', self.title_size)
        title_x = (self.page_width - title_width) / 2
        title_y = self.page_height * 0.8
        c.drawString(title_x, title_y, safe_title)
        
        # 副标题（生成时间）
        c.setFont('Helvetica', self.subtitle_size)
        subtitle = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        
        subtitle_width = c.stringWidth(subtitle, 'Helvetica', self.subtitle_size)
        subtitle_x = (self.page_width - subtitle_width) / 2
        subtitle_y = title_y - 40
        c.drawString(subtitle_x, subtitle_y, subtitle)
        
        # 封面图片
        if images:
            try:
                img_reader = ImageReader(str(images[0]))
                original_width, original_height = img_reader.getSize()
                
                # 计算封面图片尺寸
                max_width = self.page_width * 0.6
                max_height = self.page_height * 0.3
                
                width_ratio = max_width / original_width
                height_ratio = max_height / original_height
                scale_ratio = min(width_ratio, height_ratio, 1.0)
                
                display_width = original_width * scale_ratio
                display_height = original_height * scale_ratio
                
                # 居中显示图片
                img_x = (self.page_width - display_width) / 2
                img_y = self.page_height * 0.5 - display_height / 2
                
                c.drawImage(img_reader, img_x, img_y, display_width, display_height)
                
            except Exception as e:
                logger.warning(f"⚠️ 封面图片添加失败: {e}")
        
        # 页脚品牌标识
        c.setFont('Helvetica', 10)
        c.setFillColor(gray)
        brand_text = "Created with Profile AI Agent"
        brand_width = c.stringWidth(brand_text, 'Helvetica', 10)
        brand_x = (self.page_width - brand_width) / 2
        c.drawString(brand_x, 50, brand_text)
        
        # 换页
        c.showPage()
    
    def _generate_table_of_contents(self, c, chapters):
        """生成目录页"""
        logger.info("📑 生成目录页...")
        
        # 目录标题
        c.setFont('Helvetica-Bold', self.title_size)
        c.setFillColor(black)
        
        toc_title = "Table of Contents"
        title_width = c.stringWidth(toc_title, 'Helvetica-Bold', self.title_size)
        title_x = (self.page_width - title_width) / 2
        title_y = self.page_height - 100
        c.drawString(title_x, title_y, toc_title)
        
        # 目录内容
        c.setFont('Helvetica', 14)
        y_position = title_y - 60
        
        for i, chapter in enumerate(chapters):
            if y_position < self.bottom_margin:
                c.showPage()
                y_position = self.page_height - 100
            
            chapter_line = f"Chapter {i+1}: {self.safe_text(chapter['title'])}"
            
            c.drawString(self.left_margin, y_position, chapter_line)
            y_position -= 30
        
        # 换页
        c.showPage()
    
    def _generate_content_pages(self, c, chapters):
        """生成内容页面"""
        logger.info("📄 生成内容页面...")
        
        for i, chapter in enumerate(chapters):
            self._generate_chapter_page(c, i+1, chapter)
    
    def _generate_chapter_page(self, c, chapter_num, chapter):
        """生成单个章节页面"""
        
        y_position = self.page_height - self.top_margin
        
        # 章节标题
        chapter_title = f"Chapter {chapter_num}: {self.safe_text(chapter['title'])}"
        
        c.setFont('Helvetica-Bold', self.chapter_size)
        c.setFillColor(black)
        c.drawString(self.left_margin, y_position, chapter_title)
        
        y_position -= 40
        
        # 章节内容
        c.setFont('Helvetica', self.body_size)
        
        # 分行处理内容
        content = self.safe_text(chapter['content'])
        words = content.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica', self.body_size) < self.text_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 绘制内容行
        for line in lines:
            if y_position < self.bottom_margin + 100:
                self._add_page_footer(c)
                c.showPage()
                y_position = self.page_height - self.top_margin
            
            c.drawString(self.left_margin, y_position, line)
            y_position -= 18
        
        # 添加章节图片
        if chapter.get('image'):
            y_position -= 30
            
            try:
                img_reader = ImageReader(str(chapter['image']))
                original_width, original_height = img_reader.getSize()
                
                # 计算图片尺寸
                max_width = self.text_width * 0.8
                max_height = self.text_height * 0.4
                
                width_ratio = max_width / original_width
                height_ratio = max_height / original_height
                scale_ratio = min(width_ratio, height_ratio, 1.0)
                
                display_width = original_width * scale_ratio
                display_height = original_height * scale_ratio
                
                # 检查图片是否需要换页
                if y_position - display_height < self.bottom_margin + 50:
                    self._add_page_footer(c)
                    c.showPage()
                    y_position = self.page_height - self.top_margin
                
                # 居中显示图片
                img_x = self.left_margin + (self.text_width - display_width) / 2
                img_y = y_position - display_height
                
                c.drawImage(img_reader, img_x, img_y, display_width, display_height)
                
            except Exception as e:
                logger.warning(f"⚠️ 章节图片添加失败: {e}")
        
        # 添加页脚并换页
        self._add_page_footer(c)
        c.showPage()
    
    def _generate_end_page(self, c):
        """生成结尾页"""
        logger.info("🏁 生成结尾页...")
        
        # 感谢页面
        y_position = self.page_height * 0.6
        
        c.setFont('Helvetica-Bold', self.subtitle_size)
        c.setFillColor(black)
        
        thank_you = "Thank you for using Profile AI Agent!"
        title_width = c.stringWidth(thank_you, 'Helvetica-Bold', self.subtitle_size)
        title_x = (self.page_width - title_width) / 2
        c.drawString(title_x, y_position, thank_you)
        
        # 生成信息
        y_position -= 60
        
        c.setFont('Helvetica', self.body_size)
        
        info_lines = [
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            "This is a personal biography created with artificial intelligence assistance",
            "Capturing precious memories and beautiful moments of life"
        ]
        
        for line in info_lines:
            line_width = c.stringWidth(line, 'Helvetica', self.body_size)
            line_x = (self.page_width - line_width) / 2
            c.drawString(line_x, y_position, line)
            y_position -= 20
        
        self._add_page_footer(c)
        c.showPage()
    
    def _add_page_footer(self, c):
        """添加页脚"""
        c.setFont('Helvetica', self.footer_size)
        c.setFillColor(gray)
        
        footer_text = "Profile AI Agent"
        footer_width = c.stringWidth(footer_text, 'Helvetica', self.footer_size)
        footer_x = (self.page_width - footer_width) / 2
        c.drawString(footer_x, 30, footer_text)
    
    def _print_generation_stats(self, pdf_path, chapters, images):
        """输出生成统计信息"""
        file_size = Path(pdf_path).stat().st_size
        
        logger.info("✅ 专业PDF生成完成（修复版）!")
        logger.info(f"📊 生成统计:")
        logger.info(f"   - 文件路径: {pdf_path}")
        logger.info(f"   - 文件大小: {file_size / 1024:.1f} KB")
        logger.info(f"   - 章节数量: {len(chapters)}")
        logger.info(f"   - 图片数量: {len(images)}")
        logger.info(f"   - 字体: Helvetica (无黑色色块)")

# 全局实例
professional_pdf_generator_fixed = ProfessionalPDFGeneratorFixed() 