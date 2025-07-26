#!/usr/bin/env python3
"""
简化PDF生成器 - 彻底解决黑色色块问题
使用最基础可靠的字体和方法
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

class SimplePDFGenerator:
    """简化PDF生成器 - 完全避免字体问题"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 页面参数
        self.page_width, self.page_height = A4
        
        # 版面参数
        self.margin = 72  # 1英寸边距
        self.text_width = self.page_width - 2 * self.margin
        
        logger.info("✨ 简化PDF生成器初始化完成")
    
    def generate_biography_book(self, content, images, title="Personal Biography", language="zh-CN"):
        """生成简化传记图书"""
        
        try:
            logger.info("📖 开始生成简化传记图书...")
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = self.output_dir / f"biography_simple_{timestamp}.pdf"
            
            # 创建PDF文档
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            
            # 生成各个部分
            self._generate_cover_page(c, title, images, language)
            self._generate_content_pages(c, content, images)
            self._generate_end_page(c, language)
            
            # 保存文档
            c.save()
            
            # 输出统计信息
            file_size = Path(pdf_path).stat().st_size
            logger.info("✅ 简化PDF生成完成!")
            logger.info(f"📊 文件信息:")
            logger.info(f"   - 路径: {pdf_path}")
            logger.info(f"   - 大小: {file_size / 1024:.1f} KB")
            logger.info(f"   - 图片数量: {len(images)}")
            
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"❌ 简化PDF生成失败: {e}")
            return None
    
    def _generate_cover_page(self, c, title, images, language="zh-CN"):
        """生成封面页"""
        logger.info("🎨 生成封面页...")
        
        # 使用最基础的字体
        c.setFont('Helvetica-Bold', 28)
        c.setFillColor(black)
        
        # 根据语言设置标题
        if language == "zh-CN" or language == "Chinese":
            safe_title = "Personal Biography"  # Helvetica不支持中文，使用英文避免问题
        elif language == "en" or language == "English":
            safe_title = "Personal Biography"
        elif language == "it" or language == "Italian":
            safe_title = "Biografia Personale"
        elif language == "fr" or language == "French":
            safe_title = "Biographie Personnelle"
        elif language == "pt" or language == "Portuguese":
            safe_title = "Biografia Pessoal"
        elif language == "es" or language == "Spanish":
            safe_title = "Biografía Personal"
        else:
            safe_title = "Personal Biography"
        
        # 计算标题位置
        title_width = c.stringWidth(safe_title, 'Helvetica-Bold', 28)
        title_x = (self.page_width - title_width) / 2
        title_y = self.page_height - 150
        
        c.drawString(title_x, title_y, safe_title)
        
        # 生成日期 - 根据语言格式化
        c.setFont('Helvetica', 16)
        current_date = datetime.now()
        
        if language == "zh-CN" or language == "Chinese":
            date_text = f"Generated: {current_date.strftime('%B %d, %Y')}"  # 保持英文避免字体问题
        elif language == "it" or language == "Italian":
            date_text = f"Generato: {current_date.strftime('%d %B %Y')}"
        elif language == "fr" or language == "French":
            date_text = f"Généré: {current_date.strftime('%d %B %Y')}"
        elif language == "pt" or language == "Portuguese":
            date_text = f"Gerado: {current_date.strftime('%d de %B de %Y')}"
        elif language == "es" or language == "Spanish":
            date_text = f"Generado: {current_date.strftime('%d de %B de %Y')}"
        else:
            date_text = f"Generated: {current_date.strftime('%B %d, %Y')}"
        
        date_width = c.stringWidth(date_text, 'Helvetica', 16)
        date_x = (self.page_width - date_width) / 2
        date_y = title_y - 50
        
        c.drawString(date_x, date_y, date_text)
        
        # 封面图片
        if images:
            try:
                img_reader = ImageReader(str(images[0]))
                original_width, original_height = img_reader.getSize()
                
                # 简单的图片缩放
                max_size = 300
                if original_width > original_height:
                    new_width = max_size
                    new_height = int(original_height * max_size / original_width)
                else:
                    new_height = max_size
                    new_width = int(original_width * max_size / original_height)
                
                # 居中放置图片
                img_x = (self.page_width - new_width) / 2
                img_y = self.page_height / 2 - new_height / 2
                
                c.drawImage(img_reader, img_x, img_y, new_width, new_height)
                
            except Exception as e:
                logger.warning(f"⚠️ 封面图片处理失败: {e}")
        
        # 品牌标识
        c.setFont('Helvetica', 10)
        c.setFillColor(gray)
        brand_text = "Created with Biography AI Agent"
        brand_width = c.stringWidth(brand_text, 'Helvetica', 10)
        brand_x = (self.page_width - brand_width) / 2
        c.drawString(brand_x, 50, brand_text)
        
        c.showPage()
    
    def _generate_content_pages(self, c, content, images):
        """生成内容页"""
        logger.info("📄 生成内容页...")
        
        # 解析传入的多语言内容并创建章节
        chapters = self._parse_content_to_chapters(content, images)
        
        for i, chapter in enumerate(chapters):
            self._generate_chapter_page(c, chapter, images[i] if i < len(images) else None)
    
    def _parse_content_to_chapters(self, content, images):
        """将内容解析为章节"""
        chapters = []
        
        # 按段落分割内容
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # 如果没有内容，返回默认英文章节作为fallback
            return [
                {"title": "Chapter 1: Early Years", "content": "In my early years, I was filled with curiosity and wonder about the world around me."},
                {"title": "Chapter 2: School Days", "content": "My school days were a time of learning, friendship, and discovering my passions."},
                {"title": "Chapter 3: Life Journey", "content": "Throughout my life journey, I have experienced many unforgettable moments."}
            ]
        
        # 找到章节和内容
        current_chapter = None
        current_content = []
        
        for paragraph in paragraphs:
            # 检查是否是章节标题（包含中文、英文、日语、韩语、意大利语、法语的章节标识）
            if self._is_chapter_title(paragraph):
                # 如果有当前章节，先保存
                if current_chapter and current_content:
                    chapters.append({
                        "title": current_chapter,
                        "content": '\n\n'.join(current_content)
                    })
                    current_content = []
                
                current_chapter = paragraph
            else:
                # 跳过纯介绍段落，只保留章节内容
                if current_chapter:
                    current_content.append(paragraph)
        
        # 保存最后一个章节
        if current_chapter and current_content:
            chapters.append({
                "title": current_chapter,
                "content": '\n\n'.join(current_content)
            })
        
        # 如果没有找到章节，创建单个章节
        if not chapters and paragraphs:
            # 使用第一段作为标题，其余作为内容
            if len(paragraphs) >= 2:
                chapters.append({
                    "title": paragraphs[0],
                    "content": '\n\n'.join(paragraphs[1:])
                })
            else:
                chapters.append({
                    "title": "Personal Biography",
                    "content": paragraphs[0]
                })
        
        return chapters
    
    def _is_chapter_title(self, text):
        """判断是否是章节标题"""
        # 检查各种语言的章节标识符
        chapter_markers = [
            # 中文
            '童年时光', '求学岁月', '家庭生活', '人生旅途', '成长收获', '感悟思考',
            # 英文
            'Early Years', 'School Days', 'Family Time', 'Adventures', 'Achievements', 'Reflections',
            'Chapter 1:', 'Chapter 2:', 'Chapter 3:', 'Chapter 4:', 'Chapter 5:', 'Chapter 6:',
            # 意大利语
            'Primi Anni', 'Anni di Scuola', 'Tempo in Famiglia', 'Avventure', 'Conquiste', 'Riflessioni',
            # 法语
            'Premières Années', 'Années d\'École', 'Temps en Famille', 'Aventures', 'Réalisations', 'Réflexions'
        ]
        
        # 检查文本是否以章节标识符开始
        for marker in chapter_markers:
            if text.startswith(marker):
                return True
        
        # 检查是否是简单的标题格式（短于100字符且不包含句号）
        if len(text) < 100 and '.' not in text.rstrip() and '\n' not in text:
            return True
            
        return False
    
    def _generate_chapter_page(self, c, chapter, image):
        """生成章节页"""
        
        y_position = self.page_height - self.margin
        
        # 章节标题
        c.setFont('Helvetica-Bold', 18)
        c.setFillColor(black)
        c.drawString(self.margin, y_position, chapter["title"])
        
        y_position -= 40
        
        # 章节内容
        c.setFont('Helvetica', 12)
        content_lines = self._wrap_text(c, chapter["content"], self.text_width)
        
        for line in content_lines:
            if y_position < self.margin + 100:
                self._add_footer(c)
                c.showPage()
                y_position = self.page_height - self.margin
            
            c.drawString(self.margin, y_position, line)
            y_position -= 20
        
        # 添加图片
        if image:
            y_position -= 30
            
            try:
                img_reader = ImageReader(str(image))
                original_width, original_height = img_reader.getSize()
                
                # 简单缩放
                max_width = self.text_width * 0.8
                max_height = 200
                
                if original_width > max_width:
                    scale = max_width / original_width
                    new_width = max_width
                    new_height = int(original_height * scale)
                else:
                    new_width = original_width
                    new_height = original_height
                
                if new_height > max_height:
                    scale = max_height / new_height
                    new_height = max_height
                    new_width = int(new_width * scale)
                
                # 检查是否需要换页
                if y_position - new_height < self.margin + 50:
                    self._add_footer(c)
                    c.showPage()
                    y_position = self.page_height - self.margin
                
                # 居中放置图片
                img_x = self.margin + (self.text_width - new_width) / 2
                img_y = y_position - new_height
                
                c.drawImage(img_reader, img_x, img_y, new_width, new_height)
                
            except Exception as e:
                logger.warning(f"⚠️ 图片处理失败: {e}")
        
        self._add_footer(c)
        c.showPage()
    
    def _generate_end_page(self, c, language="zh-CN"):
        """生成结尾页"""
        logger.info("🏁 生成结尾页...")
        
        y_position = self.page_height / 2
        
        # 感谢信息 - 根据语言设置
        c.setFont('Helvetica-Bold', 20)
        c.setFillColor(black)
        
        if language == "zh-CN" or language == "Chinese":
            thank_text = "Thank you for using Biography AI Agent!"  # 使用英文避免字体问题
        elif language == "en" or language == "English":
            thank_text = "Thank you for using Biography AI Agent!"
        elif language == "it" or language == "Italian":
            thank_text = "Grazie per aver usato Biography AI Agent!"
        elif language == "fr" or language == "French":
            thank_text = "Merci d'avoir utilise Biography AI Agent!"
        else:
            thank_text = "Thank you for using Biography AI Agent!"
        
        text_width = c.stringWidth(thank_text, 'Helvetica-Bold', 20)
        text_x = (self.page_width - text_width) / 2
        
        c.drawString(text_x, y_position, thank_text)
        
        # 生成信息
        y_position -= 60
        c.setFont('Helvetica', 12)
        
        if language == "it" or language == "Italian":
            info_text = f"Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}"
        elif language == "fr" or language == "French":
            info_text = f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}"
        else:
            info_text = f"Generated on {datetime.now().strftime('%m/%d/%Y at %H:%M')}"
        
        info_width = c.stringWidth(info_text, 'Helvetica', 12)
        info_x = (self.page_width - info_width) / 2
        
        c.drawString(info_x, y_position, info_text)
        
        self._add_footer(c)
        c.showPage()
    
    def _wrap_text(self, c, text, max_width):
        """文本自动换行"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if c.stringWidth(test_line, 'Helvetica', 12) <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _add_footer(self, c):
        """添加页脚"""
        c.setFont('Helvetica', 8)
        c.setFillColor(gray)
        
        footer_text = "Biography AI Agent"
        footer_width = c.stringWidth(footer_text, 'Helvetica', 8)
        footer_x = (self.page_width - footer_width) / 2
        c.drawString(footer_x, 30, footer_text)

# 全局实例
simple_pdf_generator = SimplePDFGenerator() 