#!/usr/bin/env python3
"""
轻量级PDF生成器
为Vercel部署优化，避免使用重型依赖如reportlab
使用纯Python实现简单的PDF生成
"""

import os
import io
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class LightweightPDFGenerator:
    """轻量级PDF生成器"""
    
    def __init__(self):
        self.margin = 50
        self.page_width = 595  # A4宽度
        self.page_height = 842  # A4高度
        self.font_size = 12
        self.line_height = 18
        
    def generate_pdf_html(self, content: str, title: str = "个人传记", 
                         style: str = "classic", language: str = "zh-CN") -> str:
        """
        生成PDF的HTML版本（可用于后续转换）
        这个方法生成格式化的HTML，可以被现代浏览器转换为PDF
        """
        
        # 样式定义
        styles = {
            "classic": {
                "font_family": "serif",
                "color_scheme": "#2c3e50",
                "accent_color": "#3498db"
            },
            "modern": {
                "font_family": "sans-serif", 
                "color_scheme": "#2c3e50",
                "accent_color": "#e74c3c"
            },
            "elegant": {
                "font_family": "serif",
                "color_scheme": "#2c2c2c", 
                "accent_color": "#8b4513"
            }
        }
        
        style_config = styles.get(style, styles["classic"])
        
        # 语言相关配置
        lang_config = {
            "zh-CN": {
                "direction": "ltr",
                "font_stack": "'Noto Sans SC', 'Source Han Sans SC', 'Microsoft YaHei', sans-serif"
            },
            "en": {
                "direction": "ltr", 
                "font_stack": "'Times New Roman', Times, serif"
            },
            "ja": {
                "direction": "ltr",
                "font_stack": "'Noto Sans JP', 'Hiragino Sans', sans-serif"
            },
            "ko": {
                "direction": "ltr",
                "font_stack": "'Noto Sans KR', 'Malgun Gothic', sans-serif"
            }
        }
        
        lang_settings = lang_config.get(language, lang_config["zh-CN"])
        
        html_template = f"""
<!DOCTYPE html>
<html lang="{language}">
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
            font-family: {lang_settings['font_stack']};
            font-size: 14px;
            line-height: 1.8;
            color: {style_config['color_scheme']};
            direction: {lang_settings['direction']};
            margin: 0;
            padding: 0;
            background: white;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 2px solid {style_config['accent_color']};
            padding-bottom: 20px;
        }}
        
        .title {{
            font-size: 28px;
            font-weight: bold;
            color: {style_config['accent_color']};
            margin: 0;
        }}
        
        .subtitle {{
            font-size: 16px;
            color: #666;
            margin-top: 10px;
        }}
        
        .content {{
            text-align: justify;
            text-justify: inter-word;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 20px;
            font-weight: bold;
            color: {style_config['accent_color']};
            margin-bottom: 15px;
            border-left: 4px solid {style_config['accent_color']};
            padding-left: 15px;
        }}
        
        .paragraph {{
            margin-bottom: 15px;
            text-indent: 2em;
        }}
        
        .footer {{
            margin-top: 50px;
            text-align: center;
            font-size: 12px;
            color: #888;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
        
        .quote {{
            font-style: italic;
            padding: 15px;
            border-left: 3px solid {style_config['accent_color']};
            background-color: #f8f9fa;
            margin: 20px 0;
        }}
        
        @media print {{
            body {{
                font-size: 12px;
                line-height: 1.6;
            }}
            
            .header {{
                page-break-after: avoid;
            }}
            
            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">{title}</h1>
            <div class="subtitle">生成时间：{datetime.now().strftime('%Y年%m月%d日')}</div>
        </div>
        
        <div class="content">
            {self._format_content(content)}
        </div>
        
        <div class="footer">
            <p>本传记由AI智能生成，仅供参考</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html_template.strip()
    
    def _format_content(self, content: str) -> str:
        """格式化内容为HTML"""
        if not content:
            return "<p>暂无内容</p>"
        
        # 简单的段落分割
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # 检查是否为标题（简单检测）
            if (paragraph.startswith('#') or 
                len(paragraph) < 50 and 
                any(keyword in paragraph for keyword in ['章', '节', '部分', '引言', '结语', '总结'])):
                # 移除可能的标记符号
                clean_title = paragraph.lstrip('#').strip()
                formatted_paragraphs.append(f'<div class="section-title">{clean_title}</div>')
            else:
                # 普通段落
                formatted_paragraphs.append(f'<div class="paragraph">{paragraph}</div>')
        
        return '\n'.join(formatted_paragraphs)
    
    def generate_text_pdf(self, content: str, title: str = "个人传记") -> str:
        """
        生成纯文本格式的PDF内容
        返回可以保存为.txt文件的格式化文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"{title:^60}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")
        
        # 格式化内容
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 简单的文本换行处理
            words = paragraph.split()
            current_line = ""
            for word in words:
                if len(current_line + word) > 70:
                    lines.append(current_line.strip())
                    current_line = word + " "
                else:
                    current_line += word + " "
            
            if current_line.strip():
                lines.append(current_line.strip())
            lines.append("")
        
        lines.append("")
        lines.append("-" * 60)
        lines.append("本传记由AI智能生成，仅供参考")
        lines.append("=" * 60)
        
        return '\n'.join(lines)
    
    def save_html_pdf(self, content: str, output_path: str, 
                      title: str = "个人传记", style: str = "classic", 
                      language: str = "zh-CN") -> str:
        """保存HTML格式的PDF"""
        html_content = self.generate_pdf_html(content, title, style, language)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def save_text_pdf(self, content: str, output_path: str, 
                      title: str = "个人传记") -> str:
        """保存文本格式的PDF"""
        text_content = self.generate_text_pdf(content, title)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return output_path

# 便捷函数
def generate_lightweight_pdf(content: str, output_path: str, 
                           title: str = "个人传记", 
                           format_type: str = "html",
                           style: str = "classic",
                           language: str = "zh-CN") -> str:
    """
    生成轻量级PDF
    
    Args:
        content: 传记内容
        output_path: 输出路径
        title: 标题
        format_type: 格式类型 ("html" 或 "text")
        style: 样式 ("classic", "modern", "elegant")
        language: 语言代码
    
    Returns:
        输出文件路径
    """
    generator = LightweightPDFGenerator()
    
    if format_type == "html":
        return generator.save_html_pdf(content, output_path, title, style, language)
    else:
        return generator.save_text_pdf(content, output_path, title)

# 测试代码
if __name__ == "__main__":
    # 测试用例
    test_content = """
    # 引言
    
    这是一个测试传记的开始。
    
    # 早期生活
    
    在这个章节中，我们将探讨主人公的早期生活经历。
    
    这是一个关于成长的故事，充满了挑战和机遇。
    
    # 成就与贡献
    
    主人公在其生涯中取得了许多重要的成就。
    
    # 结语
    
    这是一个鼓舞人心的人生故事。
    """
    
    # 生成HTML版本
    html_path = "/tmp/test_biography.html"
    generate_lightweight_pdf(test_content, html_path, "测试传记", "html")
    print(f"HTML版本已保存到: {html_path}")
    
    # 生成文本版本  
    text_path = "/tmp/test_biography.txt"
    generate_lightweight_pdf(test_content, text_path, "测试传记", "text")
    print(f"文本版本已保存到: {text_path}") 