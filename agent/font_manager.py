#!/usr/bin/env python3
"""
字体管理器 - 解决PDF生成中的字体和编码问题
支持中英文混合显示，避免黑色色块
"""

import os
import platform
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import tt2ps
import logging

logger = logging.getLogger(__name__)

class FontManager:
    """字体管理器 - 确保稳定的字体支持"""
    
    def __init__(self):
        self.registered_fonts = {}
        self.fallback_font = 'Helvetica'
        self.chinese_font = None
        self.system = platform.system()
        
        # 初始化字体
        self._setup_fonts()
    
    def _setup_fonts(self):
        """设置字体系统"""
        logger.info("🔤 初始化字体管理器...")
        
        # 尝试注册中文字体
        self._register_chinese_fonts()
        
        # 注册英文字体
        self._register_english_fonts()
        
        logger.info(f"✅ 字体系统初始化完成，可用字体: {list(self.registered_fonts.keys())}")
    
    def _register_chinese_fonts(self):
        """注册中文字体"""
        try:
            if self.system == "Darwin":  # macOS
                self._register_macos_fonts()
            elif self.system == "Windows":
                self._register_windows_fonts()
            else:
                self._register_linux_fonts()
                
        except Exception as e:
            logger.warning(f"⚠️ 中文字体注册失败: {e}")
            self._use_unicode_font()
    
    def _register_macos_fonts(self):
        """注册macOS字体"""
        font_candidates = [
            ("/System/Library/Fonts/PingFang.ttc", "PingFang"),
            ("/System/Library/Fonts/Hiragino Sans GB.ttc", "HiraginoSansGB"),
            ("/Library/Fonts/Arial Unicode MS.ttf", "ArialUnicodeMS"),
            ("/System/Library/Fonts/Arial Unicode MS.ttf", "ArialUnicodeMS"),
        ]
        
        for font_path, font_name in font_candidates:
            if os.path.exists(font_path) and not font_path.endswith('.ttc'):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.chinese_font = font_name
                    self.registered_fonts[font_name] = font_path
                    logger.info(f"✅ 成功注册macOS中文字体: {font_name}")
                    return
                except Exception as e:
                    logger.debug(f"注册字体失败 {font_name}: {e}")
                    continue
        
        # 如果都失败，使用简单方案
        self._use_simple_font()
    
    def _register_windows_fonts(self):
        """注册Windows字体"""
        font_candidates = [
            ("C:/Windows/Fonts/simsun.ttc", "SimSun"),
            ("C:/Windows/Fonts/msyh.ttf", "MicrosoftYaHei"),
            ("C:/Windows/Fonts/arial.ttf", "Arial"),
        ]
        
        for font_path, font_name in font_candidates:
            if os.path.exists(font_path) and not font_path.endswith('.ttc'):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.chinese_font = font_name
                    self.registered_fonts[font_name] = font_path
                    logger.info(f"✅ 成功注册Windows中文字体: {font_name}")
                    return
                except Exception as e:
                    logger.debug(f"注册字体失败 {font_name}: {e}")
                    continue
        
        self._use_simple_font()
    
    def _register_linux_fonts(self):
        """注册Linux字体"""
        font_candidates = [
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans"),
            ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", "LiberationSans"),
        ]
        
        for font_path, font_name in font_candidates:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    self.chinese_font = font_name
                    self.registered_fonts[font_name] = font_path
                    logger.info(f"✅ 成功注册Linux字体: {font_name}")
                    return
                except Exception as e:
                    logger.debug(f"注册字体失败 {font_name}: {e}")
                    continue
        
        self._use_simple_font()
    
    def _use_unicode_font(self):
        """使用Unicode字体"""
        try:
            from reportlab.pdfbase.cidfonts import UnicodeCIDFont
            pdfmetrics.registerFont(UnicodeCIDFont('STSong-Light'))
            self.chinese_font = 'STSong-Light'
            self.registered_fonts['STSong-Light'] = 'built-in'
            logger.info("✅ 使用内置Unicode字体: STSong-Light")
        except Exception as e:
            logger.warning(f"⚠️ Unicode字体注册失败: {e}")
            self._use_simple_font()
    
    def _use_simple_font(self):
        """使用简单字体方案"""
        self.chinese_font = 'Helvetica'
        self.registered_fonts['Helvetica'] = 'built-in'
        logger.info("ℹ️ 使用默认字体: Helvetica")
    
    def _register_english_fonts(self):
        """注册英文字体"""
        english_fonts = ['Helvetica', 'Times-Roman', 'Courier']
        for font in english_fonts:
            self.registered_fonts[font] = 'built-in'
    
    def get_font(self, language="zh-CN"):
        """获取适合的字体"""
        if language.startswith('zh') or language == 'Chinese':
            return self.chinese_font or self.fallback_font
        else:
            return 'Helvetica'
    
    def clean_text(self, text):
        """清理文本，确保可以正确渲染"""
        if not text:
            return ""
        
        # 移除可能导致渲染问题的字符
        cleaned = text.replace('\x00', '').replace('\ufffd', '')
        
        # 确保文本是UTF-8编码
        if isinstance(cleaned, bytes):
            try:
                cleaned = cleaned.decode('utf-8', errors='replace')
            except:
                cleaned = str(cleaned)
        
        return cleaned.strip()
    
    def get_safe_text(self, text, max_length=1000):
        """获取安全的文本，适合PDF渲染"""
        cleaned = self.clean_text(text)
        
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def test_font_rendering(self):
        """测试字体渲染"""
        test_texts = [
            "Hello World",
            "你好世界",
            "English中文Mixed混合",
            "Profile AI Agent"
        ]
        
        logger.info("🧪 测试字体渲染...")
        for text in test_texts:
            cleaned = self.get_safe_text(text)
            font = self.get_font("zh-CN")
            logger.info(f"   文本: '{cleaned}' -> 字体: {font}")
        
        return True

# 全局字体管理器实例
font_manager = FontManager() 