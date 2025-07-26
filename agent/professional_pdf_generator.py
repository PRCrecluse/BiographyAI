#!/usr/bin/env python3
"""
专业PDF生成器 - 集成字体管理器和版面引擎
生成出版级别的个人传记图书
"""

import os
from pathlib import Path
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black, gray, white
import logging

# 导入自定义模块
from font_manager import font_manager
from layout_engine import LayoutEngine

logger = logging.getLogger(__name__)

class ProfessionalPDFGenerator:
    """专业PDF生成器"""
    
    def __init__(self):
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化引擎
        self.font_manager = font_manager
        self.layout_engine = LayoutEngine(self.font_manager)
        
        # 页面参数
        self.page_width, self.page_height = A4
        
        logger.info("✨ 专业PDF生成器初始化完成")
    
    def generate_biography_book(self, content, images, title="我的人生故事", language="zh-CN"):
        """生成专业传记图书"""
        
        try:
            logger.info("📖 开始生成专业传记图书...")
            
            # 生成文件路径
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_path = self.output_dir / f"biography_professional_{timestamp}.pdf"
            
            # 分析和准备内容
            chapters = self._prepare_content(content, images, language)
            
            # 创建PDF文档
            c = canvas.Canvas(str(pdf_path), pagesize=A4)
            
            # 生成各个部分
            self._generate_cover_page(c, title, images, language)
            self._generate_table_of_contents(c, chapters)
            self._generate_content_pages(c, chapters, images)
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
        
        # 使用字体管理器清理内容
        cleaned_content = self.font_manager.get_safe_text(content, max_length=5000)
        
        # 分析内容创建章节
        chapters = self._analyze_content_for_chapters(cleaned_content, images, language)
        
        logger.info(f"📚 生成了 {len(chapters)} 个章节")
        return chapters
    
    def _analyze_content_for_chapters(self, content, images, language):
        """分析内容并创建章节"""
        
        # 创建默认章节模板
        if language.startswith('zh') or language == 'Chinese':
            chapter_templates = [
                {
                    'title': '童年时光',
                    'content': '在我的童年时光里，充满了对世界的好奇和探索。每一天都有新的发现和快乐，那些天真烂漫的岁月，是我人生中最美好的回忆之一。家人的陪伴让我感受到了无尽的温暖，朋友的友谊让我学会了分享和关爱。'
                },
                {
                    'title': '求学岁月',
                    'content': '求学的岁月是我人生中重要的阶段，在这里我不仅学到了知识，更结识了珍贵的友谊。每一次学习都是一次成长，每一次挑战都让我变得更强。老师的教导和同学的帮助，让我在知识的海洋中尽情遨游。'
                },
                {
                    'title': '人生旅途',
                    'content': '人生的旅途中，我经历了许多难忘的时刻。无论是快乐还是挫折，都是我人生宝贵的财富。每一次经历都让我成长得更加坚强，每一个选择都塑造了今天的我。感谢生活给予我的一切，让我成为更好的自己。'
                }
            ]
        elif language == "pt" or language == "Portuguese":
            chapter_templates = [
                {
                    'title': 'Primeiros Anos',
                    'content': 'Nos meus primeiros anos, eu estava cheio de curiosidade e admiração pelo mundo ao meu redor. Cada dia trazia novas descobertas e alegria. Aqueles dias inocentes e despreocupados permanecem como algumas das minhas memórias mais preciosas. O calor da família e a alegria da amizade moldaram minha compreensão do amor e cuidado.'
                },
                {
                    'title': 'Dias de Escola',
                    'content': 'Meus dias de escola foram um tempo de aprendizado, amizade e descoberta das minhas paixões. Cada lição foi um passo em direção ao crescimento, e cada desafio me tornou mais forte. A orientação dos professores e o apoio dos colegas de classe me ajudaram a navegar no vasto oceano do conhecimento com confiança e entusiasmo.'
                },
                {
                    'title': 'Jornada da Vida',
                    'content': 'Ao longo da minha jornada de vida, experimentei muitos momentos inesquecíveis. Seja cheio de alegria ou desafios, cada experiência foi um presente precioso. Cada experiência me tornou mais forte, e cada escolha moldou quem sou hoje. Sou grato por tudo que a vida me deu.'
                }
            ]
        elif language == "es" or language == "Spanish":
            chapter_templates = [
                {
                    'title': 'Primeros Años',
                    'content': 'En mis primeros años, estaba lleno de curiosidad y asombro por el mundo que me rodeaba. Cada día traía nuevos descubrimientos y alegría. Esos días inocentes y despreocupados siguen siendo algunos de mis recuerdos más preciados. La calidez de la familia y la alegría de la amistad formaron mi comprensión del amor y el cuidado.'
                },
                {
                    'title': 'Días de Escuela',
                    'content': 'Mis días de escuela fueron un tiempo de aprendizaje, amistad y descubrimiento de mis pasiones. Cada lección fue un paso hacia el crecimiento, y cada desafío me hizo más fuerte. La guía de los maestros y el apoyo de los compañeros de clase me ayudaron a navegar por el vasto océano del conocimiento con confianza y entusiasmo.'
                },
                {
                    'title': 'Viaje de la Vida',
                    'content': 'A lo largo de mi viaje de vida, he experimentado muchos momentos inolvidables. Ya sea lleno de alegría o desafíos, cada experiencia ha sido un regalo precioso. Cada experiencia me ha hecho más fuerte, y cada elección ha moldeado quien soy hoy. Estoy agradecido por todo lo que la vida me ha dado.'
                }
            ]
        else:
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
        
        # 如果用户提供了内容，尝试融合
        if content and content.strip():
            user_content = content.strip()
            # 将用户内容融入第一个章节
            if len(chapter_templates) > 0:
                chapter_templates[0]['content'] = user_content + "\n\n" + chapter_templates[0]['content']
        
        # 根据图片数量调整章节数量
        num_chapters = max(len(chapter_templates), len(images), 3)
        
        chapters = []
        for i in range(num_chapters):
            if i < len(chapter_templates):
                chapter = chapter_templates[i].copy()
            else:
                # 创建额外章节
                if language.startswith('zh'):
                    chapter = {
                        'title': f'人生感悟 {i-len(chapter_templates)+1}',
                        'content': '每一段人生经历都值得珍藏，每一个瞬间都有其独特的意义。回望来路，我对过去心怀感激；展望未来，我满怀希望和期待。'
                    }
                elif language == "pt" or language == "Portuguese":
                    chapter = {
                        'title': f'Reflexões da Vida {i-len(chapter_templates)+1}',
                        'content': 'Cada experiência de vida vale a pena ser treasurada, e cada momento tem seu significado único. Olhando para trás, sou grato pelo passado; olhando para frente, estou cheio de esperança e expectativa para o futuro.'
                    }
                elif language == "es" or language == "Spanish":
                    chapter = {
                        'title': f'Reflexiones de Vida {i-len(chapter_templates)+1}',
                        'content': 'Cada experiencia de vida vale la pena atesorar, y cada momento tiene su significado único. Mirando hacia atrás, estoy agradecido por el pasado; mirando hacia adelante, estoy lleno de esperanza y expectativa para el futuro.'
                    }
                elif language == "fr" or language == "French":
                    chapter = {
                        'title': f'Réflexions sur la Vie {i-len(chapter_templates)+1}',
                        'content': 'Chaque expérience de vie mérite d\'être chérie, et chaque moment a sa signification unique. En regardant en arrière, je suis reconnaissant pour le passé; en regardant vers l\'avenir, je suis rempli d\'espoir et d\'attente pour l\'avenir.'
                    }
                elif language == "it" or language == "Italian":
                    chapter = {
                        'title': f'Riflessioni sulla Vita {i-len(chapter_templates)+1}',
                        'content': 'Ogni esperienza di vita vale la pena di essere custodita, e ogni momento ha il suo significato unico. Guardando indietro, sono grato per il passato; guardando avanti, sono pieno di speranza e aspettativa per il futuro.'
                    }
                else:
                    chapter = {
                        'title': f'Life Reflections {i-len(chapter_templates)+1}',
                        'content': 'Every life experience is worth treasuring, and every moment has its unique meaning. Looking back, I am grateful for the past; looking forward, I am filled with hope and anticipation for the future.'
                    }
            
            # 分配图片
            chapter['image'] = images[i] if i < len(images) else None
            chapters.append(chapter)
        
        return chapters
    
    def _generate_cover_page(self, c, title, images, language):
        """生成封面页"""
        logger.info("🎨 生成封面页...")
        
        # 获取封面布局
        layout = self.layout_engine.get_cover_layout()
        
        # 绘制背景（可选）
        c.setFillColor(white)
        c.rect(0, 0, self.page_width, self.page_height, fill=1)
        
        # 书名
        title_style = self.layout_engine.get_style('title')
        safe_title = self.font_manager.get_safe_text(title)
        
        c.setFont(title_style.fontName, title_style.fontSize)
        c.setFillColor(title_style.textColor)
        
        # 居中绘制标题
        title_width = c.stringWidth(safe_title, title_style.fontName, title_style.fontSize)
        title_x = (self.page_width - title_width) / 2
        c.drawString(title_x, layout['title_y'], safe_title)
        
        # 副标题（生成时间）
        if language.startswith('zh'):
            subtitle = f"生成时间：{datetime.now().strftime('%Y年%m月%d日')}"
        elif language == "pt" or language == "Portuguese":
            subtitle = f"Gerado: {datetime.now().strftime('%d de %B de %Y')}"
        elif language == "es" or language == "Spanish":
            subtitle = f"Generado: {datetime.now().strftime('%d de %B de %Y')}"
        elif language == "fr" or language == "French":
            subtitle = f"Généré: {datetime.now().strftime('%d %B %Y')}"
        elif language == "it" or language == "Italian":
            subtitle = f"Generato: {datetime.now().strftime('%d %B %Y')}"
        else:
            subtitle = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
        
        subtitle_style = self.layout_engine.get_style('subtitle')
        c.setFont(subtitle_style.fontName, subtitle_style.fontSize)
        c.setFillColor(subtitle_style.textColor)
        
        subtitle_width = c.stringWidth(subtitle, subtitle_style.fontName, subtitle_style.fontSize)
        subtitle_x = (self.page_width - subtitle_width) / 2
        c.drawString(subtitle_x, layout['subtitle_y'], subtitle)
        
        # 封面图片
        if images:
            try:
                img_reader = ImageReader(str(images[0]))
                original_width, original_height = img_reader.getSize()
                
                # 计算封面图片尺寸
                display_width, display_height = self.layout_engine.calculate_image_size(
                    original_width, original_height, 
                    layout['image_width'], layout['image_height']
                )
                
                # 居中显示图片
                img_x = (self.page_width - display_width) / 2
                img_y = layout['image_y'] - display_height / 2
                
                c.drawImage(img_reader, img_x, img_y, display_width, display_height)
                
            except Exception as e:
                logger.warning(f"⚠️ 封面图片添加失败: {e}")
        
        # 页脚品牌标识
        c.setFont('Helvetica', 10)
        c.setFillColor(gray)
        brand_text = "Created with Biography AI Agent"
        brand_width = c.stringWidth(brand_text, 'Helvetica', 10)
        brand_x = (self.page_width - brand_width) / 2
        c.drawString(brand_x, layout['date_y'], brand_text)
        
        # 换页
        c.showPage()
    
    def _generate_table_of_contents(self, c, chapters):
        """生成目录页"""
        logger.info("📑 生成目录页...")
        
        layout = self.layout_engine.get_toc_layout()
        
        # 目录标题
        title_style = self.layout_engine.get_style('title')
        c.setFont(title_style.fontName, title_style.fontSize)
        c.setFillColor(title_style.textColor)
        
        toc_title = "目录"
        title_width = c.stringWidth(toc_title, title_style.fontName, title_style.fontSize)
        title_x = (self.page_width - title_width) / 2
        c.drawString(title_x, layout['title_y'], toc_title)
        
        # 目录内容
        chapter_style = self.layout_engine.get_style('section')
        c.setFont(chapter_style.fontName, chapter_style.fontSize)
        c.setFillColor(chapter_style.textColor)
        
        y_position = layout['content_start_y']
        
        for i, chapter in enumerate(chapters):
            if y_position < self.layout_engine.bottom_margin:
                c.showPage()
                y_position = layout['content_start_y']
            
            chapter_line = f"第{i+1}章  {chapter['title']}"
            safe_line = self.font_manager.get_safe_text(chapter_line)
            
            c.drawString(layout['indent'], y_position, safe_line)
            y_position -= layout['line_height']
        
        # 换页
        c.showPage()
    
    def _generate_content_pages(self, c, chapters, images):
        """生成内容页面"""
        logger.info("📄 生成内容页面...")
        
        for i, chapter in enumerate(chapters):
            self._generate_chapter_page(c, i+1, chapter)
    
    def _generate_chapter_page(self, c, chapter_num, chapter):
        """生成单个章节页面"""
        
        y_position = self.page_height - self.layout_engine.top_margin
        
        # 章节标题
        chapter_title = self.layout_engine.format_chapter_title(chapter_num, chapter['title'])
        safe_title = self.font_manager.get_safe_text(chapter_title)
        
        title_style = self.layout_engine.get_style('chapter')
        c.setFont(title_style.fontName, title_style.fontSize)
        c.setFillColor(title_style.textColor)
        c.drawString(self.layout_engine.inner_margin, y_position, safe_title)
        
        y_position -= title_style.fontSize + title_style.spaceAfter
        
        # 章节内容
        content_chunks = self.layout_engine.split_long_text(chapter['content'], 800)
        
        body_style = self.layout_engine.get_style('body')
        c.setFont(body_style.fontName, body_style.fontSize)
        c.setFillColor(body_style.textColor)
        
        for chunk in content_chunks:
            # 检查是否需要换页
            if y_position < self.layout_engine.bottom_margin + 100:
                self._add_page_footer(c)
                c.showPage()
                y_position = self.page_height - self.layout_engine.top_margin
            
            # 分段落绘制文本
            paragraphs = chunk.split('\n\n')
            for para in paragraphs:
                if not para.strip():
                    continue
                
                # 自动换行
                words = para.split()
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if c.stringWidth(test_line, body_style.fontName, body_style.fontSize) < self.layout_engine.text_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                
                if current_line:
                    lines.append(current_line)
                
                # 绘制行
                for line in lines:
                    if y_position < self.layout_engine.bottom_margin + 50:
                        self._add_page_footer(c)
                        c.showPage()
                        y_position = self.page_height - self.layout_engine.top_margin
                    
                    c.drawString(self.layout_engine.inner_margin, y_position, line)
                    y_position -= body_style.leading
                
                y_position -= body_style.spaceAfter
        
        # 添加章节图片
        if chapter.get('image'):
            y_position -= 30  # 额外间距
            
            try:
                img_reader = ImageReader(str(chapter['image']))
                original_width, original_height = img_reader.getSize()
                
                display_width, display_height = self.layout_engine.calculate_image_size(
                    original_width, original_height
                )
                
                # 检查图片是否需要换页
                if y_position - display_height < self.layout_engine.bottom_margin + 50:
                    self._add_page_footer(c)
                    c.showPage()
                    y_position = self.page_height - self.layout_engine.top_margin
                
                # 居中显示图片
                img_x = self.layout_engine.inner_margin + (self.layout_engine.text_width - display_width) / 2
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
        
        title_style = self.layout_engine.get_style('subtitle')
        c.setFont(title_style.fontName, title_style.fontSize)
        c.setFillColor(title_style.textColor)
        
        thank_you = "感谢使用 Biography AI Agent"
        title_width = c.stringWidth(thank_you, title_style.fontName, title_style.fontSize)
        title_x = (self.page_width - title_width) / 2
        c.drawString(title_x, y_position, thank_you)
        
        # 生成信息
        y_position -= 60
        
        body_style = self.layout_engine.get_style('body')
        c.setFont(body_style.fontName, body_style.fontSize)
        c.setFillColor(body_style.textColor)
        
        info_lines = [
            f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            "这是一份由人工智能协助创作的个人传记",
            "记录了珍贵的人生回忆和美好时光"
        ]
        
        for line in info_lines:
            line_width = c.stringWidth(line, body_style.fontName, body_style.fontSize)
            line_x = (self.page_width - line_width) / 2
            c.drawString(line_x, y_position, line)
            y_position -= body_style.leading
        
        self._add_page_footer(c)
        c.showPage()
    
    def _add_page_footer(self, c):
        """添加页脚"""
        footer_style = self.layout_engine.get_style('footer')
        c.setFont(footer_style.fontName, footer_style.fontSize)
        c.setFillColor(footer_style.textColor)
        
        footer_text = "Biography AI Agent"
        footer_width = c.stringWidth(footer_text, footer_style.fontName, footer_style.fontSize)
        footer_x = (self.page_width - footer_width) / 2
        c.drawString(footer_x, 50, footer_text)
    
    def _print_generation_stats(self, pdf_path, chapters, images):
        """输出生成统计信息"""
        file_size = Path(pdf_path).stat().st_size
        
        logger.info("✅ 专业PDF生成完成!")
        logger.info(f"📊 生成统计:")
        logger.info(f"   - 文件路径: {pdf_path}")
        logger.info(f"   - 文件大小: {file_size / 1024:.1f} KB")
        logger.info(f"   - 章节数量: {len(chapters)}")
        logger.info(f"   - 图片数量: {len(images)}")
        logger.info(f"   - 字体系统: {self.font_manager.chinese_font}")

# 全局实例
professional_pdf_generator = ProfessionalPDFGenerator() 