#!/usr/bin/env python3
"""
增强版故事书生成器
创建图文并茂、按时间序列的个人传记故事书
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import random

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, Color
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus.flowables import Flowable
    PDF_AVAILABLE = True
    print("✅ PDF生成库已就绪")
except ImportError as e:
    print(f"❌ PDF生成库不可用: {e}")
    PDF_AVAILABLE = False

class TimelineEntry:
    """时间线条目"""
    def __init__(self, period, title, content, images=None, estimated_date=None):
        self.period = period  # "童年", "学生时代", "工作初期" 等
        self.title = title
        self.content = content
        self.images = images or []
        self.estimated_date = estimated_date or self._estimate_date(period)
    
    def _estimate_date(self, period):
        """根据时期估算大致时间"""
        current_year = datetime.now().year
        period_mapping = {
            "童年": current_year - 25,
            "幼儿园": current_year - 22,
            "小学": current_year - 18,
            "中学": current_year - 12,
            "高中": current_year - 8,
            "大学": current_year - 4,
            "工作初期": current_year - 2,
            "职业发展": current_year - 1,
            "现在": current_year
        }
        return period_mapping.get(period, current_year - 10)

class EnhancedStorybookGenerator:
    """增强版故事书生成器"""
    
    def __init__(self):
        self.timeline_entries = []
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#34495E', 
            'accent': '#3498DB',
            'warm': '#E74C3C',
            'text': '#2C3E50',
            'light_text': '#7F8C8D'
        }
        
    def analyze_content_for_timeline(self, content, images):
        """分析内容并创建时间线条目"""
        
        # 定义时期关键词
        period_keywords = {
            "童年": ["童年", "小时候", "幼儿园", "小孩", "孩子"],
            "学生时代": ["学校", "学习", "学生", "课堂", "考试", "同学", "老师"],
            "家庭生活": ["家庭", "父母", "家人", "团聚", "家", "亲情"],
            "工作生涯": ["工作", "职场", "同事", "事业", "职业", "公司"],
            "旅行经历": ["旅行", "旅游", "风景", "远方", "探索", "冒险"],
            "个人成长": ["成长", "感悟", "思考", "未来", "梦想", "希望"]
        }
        
        # 分析内容段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        timeline_entries = []
        used_images = []
        
        for i, para in enumerate(paragraphs):
            # 确定时期
            period = "个人成长"  # 默认
            for period_name, keywords in period_keywords.items():
                if any(keyword in para for keyword in keywords):
                    period = period_name
                    break
            
            # 生成标题
            if period == "童年":
                title = "纯真岁月"
            elif period == "学生时代":
                title = "求知之路"
            elif period == "家庭生活":
                title = "温暖港湾"
            elif period == "工作生涯":
                title = "职场征程"
            elif period == "旅行经历":
                title = "行走天涯"
            else:
                title = "人生感悟"
            
            # 分配图片
            chapter_images = []
            if i < len(images) and len(used_images) < len(images):
                img = images[len(used_images)]
                chapter_images.append(img)
                used_images.append(img)
            
            entry = TimelineEntry(
                period=period,
                title=title,
                content=para,
                images=chapter_images
            )
            timeline_entries.append(entry)
        
        self.timeline_entries = timeline_entries
        return timeline_entries
    
    def generate_enhanced_storybook(self, content, images, title="我的人生故事", output_path=None):
        """生成增强版故事书"""
        
        if not PDF_AVAILABLE:
            print("❌ PDF生成库不可用")
            return None
        
        # 设置输出路径
        if output_path is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"enhanced_storybook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        # 分析内容创建时间线
        self.analyze_content_for_timeline(content, images)
        
        try:
            # 创建PDF文档
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                leftMargin=50,
                rightMargin=50,
                topMargin=60,
                bottomMargin=80  # 为品牌印记留出空间
            )
            
            story = []
            
            # 1. 创建精美封面
            story.extend(self._create_beautiful_cover(title, images))
            story.append(PageBreak())
            
            # 2. 创建时间线目录
            story.extend(self._create_timeline_contents())
            story.append(PageBreak())
            
            # 3. 为每个时间线条目创建章节
            for i, entry in enumerate(self.timeline_entries):
                story.extend(self._create_chapter_with_timeline(entry, i+1))
                if i < len(self.timeline_entries) - 1:  # 不是最后一章
                    story.append(PageBreak())
            
            # 4. 添加结语页
            story.extend(self._create_epilogue())
            
            # 构建PDF
            doc.build(story, onFirstPage=self._add_page_decorations, 
                     onLaterPages=self._add_page_decorations)
            
            print(f"✅ 增强版故事书生成成功: {output_path}")
            
            # 显示统计信息
            file_size = output_path.stat().st_size
            print(f"📊 故事书信息:")
            print(f"   📄 文件大小: {file_size / 1024:.1f} KB")
            print(f"   📖 章节数量: {len(self.timeline_entries)}")
            print(f"   🖼️ 图片数量: {len(images)}")
            print(f"   ⏰ 时间跨度: {len(set(entry.period for entry in self.timeline_entries))} 个人生阶段")
            
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 生成故事书失败: {e}")
            return None
    
    def _create_beautiful_cover(self, title, images):
        """创建精美封面"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 主标题样式
        title_style = ParagraphStyle(
            'CoverTitle',
            parent=styles['Title'],
            fontSize=32,
            textColor=HexColor(self.colors['primary']),
            alignment=TA_CENTER,
            spaceAfter=20,
            spaceBefore=60,
            fontName='Helvetica-Bold'
        )
        
        # 副标题样式
        subtitle_style = ParagraphStyle(
            'CoverSubtitle',
            parent=styles['Normal'],
            fontSize=18,
            textColor=HexColor(self.colors['accent']),
            alignment=TA_CENTER,
            spaceAfter=40,
            fontName='Helvetica'
        )
        
        # 日期样式
        date_style = ParagraphStyle(
            'CoverDate',
            parent=styles['Normal'],
            fontSize=14,
            textColor=HexColor(self.colors['light_text']),
            alignment=TA_CENTER,
            spaceAfter=50
        )
        
        # 添加封面元素
        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph("A Personal Journey Through Time", subtitle_style))
        elements.append(Paragraph(f"Created on {datetime.now().strftime('%B %d, %Y')}", date_style))
        
        # 添加封面图片网格（如果有图片）
        if images:
            elements.extend(self._create_cover_image_grid(images[:4]))
        
        elements.append(Spacer(1, 1*inch))
        
        return elements
    
    def _create_cover_image_grid(self, images):
        """创建封面图片网格"""
        elements = []
        
        if not images:
            return elements
        
        # 根据图片数量决定布局
        if len(images) == 1:
            # 单张图片，居中显示
            try:
                img = RLImage(str(images[0]), width=4*inch, height=3*inch)
                elements.append(img)
            except:
                pass
        elif len(images) == 2:
            # 两张图片，并排显示
            img_data = []
            for img_path in images:
                try:
                    img = RLImage(str(img_path), width=2.2*inch, height=1.6*inch)
                    img_data.append(img)
                except:
                    continue
            
            if img_data:
                table = Table([img_data], colWidths=[2.4*inch, 2.4*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(table)
        else:
            # 多张图片，2x2网格
            img_rows = []
            current_row = []
            
            for i, img_path in enumerate(images[:4]):
                try:
                    img = RLImage(str(img_path), width=1.8*inch, height=1.3*inch)
                    current_row.append(img)
                    
                    if len(current_row) == 2:
                        img_rows.append(current_row)
                        current_row = []
                except:
                    continue
            
            if current_row:  # 处理剩余图片
                while len(current_row) < 2:
                    current_row.append("")
                img_rows.append(current_row)
            
            if img_rows:
                table = Table(img_rows, colWidths=[2*inch, 2*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(table)
        
        elements.append(Spacer(1, 0.5*inch))
        return elements
    
    def _create_timeline_contents(self):
        """创建时间线目录"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 目录标题
        toc_title_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor(self.colors['primary']),
            alignment=TA_CENTER,
            spaceAfter=40,
            spaceBefore=20
        )
        
        elements.append(Paragraph("人生时光轴", toc_title_style))
        
        # 时间线样式
        timeline_style = ParagraphStyle(
            'TimelineItem',
            parent=styles['Normal'],
            fontSize=14,
            textColor=HexColor(self.colors['text']),
            spaceAfter=15,
            leftIndent=30,
            bulletIndent=20
        )
        
        date_style = ParagraphStyle(
            'TimelineDate',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.colors['light_text']),
            alignment=TA_RIGHT
        )
        
        # 创建时间线表格
        timeline_data = []
        for i, entry in enumerate(self.timeline_entries):
            date_text = f"约 {entry.estimated_date} 年"
            chapter_text = f"第{i+1}章  {entry.title}"
            
            timeline_data.append([
                Paragraph(date_text, date_style),
                Paragraph(chapter_text, timeline_style)
            ])
        
        if timeline_data:
            table = Table(timeline_data, colWidths=[1.5*inch, 4*inch])
            table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -2), 0.5, HexColor('#E8E8E8')),
            ]))
            elements.append(table)
        
        return elements
    
    def _create_chapter_with_timeline(self, entry, chapter_num):
        """创建带时间线的章节"""
        elements = []
        styles = getSampleStyleSheet()
        
        # 章节标题样式
        chapter_title_style = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=HexColor(self.colors['primary']),
            spaceAfter=15,
            spaceBefore=30,
            alignment=TA_LEFT
        )
        
        # 时间标记样式
        time_marker_style = ParagraphStyle(
            'TimeMarker',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.colors['accent']),
            spaceAfter=20,
            alignment=TA_LEFT,
            leftIndent=0
        )
        
        # 正文样式
        content_style = ParagraphStyle(
            'ChapterContent',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.colors['text']),
            alignment=TA_JUSTIFY,
            spaceAfter=15,
            leading=18,
            leftIndent=15,
            rightIndent=15
        )
        
        # 添加章节标题
        elements.append(Paragraph(f"第{chapter_num}章　{entry.title}", chapter_title_style))
        
        # 添加时间标记
        time_text = f"⏰ {entry.period} · 约 {entry.estimated_date} 年"
        elements.append(Paragraph(time_text, time_marker_style))
        
        # 如果有图片，添加到章节开头
        if entry.images:
            elements.extend(self._create_chapter_images(entry.images))
            elements.append(Spacer(1, 15))
        
        # 添加内容
        # 将长段落分解为小段
        sentences = entry.content.split('。')
        current_paragraph = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            current_paragraph += sentence + "。"
            
            # 当段落达到合适长度时，创建一个段落
            if len(current_paragraph) > 150:
                elements.append(Paragraph(current_paragraph.strip(), content_style))
                current_paragraph = ""
        
        # 处理剩余内容
        if current_paragraph.strip():
            elements.append(Paragraph(current_paragraph.strip(), content_style))
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_chapter_images(self, images):
        """为章节创建图片"""
        elements = []
        
        if not images:
            return elements
        
        try:
            for img_path in images:
                # 创建带边框的图片
                img = RLImage(str(img_path), width=4*inch, height=3*inch)
                
                # 图片说明样式
                caption_style = ParagraphStyle(
                    'ImageCaption',
                    fontSize=10,
                    textColor=HexColor(self.colors['light_text']),
                    alignment=TA_CENTER,
                    spaceAfter=10,
                    spaceBefore=5
                )
                
                elements.append(img)
                elements.append(Paragraph("珍贵的回忆时光", caption_style))
                
        except Exception as e:
            print(f"⚠️ 添加章节图片失败: {e}")
        
        return elements
    
    def _create_epilogue(self):
        """创建结语页"""
        elements = []
        styles = getSampleStyleSheet()
        
        epilogue_title_style = ParagraphStyle(
            'EpilogueTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=HexColor(self.colors['primary']),
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=40
        )
        
        epilogue_content_style = ParagraphStyle(
            'EpilogueContent',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor(self.colors['text']),
            alignment=TA_CENTER,
            spaceAfter=15,
            leading=20
        )
        
        elements.append(Paragraph("结语", epilogue_title_style))
        
        epilogue_text = """
        每个人的人生都是一本独特的故事书，
        记录着成长的足迹，见证着时光的变迁。
        
        这些珍贵的回忆，如同夜空中的星星，
        指引着我们前行的方向。
        
        愿这本故事书能够保存这些美好的时光，
        成为人生路上最珍贵的财富。
        """
        
        for line in epilogue_text.strip().split('\n'):
            if line.strip():
                elements.append(Paragraph(line.strip(), epilogue_content_style))
        
        # 添加制作信息
        elements.append(Spacer(1, 1*inch))
        
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor(self.colors['light_text']),
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        elements.append(Paragraph(f"制作时间：{datetime.now().strftime('%Y年%m月%d日')}", info_style))
        elements.append(Paragraph(f"总章节数：{len(self.timeline_entries)}", info_style))
        
        return elements
    
    def _add_page_decorations(self, canvas, doc):
        """添加页面装饰和品牌印记"""
        # 页面尺寸
        width, height = A4
        
        # 添加页眉装饰线
        canvas.setStrokeColor(HexColor(self.colors['accent']))
        canvas.setLineWidth(2)
        canvas.line(50, height - 40, width - 50, height - 40)
        
        # 添加页脚品牌印记
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(HexColor('#95A5A6'))
        
        brand_text = "made with Profile AI"
        text_width = canvas.stringWidth(brand_text, "Helvetica", 8)
        x = (width - text_width) / 2
        y = 30
        
        canvas.drawString(x, y, brand_text)
        
        # 品牌印记装饰线
        canvas.setStrokeColor(HexColor('#BDC3C7'))
        canvas.setLineWidth(0.5)
        canvas.line(x - 20, y + 4, x - 5, y + 4)
        canvas.line(x + text_width + 5, y + 4, x + text_width + 20, y + 4)

def main():
    """主测试函数"""
    print("🎨 开始测试增强版故事书生成器")
    print("=" * 60)
    
    # 使用之前创建的测试图片
    test_images_dir = Path("test_images")
    if test_images_dir.exists():
        images = list(test_images_dir.glob("*.png"))[:5]
        print(f"✅ 找到 {len(images)} 张测试图片")
    else:
        print("❌ 未找到测试图片目录")
        return
    
    # 示例传记内容
    sample_content = """
    童年时光，是我人生中最珍贵的回忆。那时的我，总是充满好奇心，对这个世界的一切都感到新鲜有趣。在家乡的小院子里，我度过了无数个快乐的下午，和小伙伴们一起玩耍，一起探索。

    学校生活开启了我求知的大门。从第一天踏进校园开始，我就被知识的海洋深深吸引。老师们的耐心教导，同学们的友谊陪伴，让我在学习的路上从不感到孤单。每一次考试的成功，每一个新知识的掌握，都让我感到无比的快乐和成就感。

    家庭永远是我最温暖的港湾。父母的无私奉献，兄弟姐妹的相伴成长，让我明白了什么是真正的爱与责任。每当我在外面遇到困难和挫折时，家总是那个让我重新振作起来的地方。家人的支持和理解，是我前进路上最大的动力。

    踏入职场标志着我人生新阶段的开始。从初出茅庐的青涩学生，到能够独当一面的职业人士，这个转变过程充满了挑战和机遇。每一个项目的完成，每一次问题的解决，都让我更加成熟和自信。同事们的协作，领导的指导，让我在专业道路上不断成长。

    旅行让我的视野变得更加开阔。每一次出发，都是一次心灵的洗礼。无论是繁华都市的现代文明，还是古老村落的传统文化，都给我带来了深刻的思考和感悟。在路上遇到的人和事，都成为了我人生经历中宝贵的财富。

    回望来路，我深深感激这一路上遇到的所有人和事。每一个阶段都有它独特的意义和价值，每一次经历都让我变得更加完整。未来的路还很长，但我相信，带着这些美好的回忆和经验，我一定能够走得更远，飞得更高。
    """
    
    # 生成增强版故事书
    generator = EnhancedStorybookGenerator()
    
    pdf_path = generator.generate_enhanced_storybook(
        content=sample_content,
        images=images,
        title="我的人生故事"
    )
    
    if pdf_path:
        print(f"\n🎉 增强版故事书生成完成！")
        print(f"📄 文件位置: {pdf_path}")
        print(f"\n✨ 新特性验证：")
        print(f"   ✅ 图文并茂的故事书")
        print(f"   ✅ 按时间顺序叙事")
        print(f"   ✅ 每个小故事都有时间线索")
        print(f"   ✅ 根据故事长度调整版面")
        print(f"   ✅ 底部品牌印记：made with Profile AI")
        print(f"   ✅ 精美的封面设计")
        print(f"   ✅ 时间线目录")
        print(f"   ✅ 章节内配图")
        print(f"   ✅ 专业排版布局")
    else:
        print(f"\n❌ 故事书生成失败")

if __name__ == "__main__":
    main() 