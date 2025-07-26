"""
排版引擎
负责图文排版，创建美观的传记布局
"""

import os
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import textwrap

from ..core.models import LayoutElement, BiographySection, ImageAnalysisResult


class LayoutEngine:
    """排版引擎"""
    
    def __init__(self):
        self.page_width = 210  # A4宽度(mm)
        self.page_height = 297  # A4高度(mm)
        self.margin = 20  # 边距(mm)
        self.content_width = self.page_width - 2 * self.margin
        self.content_height = self.page_height - 2 * self.margin
        
        # 排版配置
        self.config = {
            "title_font_size": 24,
            "heading_font_size": 18,
            "body_font_size": 12,
            "caption_font_size": 10,
            "line_height": 1.4,
            "paragraph_spacing": 12,
            "image_max_width": 150,  # mm
            "image_max_height": 100,  # mm
            "qr_size": 30,  # mm
        }
    
    async def create_layout(
        self,
        biography_content: str,
        image_analyses: List[ImageAnalysisResult],
        qr_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        创建完整的传记排版
        
        Args:
            biography_content: 传记文本内容
            image_analyses: 图片分析结果列表
            qr_codes: 二维码路径映射
            
        Returns:
            Dict[str, Any]: 排版结果数据
        """
        try:
            # 解析内容结构
            sections = await self._parse_content_structure(biography_content)
            
            # 分配图片到各个章节
            sections_with_images = self._assign_images_to_sections(sections, image_analyses)
            
            # 创建页面布局
            pages = await self._create_page_layouts(sections_with_images, qr_codes)
            
            # 生成最终布局数据
            layout_result = {
                "title": "我的个人传记",
                "subtitle": "珍贵回忆的记录",
                "template": "classic",
                "user_id": "user_001",
                "chapters": self._format_chapters_for_pdf(sections_with_images, qr_codes),
                "pages": pages,
                "total_pages": len(pages),
                "cover_image": self._select_cover_image(image_analyses)
            }
            
            return layout_result
            
        except Exception as e:
            raise Exception(f"创建排版失败: {str(e)}")
    
    async def _parse_content_structure(self, content: str) -> List[BiographySection]:
        """解析内容结构，分割成章节"""
        sections = []
        
        # 简单的章节分割逻辑（基于段落）
        paragraphs = content.split('\n\n')
        current_section = None
        section_content = []
        section_counter = 1
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 检查是否是新章节的标题（简单启发式规则）
            if (len(para) < 50 and 
                ('第' in para or '章' in para or para.endswith('时期') or 
                 para.endswith('阶段') or para.endswith('岁月'))):
                
                # 保存前一个章节
                if current_section and section_content:
                    current_section.content = '\n\n'.join(section_content)
                    sections.append(current_section)
                
                # 创建新章节
                current_section = BiographySection(
                    title=para,
                    content="",
                    images=[],
                    order=section_counter,
                    style="paragraph"
                )
                section_content = []
                section_counter += 1
            else:
                if current_section is None:
                    # 创建默认章节
                    current_section = BiographySection(
                        title="我的故事",
                        content="",
                        images=[],
                        order=1,
                        style="paragraph"
                    )
                
                section_content.append(para)
        
        # 保存最后一个章节
        if current_section and section_content:
            current_section.content = '\n\n'.join(section_content)
            sections.append(current_section)
        
        # 如果没有章节，创建一个默认章节
        if not sections:
            sections.append(BiographySection(
                title="我的个人传记",
                content=content,
                images=[],
                order=1,
                style="paragraph"
            ))
        
        return sections
    
    def _assign_images_to_sections(
        self,
        sections: List[BiographySection],
        image_analyses: List[ImageAnalysisResult]
    ) -> List[BiographySection]:
        """为章节分配相关图片"""
        
        if not image_analyses:
            return sections
        
        # 简单的图片分配策略：按顺序平均分配
        images_per_section = len(image_analyses) // len(sections)
        remaining_images = len(image_analyses) % len(sections)
        
        image_index = 0
        for i, section in enumerate(sections):
            # 计算这个章节应该分配多少张图片
            num_images = images_per_section
            if i < remaining_images:
                num_images += 1
            
            # 分配图片
            section_images = []
            for j in range(num_images):
                if image_index < len(image_analyses):
                    section_images.append(image_analyses[image_index].file_path)
                    image_index += 1
            
            section.images = section_images
        
        return sections
    
    async def _create_page_layouts(
        self,
        sections: List[BiographySection],
        qr_codes: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """创建页面布局"""
        pages = []
        
        for section in sections:
            # 为每个章节创建页面
            section_pages = await self._layout_section(section, qr_codes)
            pages.extend(section_pages)
        
        return pages
    
    async def _layout_section(
        self,
        section: BiographySection,
        qr_codes: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """为单个章节创建布局"""
        pages = []
        
        # 创建章节页面
        page_elements = []
        
        # 添加章节标题
        title_element = LayoutElement(
            element_type="title",
            content=section.title,
            position={"x": 0, "y": 0, "width": self.content_width, "height": 30},
            style={"font_size": self.config["heading_font_size"], "align": "center"}
        )
        page_elements.append(title_element)
        
        # 处理章节内容
        y_offset = 40  # 标题下方开始
        
        # 分段处理文本
        paragraphs = section.content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # 计算文本高度
                lines = self._wrap_text(para, self.content_width)
                text_height = len(lines) * self.config["body_font_size"] * self.config["line_height"]
                
                text_element = LayoutElement(
                    element_type="text",
                    content=para.strip(),
                    position={"x": 0, "y": y_offset, "width": self.content_width, "height": text_height},
                    style={"font_size": self.config["body_font_size"], "align": "justify"}
                )
                page_elements.append(text_element)
                y_offset += text_height + self.config["paragraph_spacing"]
        
        # 添加图片和二维码
        for image_path in section.images:
            if os.path.exists(image_path):
                # 添加图片
                image_element = LayoutElement(
                    element_type="image",
                    content=image_path,
                    position={"x": 0, "y": y_offset, "width": self.config["image_max_width"], "height": self.config["image_max_height"]},
                    style={"align": "center"}
                )
                page_elements.append(image_element)
                
                # 添加对应的二维码
                qr_path = qr_codes.get(image_path)
                if qr_path and os.path.exists(qr_path):
                    qr_element = LayoutElement(
                        element_type="qr_code",
                        content=qr_path,
                        position={"x": self.config["image_max_width"] + 10, "y": y_offset, "width": self.config["qr_size"], "height": self.config["qr_size"]},
                        style={"align": "center"}
                    )
                    page_elements.append(qr_element)
                
                y_offset += self.config["image_max_height"] + 20
        
        # 创建页面数据
        page = {
            "page_number": len(pages) + 1,
            "section_title": section.title,
            "elements": page_elements,
            "content_height": y_offset
        }
        pages.append(page)
        
        return pages
    
    def _wrap_text(self, text: str, width: float) -> List[str]:
        """文本换行处理"""
        # 简化的文本换行逻辑
        # 实际实现中需要考虑字体大小和宽度的精确计算
        chars_per_line = int(width / 6)  # 假设每个字符6单位宽度
        return textwrap.wrap(text, width=chars_per_line)
    
    def _format_chapters_for_pdf(
        self,
        sections: List[BiographySection],
        qr_codes: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """格式化章节数据用于PDF生成"""
        chapters = []
        
        for section in sections:
            # 处理章节图片数据
            images_data = []
            for image_path in section.images:
                image_info = {
                    "path": image_path,
                    "caption": f"",  # 可以从图片分析结果中获取
                    "qr_code": qr_codes.get(image_path)
                }
                images_data.append(image_info)
            
            chapter = {
                "title": section.title,
                "content": section.content,
                "images": images_data,
                "order": section.order,
                "style": section.style
            }
            chapters.append(chapter)
        
        return chapters
    
    def _select_cover_image(self, image_analyses: List[ImageAnalysisResult]) -> Optional[str]:
        """选择封面图片"""
        if not image_analyses:
            return None
        
        # 简单的封面选择逻辑：选择第一张图片
        # 实际实现中可以基于图片质量、内容等因素选择
        return image_analyses[0].file_path
    
    async def create_simple_layout(
        self,
        content: str,
        images: List[str],
        qr_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        创建简单布局（单章节）
        
        Args:
            content: 文本内容
            images: 图片路径列表
            qr_codes: 二维码路径映射
            
        Returns:
            Dict[str, Any]: 简单布局数据
        """
        # 创建单个章节
        section = BiographySection(
            title="我的个人传记",
            content=content,
            images=images,
            order=1,
            style="paragraph"
        )
        
        # 格式化为PDF数据
        chapters = self._format_chapters_for_pdf([section], qr_codes)
        
        return {
            "title": "我的个人传记",
            "subtitle": "珍贵回忆的记录",
            "template": "classic",
            "chapters": chapters,
            "cover_image": images[0] if images else None
        }
    
    def calculate_content_metrics(self, content: str, images: List[str]) -> Dict[str, Any]:
        """计算内容指标"""
        # 文本统计
        word_count = len(content.split())
        char_count = len(content)
        paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
        
        # 图片统计
        image_count = len(images)
        
        # 页面估算
        estimated_pages = max(1, (char_count // 2000) + (image_count // 3))
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "paragraph_count": paragraph_count,
            "image_count": image_count,
            "estimated_pages": estimated_pages
        }
    
    async def optimize_layout(
        self,
        layout_data: Dict[str, Any],
        optimization_type: str = "balance"
    ) -> Dict[str, Any]:
        """
        优化布局
        
        Args:
            layout_data: 原始布局数据
            optimization_type: 优化类型 (balance, text_heavy, image_heavy)
            
        Returns:
            Dict[str, Any]: 优化后的布局数据
        """
        if optimization_type == "text_heavy":
            # 文本为主的布局优化
            for chapter in layout_data.get("chapters", []):
                # 减少图片大小，增加文本空间
                pass
        elif optimization_type == "image_heavy":
            # 图片为主的布局优化
            for chapter in layout_data.get("chapters", []):
                # 增加图片大小，调整文本布局
                pass
        else:
            # 平衡布局（默认）
            pass
        
        return layout_data 