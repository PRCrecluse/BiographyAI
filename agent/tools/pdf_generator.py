"""
PDF生成工具
生成专业的个人传记PDF文档
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, black, white, gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from PIL import Image as PILImage

from ..core.models import PDFTemplate, LayoutElement


class PDFGenerator:
    """PDF生成工具"""
    
    def __init__(self):
        self.output_dir = "generated_pdfs"
        self._ensure_output_dir()
        self.templates = self._load_templates()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _load_templates(self) -> Dict[str, PDFTemplate]:
        """加载PDF模板配置"""
        return {
            "classic": PDFTemplate(
                name="经典模板",
                page_size="A4",
                margins={"top": 2*cm, "bottom": 2*cm, "left": 2*cm, "right": 2*cm},
                fonts={"title": "Helvetica-Bold", "body": "Helvetica", "caption": "Helvetica-Oblique"},
                colors={"primary": "#2C3E50", "secondary": "#7F8C8D", "text": "#2C3E50"},
                layout_config={"title_size": 24, "body_size": 12, "caption_size": 10}
            ),
            "modern": PDFTemplate(
                name="现代模板",
                page_size="A4",
                margins={"top": 1.5*cm, "bottom": 1.5*cm, "left": 1.5*cm, "right": 1.5*cm},
                fonts={"title": "Helvetica-Bold", "body": "Helvetica", "caption": "Helvetica-Oblique"},
                colors={"primary": "#3498DB", "secondary": "#E74C3C", "text": "#2C3E50"},
                layout_config={"title_size": 28, "body_size": 11, "caption_size": 9}
            ),
            "elegant": PDFTemplate(
                name="优雅模板",
                page_size="A4",
                margins={"top": 2.5*cm, "bottom": 2.5*cm, "left": 2.5*cm, "right": 2.5*cm},
                fonts={"title": "Times-Bold", "body": "Times-Roman", "caption": "Times-Italic"},
                colors={"primary": "#8E44AD", "secondary": "#F39C12", "text": "#2C3E50"},
                layout_config={"title_size": 22, "body_size": 12, "caption_size": 10}
            )
        }
    
    async def generate_pdf(self, layout_result: Dict[str, Any]) -> str:
        """
        生成PDF文档
        
        Args:
            layout_result: 排版结果数据
            
        Returns:
            str: 生成的PDF文件路径
        """
        try:
            # 获取模板配置
            template_name = layout_result.get("template", "classic")
            template = self.templates.get(template_name, self.templates["classic"])
            
            # 创建PDF文档
            filename = f"biography_{layout_result.get('user_id', 'unknown')}_{asyncio.get_event_loop().time()}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            # 创建文档
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                topMargin=template.margins["top"],
                bottomMargin=template.margins["bottom"],
                leftMargin=template.margins["left"],
                rightMargin=template.margins["right"]
            )
            
            # 创建内容
            story = []
            
            # 添加封面
            story.extend(self._create_cover_page(layout_result, template))
            story.append(PageBreak())
            
            # 添加目录（如果有章节）
            if layout_result.get("chapters"):
                story.extend(self._create_table_of_contents(layout_result, template))
                story.append(PageBreak())
            
            # 添加正文内容
            story.extend(self._create_content_pages(layout_result, template))
            
            # 构建PDF
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            raise Exception(f"生成PDF失败: {str(e)}")
    
    def _create_cover_page(self, layout_result: Dict[str, Any], template: PDFTemplate) -> List:
        """创建封面页"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 创建自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=template.layout_config["title_size"],
            textColor=Color(0, 0, 0),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=Color(0.3, 0.3, 0.3),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # 添加标题
        title = layout_result.get("title", "我的个人传记")
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(title, title_style))
        
        # 添加副标题
        subtitle = layout_result.get("subtitle", "一个人的故事")
        elements.append(Paragraph(subtitle, subtitle_style))
        
        # 添加封面图片（如果有）
        cover_image = layout_result.get("cover_image")
        if cover_image and os.path.exists(cover_image):
            try:
                # 调整图片大小
                img = self._resize_image_for_pdf(cover_image, max_width=4*inch, max_height=3*inch)
                elements.append(Spacer(1, 0.5*inch))
                elements.append(img)
            except Exception as e:
                print(f"添加封面图片失败: {e}")
        
        # 添加生成日期
        import datetime
        date_str = datetime.datetime.now().strftime("%Y年%m月%d日")
        date_style = ParagraphStyle(
            'DateStyle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=Color(0.5, 0.5, 0.5),
            alignment=TA_CENTER
        )
        elements.append(Spacer(1, 2*inch))
        elements.append(Paragraph(date_str, date_style))
        
        return elements
    
    def _create_table_of_contents(self, layout_result: Dict[str, Any], template: PDFTemplate) -> List:
        """创建目录"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 目录标题
        toc_title = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=Color(0, 0, 0),
            alignment=TA_CENTER,
            spaceAfter=30
        )
        elements.append(Paragraph("目录", toc_title))
        
        # 目录项
        toc_style = ParagraphStyle(
            'TOCItem',
            parent=styles['Normal'],
            fontSize=14,
            leftIndent=20,
            spaceAfter=10
        )
        
        chapters = layout_result.get("chapters", [])
        for i, chapter in enumerate(chapters, 1):
            toc_item = f"{i}. {chapter.get('title', f'第{i}章')}"
            elements.append(Paragraph(toc_item, toc_style))
        
        return elements
    
    def _create_content_pages(self, layout_result: Dict[str, Any], template: PDFTemplate) -> List:
        """创建内容页面"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 创建自定义样式
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=Color(0, 0, 0),
            spaceAfter=20,
            spaceBefore=30
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=template.layout_config["body_size"],
            textColor=Color(0.2, 0.2, 0.2),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        )
        
        caption_style = ParagraphStyle(
            'Caption',
            parent=styles['Normal'],
            fontSize=template.layout_config["caption_size"],
            textColor=Color(0.5, 0.5, 0.5),
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        # 处理章节内容
        chapters = layout_result.get("chapters", [])
        if chapters:
            for chapter in chapters:
                # 章节标题
                elements.append(Paragraph(chapter.get("title", ""), heading_style))
                
                # 章节内容
                content = chapter.get("content", "")
                # 分段处理内容
                paragraphs = content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        elements.append(Paragraph(para.strip(), body_style))
                
                # 章节图片
                images = chapter.get("images", [])
                for image_data in images:
                    if isinstance(image_data, dict):
                        image_path = image_data.get("path")
                        caption = image_data.get("caption", "")
                        qr_code = image_data.get("qr_code")
                    else:
                        image_path = image_data
                        caption = ""
                        qr_code = None
                    
                    if image_path and os.path.exists(image_path):
                        # 添加图片
                        try:
                            img = self._resize_image_for_pdf(image_path, max_width=5*inch, max_height=4*inch)
                            elements.append(Spacer(1, 10))
                            elements.append(img)
                            
                            # 添加图片说明
                            if caption:
                                elements.append(Paragraph(caption, caption_style))
                            
                            # 添加二维码（在图片旁边）
                            if qr_code and os.path.exists(qr_code):
                                elements.append(self._create_image_with_qr(image_path, qr_code))
                            
                        except Exception as e:
                            print(f"添加图片失败: {e}")
                
                elements.append(Spacer(1, 30))
        else:
            # 如果没有章节，直接添加内容
            content = layout_result.get("content", "")
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    elements.append(Paragraph(para.strip(), body_style))
        
        return elements
    
    def _resize_image_for_pdf(self, image_path: str, max_width: float, max_height: float) -> Image:
        """调整图片大小适合PDF"""
        try:
            # 使用PIL获取图片尺寸
            with PILImage.open(image_path) as pil_img:
                orig_width, orig_height = pil_img.size
            
            # 计算缩放比例
            width_ratio = max_width / orig_width
            height_ratio = max_height / orig_height
            scale_ratio = min(width_ratio, height_ratio, 1.0)  # 不放大图片
            
            # 计算新尺寸
            new_width = orig_width * scale_ratio
            new_height = orig_height * scale_ratio
            
            # 创建ReportLab图片对象
            img = Image(image_path, width=new_width, height=new_height)
            img.hAlign = 'CENTER'
            
            return img
            
        except Exception as e:
            print(f"调整图片大小失败: {e}")
            # 返回默认大小的图片
            return Image(image_path, width=3*inch, height=2*inch)
    
    def _create_image_with_qr(self, image_path: str, qr_path: str) -> Table:
        """创建图片和二维码的组合布局"""
        try:
            # 调整图片和二维码大小
            main_img = self._resize_image_for_pdf(image_path, max_width=4*inch, max_height=3*inch)
            qr_img = Image(qr_path, width=1*inch, height=1*inch)
            
            # 创建表格布局
            data = [[main_img, qr_img]]
            table = Table(data, colWidths=[4.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            return table
            
        except Exception as e:
            print(f"创建图片二维码组合失败: {e}")
            # 回退到只显示图片
            return self._resize_image_for_pdf(image_path, max_width=5*inch, max_height=4*inch)
    
    async def generate_simple_pdf(self, content: str, title: str = "个人传记") -> str:
        """
        生成简单的PDF文档
        
        Args:
            content: 文本内容
            title: 文档标题
            
        Returns:
            str: 生成的PDF文件路径
        """
        try:
            filename = f"simple_biography_{asyncio.get_event_loop().time()}.pdf"
            pdf_path = os.path.join(self.output_dir, filename)
            
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # 添加标题
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontSize=24,
                textColor=Color(0, 0, 0),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            story.append(Paragraph(title, title_style))
            
            # 添加内容
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=12,
                textColor=Color(0.2, 0.2, 0.2),
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                leading=16
            )
            
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
            
            doc.build(story)
            return pdf_path
            
        except Exception as e:
            raise Exception(f"生成简单PDF失败: {str(e)}")
    
    def get_available_templates(self) -> List[str]:
        """获取可用模板列表"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取模板信息"""
        template = self.templates.get(template_name)
        if template:
            return {
                "name": template.name,
                "page_size": template.page_size,
                "colors": template.colors,
                "fonts": template.fonts
            }
        return None 