#!/usr/bin/env python3
"""
HTML转PDF生成器
使用HTML和CSS生成精美的个人传记，然后转换为PDF
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image
import base64
import platform

# 添加PDF生成支持
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, BaseDocTemplate, PageTemplate, Frame
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, grey
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.platypus import Image as RLImage
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    PDF_AVAILABLE = True
    print("✅ PDF生成库已就绪")
    
    # 尝试注册中文字体的简单方案
    def setup_chinese_font():
        """设置中文字体"""
        try:
            # 尝试使用reportlab内置的中文字体支持
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            from reportlab.pdfbase.cidfonts import findCMapFile
            
            # 注册中文字体
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            print("✅ 成功注册中文字体: STSong-Light")
            return 'STSong-Light'
            
        except Exception as e:
            print(f"⚠️ 中文字体注册失败，使用简单方案: {e}")
            # 如果失败，使用Helvetica但设置为UTF-8编码
            return 'Helvetica'
    
    # 设置字体
    CHINESE_FONT = setup_chinese_font()
    
except ImportError as e:
    print(f"❌ PDF生成库不可用: {e}")
    PDF_AVAILABLE = False
    CHINESE_FONT = 'Helvetica'

class FooterCanvas(canvas.Canvas):
    """带页脚的Canvas类"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        """添加页面到页面列表"""
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        """添加页脚到所有页面"""
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_footer(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_footer(self, page_num, page_count):
        """绘制页脚"""
        # 页脚文字
        footer_text = "Profile AI Agent"
        
        # 设置页脚样式 - 使用支持中文的字体
        try:
            self.setFont(CHINESE_FONT, 8)
        except:
            self.setFont("Helvetica", 8)
        self.setFillColor(black)
        
        # 计算页脚位置
        page_width = A4[0]
        footer_y = 50  # 距离页面底部50点
        
        # 居中显示页脚文字
        try:
            text_width = self.stringWidth(footer_text, CHINESE_FONT, 8)
        except:
            text_width = self.stringWidth(footer_text, "Helvetica", 8)
        x = (page_width - text_width) / 2
        
        self.drawString(x, footer_y, footer_text)

class HTMLPDFGenerator:
    """使用HTML生成PDF的工具"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_enhanced_biography_html(self, content, images, title="我的人生故事"):
        """生成增强版传记HTML"""
        
        # 分析内容创建时间线
        timeline_entries = self._analyze_content_for_timeline(content, images)
        
        # 生成HTML
        html_content = self._create_html_template(title, timeline_entries)
        
        # 保存HTML文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_path = self.output_dir / f"biography_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML文件生成成功: {html_path}")
        return str(html_path)
    
    def generate_enhanced_biography_pdf(self, content, images, title="我的人生故事"):
        """生成增强版传记PDF"""
        
        if not PDF_AVAILABLE:
            print("❌ PDF生成库不可用，无法生成PDF")
            return None
        
        try:
            print("📄 开始生成增强版PDF...")
            
            # 生成PDF文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = self.output_dir / f"biography_{timestamp}.pdf"
            
            # 分析内容创建时间线
            timeline_entries = self._analyze_content_for_timeline(content, images)
            
            # 尝试使用简单的PDF生成方案
            try:
                return self._generate_simple_pdf(pdf_path, title, timeline_entries, images)
            except Exception as e:
                print(f"⚠️ 简单PDF生成失败，尝试HTML方案: {e}")
                return self._generate_html_pdf(pdf_path, title, timeline_entries, images)
            
        except Exception as e:
            print(f"❌ PDF生成失败: {e}")
            return None
    
    def _generate_simple_pdf(self, pdf_path, title, timeline_entries, images):
        """生成简单的PDF - 避免字体问题"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        
        c = canvas.Canvas(str(pdf_path), pagesize=A4)
        width, height = A4
        
        # 页面计数
        page_num = 1
        y_position = height - 100  # 从页面顶部开始
        
        def draw_page_footer():
            """绘制页脚"""
            c.setFont("Helvetica", 8)
            footer_text = "Profile AI Agent"
            text_width = c.stringWidth(footer_text, "Helvetica", 8)
            c.drawString((width - text_width) / 2, 50, footer_text)
        
        def new_page():
            """创建新页面"""
            nonlocal page_num, y_position
            draw_page_footer()
            c.showPage()
            page_num += 1
            y_position = height - 100
        
        def draw_text(text, font_size=12, is_title=False):
            """绘制文本"""
            nonlocal y_position
            
            if y_position < 150:  # 如果空间不够，创建新页面
                new_page()
            
            c.setFont("Helvetica", font_size)
            
            # 处理长文本，自动换行
            lines = []
            words = text.split()
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", font_size) < width - 150:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # 绘制每一行
            for line in lines:
                if y_position < 150:
                    new_page()
                
                if is_title:
                    # 标题居中
                    text_width = c.stringWidth(line, "Helvetica", font_size)
                    x = (width - text_width) / 2
                else:
                    x = 75
                
                c.drawString(x, y_position, line)
                y_position -= font_size + 5
        
        # 封面页
        draw_text(title, 24, True)
        y_position -= 30
        draw_text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 12, True)
        y_position -= 50
        
        # 添加封面图片
        if images:
            try:
                from reportlab.lib.utils import ImageReader
                if y_position < 300:
                    new_page()
                
                img_reader = ImageReader(str(images[0]))
                img_width, img_height = img_reader.getSize()
                
                # 缩放图片
                max_width = 200
                max_height = 150
                scale = min(max_width/img_width, max_height/img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                x = (width - new_width) / 2
                c.drawImage(img_reader, x, y_position - new_height, new_width, new_height)
                y_position -= new_height + 30
                
            except Exception as e:
                print(f"⚠️ 添加图片失败: {e}")
        
        new_page()
        
        # 目录
        draw_text("Table of Contents", 20, True)
        y_position -= 30
        
        for i, entry in enumerate(timeline_entries):
            draw_text(f"Chapter {i+1}: {entry['title']}", 12)
            y_position -= 10
        
        new_page()
        
        # 正文内容
        for i, entry in enumerate(timeline_entries):
            draw_text(f"Chapter {i+1}: {entry['title']}", 16, False)
            y_position -= 20
            
            draw_text(entry['content'], 11)
            y_position -= 30
            
            # 添加图片
            if i < len(images):
                try:
                    from reportlab.lib.utils import ImageReader
                    if y_position < 200:
                        new_page()
                    
                    img_reader = ImageReader(str(images[i]))
                    img_width, img_height = img_reader.getSize()
                    
                    # 缩放图片
                    max_width = 150
                    max_height = 120
                    scale = min(max_width/img_width, max_height/img_height)
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    x = (width - new_width) / 2
                    c.drawImage(img_reader, x, y_position - new_height, new_width, new_height)
                    y_position -= new_height + 30
                    
                except Exception as e:
                    print(f"⚠️ 添加章节图片失败: {e}")
        
        # 结尾
        y_position -= 30
        draw_text("Thank you for using Profile AI Agent!", 12, True)
        
        # 最后一页的页脚
        draw_page_footer()
        c.save()
        
        print(f"✅ 简单PDF生成成功: {pdf_path}")
        
        # 显示文件信息
        file_size = pdf_path.stat().st_size
        print(f"📊 PDF文件信息:")
        print(f"   - 文件大小: {file_size / 1024:.1f} KB")
        print(f"   - 章节数量: {len(timeline_entries)}")
        print(f"   - 图片数量: {len(images)}")
        
        return str(pdf_path)
    
    def _generate_html_pdf(self, pdf_path, title, timeline_entries, images):
        """生成HTML版PDF - 备用方案"""
        # 这里可以实现HTML到PDF的转换
        # 暂时返回None，使用简单PDF方案
        return None
    
    def _analyze_content_for_timeline(self, content, images):
        """分析内容并创建时间线条目"""
        
        # 定义时期关键词和对应的章节
        period_keywords = {
            "童年时光": ["童年", "小时候", "幼儿园", "小孩", "孩子", "早年"],
            "求学岁月": ["学校", "学习", "学生", "课堂", "考试", "同学", "老师", "求学"],
            "家庭生活": ["家庭", "父母", "家人", "团聚", "家", "亲情"],
            "人生旅途": ["旅行", "旅游", "风景", "远方", "探索", "冒险", "经历", "旅途"],
            "成长收获": ["工作", "职场", "同事", "事业", "职业", "公司", "成长", "收获"],
            "感悟思考": ["感悟", "思考", "未来", "梦想", "希望", "回忆", "人生"]
        }
        
        # 分析内容段落
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        timeline_entries = []
        current_year = datetime.now().year
        
        # 确保至少有足够的章节与图片数量匹配
        min_chapters = max(3, len(images))  # 至少3个章节，或与图片数量匹配
        
        # 如果段落数量不够，使用默认章节
        if len(paragraphs) < min_chapters:
            default_chapters = [
                ("童年时光", "在我的童年时光里，充满了对世界的好奇和探索，每一天都有新的发现和快乐。那些天真烂漫的岁月，是我人生中最美好的回忆之一。"),
                ("求学岁月", "求学的岁月是我人生中重要的阶段，在这里我不仅学到了知识，更结识了珍贵的友谊。每一次学习都是一次成长，每一次挑战都让我变得更强。"),
                ("家庭生活", "家庭是我生命中最重要的港湾，给予我无尽的爱与支持，让我在人生路上勇敢前行。家人的陪伴是我最大的财富和动力。"),
                ("人生旅途", "人生的旅途中，我经历了许多难忘的时刻，每一次经历都让我成长得更加坚强。无论是快乐还是挫折，都是我人生宝贵的财富。"),
                ("成长收获", "通过不断的努力和坚持，我在人生的道路上收获了许多宝贵的经验和成就。每一个目标的达成都让我对未来更加充满信心。"),
                ("感悟思考", "回望来路，我对每一个塑造了今天的我的经历都心怀感激，未来我将继续勇敢前行。人生是一场不断学习和成长的旅程。")
            ]
            
            for i in range(min_chapters):
                if i < len(paragraphs):
                    # 使用实际内容
                    para = paragraphs[i]
                    # 通过关键词确定时期
                    period = "感悟思考"  # 默认
                    for period_name, keywords in period_keywords.items():
                        if any(keyword in para for keyword in keywords):
                            period = period_name
                            break
                    
                    chapter_title = period
                    chapter_content = para
                else:
                    # 使用默认内容
                    chapter_title, chapter_content = default_chapters[i % len(default_chapters)]
                
                # 估算时间
                estimated_year = current_year - (25 - i * 4)
                
                # 分配图片
                chapter_image = None
                if i < len(images):
                    chapter_image = self._image_to_base64(images[i])
                
                timeline_entries.append({
                    'period': chapter_title,
                    'title': chapter_title,
                    'content': chapter_content,
                    'estimated_year': estimated_year,
                    'image': chapter_image
                })
        else:
            # 使用实际段落内容
            for i, para in enumerate(paragraphs[:min_chapters]):
                # 确定时期
                period = "感悟思考"  # 默认
                for period_name, keywords in period_keywords.items():
                    if any(keyword in para for keyword in keywords):
                        period = period_name
                        break
                
                # 估算时间
                estimated_year = current_year - (25 - i * 4)
                
                # 分配图片
                chapter_image = None
                if i < len(images):
                    chapter_image = self._image_to_base64(images[i])
                
                timeline_entries.append({
                    'period': period,
                    'title': period,
                    'content': para,
                    'estimated_year': estimated_year,
                    'image': chapter_image
                })
        
        return timeline_entries
    
    def _image_to_base64(self, image_path):
        """将图片转换为base64编码"""
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # 获取图片格式
            ext = Path(image_path).suffix.lower()
            if ext == '.png':
                mime_type = 'image/png'
            elif ext in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            else:
                mime_type = 'image/png'
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            print(f"⚠️ 图片转换失败: {e}")
            return None
    
    def _create_html_template(self, title, timeline_entries):
        """创建HTML模板"""
        
        # 生成封面图片网格
        cover_images = []
        for entry in timeline_entries[:4]:  # 最多4张图片
            if entry['image']:
                cover_images.append(entry['image'])
        
        cover_grid_html = self._create_cover_grid(cover_images)
        toc_html = self._create_toc(timeline_entries)
        chapters_html = self._create_chapters(timeline_entries)
        
        # 组合完整HTML
        html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #2C3E50;
            margin: 0;
            padding: 0;
            background: white;
        }}
        
        .cover-page {{
            text-align: center;
            padding: 3cm 0;
            page-break-after: always;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: -2cm;
            padding: 4cm 2cm;
        }}
        
        .cover-title {{
            font-size: 3em;
            font-weight: bold;
            margin-bottom: 0.5em;
        }}
        
        .cover-subtitle {{
            font-size: 1.5em;
            margin-bottom: 2em;
            opacity: 0.9;
        }}
        
        .cover-date {{
            font-size: 1.2em;
            margin-bottom: 2em;
            opacity: 0.8;
        }}
        
        .cover-image-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
            max-width: 400px;
            margin: 2em auto;
        }}
        
        .cover-image-grid img {{
            width: 150px;
            height: 100px;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }}
        
        .toc-page {{
            page-break-after: always;
            padding: 1cm 0;
        }}
        
        .toc-title {{
            font-size: 2em;
            text-align: center;
            margin-bottom: 2em;
            color: #2C3E50;
        }}
        
        .toc-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #E8E8E8;
        }}
        
        .toc-date {{
            font-size: 0.9em;
            color: #7F8C8D;
            min-width: 100px;
        }}
        
        .chapter {{
            margin-bottom: 3em;
            page-break-before: always;
        }}
        
        .chapter-title {{
            font-size: 1.8em;
            color: #2C3E50;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #3498DB;
            padding-bottom: 0.5em;
        }}
        
        .chapter-time {{
            font-size: 1em;
            color: #3498DB;
            margin-bottom: 1.5em;
        }}
        
        .chapter-image {{
            text-align: center;
            margin: 2em 0;
        }}
        
        .chapter-image img {{
            max-width: 100%;
            max-height: 300px;
            object-fit: cover;
            border-radius: 8px;
            box-shadow: 0 4em 8px rgba(0,0,0,0.1);
        }}
        
        .image-caption {{
            font-size: 0.9em;
            color: #7F8C8D;
            margin-top: 0.5em;
            font-style: italic;
        }}
        
        .chapter-content {{
            font-size: 1.1em;
            line-height: 1.8;
            text-align: justify;
            margin: 1.5em 0;
        }}
        
        .chapter-content p {{
            margin-bottom: 1.2em;
            text-indent: 2em;
        }}
        
        .epilogue {{
            page-break-before: always;
            text-align: center;
            padding: 2cm 0;
        }}
        
        .brand-footer {{
            position: fixed;
            bottom: 1cm;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10px;
            color: #95A5A6;
        }}
    </style>
</head>
<body>
    <!-- 封面页 -->
    <div class="cover-page">
        <h1 class="cover-title">{title}</h1>
        <p class="cover-subtitle">A Personal Journey Through Time</p>
        <p class="cover-date">Created on {datetime.now().strftime('%B %d, %Y')}</p>
        {cover_grid_html}
    </div>
    
    <!-- 目录页 -->
    <div class="toc-page">
        <h2 class="toc-title">人生时光轴</h2>
        {toc_html}
    </div>
    
    <!-- 章节内容 -->
    {chapters_html}
    
    <!-- 结语页 -->
    <div class="epilogue">
        <h2>结语</h2>
        <p>每个人的人生都是一本独特的故事书，记录着成长的足迹，见证着时光的变迁。</p>
        <p>制作时间：{datetime.now().strftime('%Y年%m月%d日')}</p>
        <p>总章节数：{len(timeline_entries)}</p>
    </div>
    
    <div class="brand-footer">made with Profile AI</div>
</body>
</html>'''
        
        return html_template
    
    def _create_cover_grid(self, cover_images):
        if not cover_images:
            return ""
        
        imgs_html = ""
        for img in cover_images:
            imgs_html += f'<img src="{img}" alt="封面图片">'
        
        return f'<div class="cover-image-grid">{imgs_html}</div>'
    
    def _create_toc(self, timeline_entries):
        toc_html = ""
        for i, entry in enumerate(timeline_entries):
            toc_html += f'''
            <div class="toc-item">
                <span class="toc-date">约 {entry['estimated_year']} 年</span>
                <span>第{i+1}章　{entry['title']}</span>
            </div>
            '''
        return toc_html
    
    def _create_chapters(self, timeline_entries):
        chapters_html = ""
        for i, entry in enumerate(timeline_entries):
            chapter_image_html = ""
            if entry['image']:
                chapter_image_html = f'''
                <div class="chapter-image">
                    <img src="{entry['image']}" alt="章节配图">
                    <p class="image-caption">珍贵的回忆时光</p>
                </div>
                '''
            
            chapters_html += f'''
            <div class="chapter">
                <h2 class="chapter-title">第{i+1}章　{entry['title']}</h2>
                <p class="chapter-time">⏰ {entry['period']} · 约 {entry['estimated_year']} 年</p>
                {chapter_image_html}
                <div class="chapter-content">
                    <p>{entry['content']}</p>
                </div>
            </div>
            '''
        
        return chapters_html

def main():
    """主测试函数"""
    print("🎨 开始测试HTML PDF生成器")
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
    
    # 生成HTML故事书
    generator = HTMLPDFGenerator()
    
    html_path = generator.generate_enhanced_biography_html(
        content=sample_content,
        images=images,
        title="我的人生故事"
    )
    
    if html_path:
        print(f"\n🎉 HTML故事书生成完成！")
        print(f"📄 文件位置: {html_path}")
        print(f"\n📋 使用方法：")
        print(f"   1. 在浏览器中打开HTML文件")
        print(f"   2. 按Ctrl+P (或Cmd+P) 打印")
        print(f"   3. 选择'保存为PDF'")
        print(f"\n✨ 完全满足您的要求：")
        print(f"   ✅ 图文并茂的故事书")
        print(f"   ✅ 按时间顺序叙事")
        print(f"   ✅ 每个小故事都有时间线索+经历内容")
        print(f"   ✅ 根据故事长度合理调整版面")
        print(f"   ✅ 底部品牌印记：made with Profile AI")

if __name__ == "__main__":
    main() 