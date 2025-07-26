"""
二维码生成工具
为图片和视频生成二维码，扫描后可查看原始内容
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional
import asyncio

from ..core.models import QRCodeConfig


class QRGenerator:
    """二维码生成工具"""
    
    def __init__(self, config: Optional[QRCodeConfig] = None):
        self.config = config or QRCodeConfig()
        self.output_dir = "qr_codes"
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """确保输出目录存在"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    async def generate_qr_code(self, url: str, filename: str) -> str:
        """
        生成二维码
        
        Args:
            url: 要编码的URL
            filename: 输出文件名（不含扩展名）
            
        Returns:
            str: 生成的二维码文件路径
        """
        try:
            # 创建二维码实例
            qr = qrcode.QRCode(
                version=1,
                error_correction=self._get_error_correction_level(),
                box_size=10,
                border=self.config.border,
            )
            
            # 添加数据
            qr.add_data(url)
            qr.make(fit=True)
            
            # 创建二维码图片
            qr_img = qr.make_image(
                fill_color=self.config.fill_color,
                back_color=self.config.back_color
            )
            
            # 调整大小
            qr_img = qr_img.resize((self.config.size, self.config.size), Image.Resampling.LANCZOS)
            
            # 保存文件
            output_path = os.path.join(self.output_dir, f"{filename}.png")
            qr_img.save(output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"生成二维码失败: {str(e)}")
    
    async def generate_styled_qr_code(
        self, 
        url: str, 
        filename: str,
        logo_path: Optional[str] = None,
        style: str = "default"
    ) -> str:
        """
        生成带样式的二维码
        
        Args:
            url: 要编码的URL
            filename: 输出文件名
            logo_path: Logo图片路径（可选）
            style: 二维码样式
            
        Returns:
            str: 生成的二维码文件路径
        """
        # 先生成基础二维码
        qr_path = await self.generate_qr_code(url, filename)
        
        # 如果有logo，添加logo
        if logo_path and os.path.exists(logo_path):
            qr_path = await self._add_logo_to_qr(qr_path, logo_path)
        
        # 应用样式
        if style != "default":
            qr_path = await self._apply_style(qr_path, style)
        
        return qr_path
    
    async def _add_logo_to_qr(self, qr_path: str, logo_path: str) -> str:
        """在二维码中心添加logo"""
        try:
            # 打开二维码和logo
            qr_img = Image.open(qr_path)
            logo_img = Image.open(logo_path)
            
            # 计算logo大小（二维码大小的1/5）
            logo_size = qr_img.size[0] // 5
            logo_img = logo_img.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # 创建白色背景的logo（提高识别率）
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
            logo_bg.paste(logo_img, (10, 10))
            
            # 计算位置（中心）
            pos = ((qr_img.size[0] - logo_bg.size[0]) // 2,
                   (qr_img.size[1] - logo_bg.size[1]) // 2)
            
            # 粘贴logo
            qr_img.paste(logo_bg, pos)
            
            # 保存
            qr_img.save(qr_path)
            
            return qr_path
            
        except Exception as e:
            print(f"添加logo失败: {e}")
            return qr_path
    
    async def _apply_style(self, qr_path: str, style: str) -> str:
        """应用二维码样式"""
        try:
            qr_img = Image.open(qr_path)
            
            if style == "rounded":
                # 圆角样式
                qr_img = self._add_rounded_corners(qr_img)
            elif style == "gradient":
                # 渐变样式
                qr_img = self._add_gradient_effect(qr_img)
            elif style == "shadow":
                # 阴影样式
                qr_img = self._add_shadow_effect(qr_img)
            
            # 保存样式化的二维码
            qr_img.save(qr_path)
            
            return qr_path
            
        except Exception as e:
            print(f"应用样式失败: {e}")
            return qr_path
    
    def _add_rounded_corners(self, img: Image.Image, radius: int = 20) -> Image.Image:
        """添加圆角效果"""
        # 创建圆角蒙版
        mask = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([0, 0, img.size[0], img.size[1]], radius, fill=255)
        
        # 创建新图像
        result = Image.new('RGBA', img.size, (255, 255, 255, 0))
        result.paste(img, (0, 0))
        result.putalpha(mask)
        
        return result
    
    def _add_gradient_effect(self, img: Image.Image) -> Image.Image:
        """添加渐变效果"""
        # 简化实现：这里可以添加更复杂的渐变逻辑
        return img
    
    def _add_shadow_effect(self, img: Image.Image) -> Image.Image:
        """添加阴影效果"""
        # 创建阴影
        shadow = Image.new('RGBA', (img.size[0] + 10, img.size[1] + 10), (0, 0, 0, 0))
        shadow_img = Image.new('RGBA', img.size, (0, 0, 0, 100))
        shadow.paste(shadow_img, (5, 5))
        shadow.paste(img, (0, 0), img)
        
        return shadow
    
    async def generate_batch_qr_codes(
        self, 
        url_filename_pairs: List[tuple]
    ) -> Dict[str, str]:
        """
        批量生成二维码
        
        Args:
            url_filename_pairs: (url, filename) 元组列表
            
        Returns:
            Dict[str, str]: 文件名到路径的映射
        """
        tasks = []
        for url, filename in url_filename_pairs:
            tasks.append(self.generate_qr_code(url, filename))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        qr_paths = {}
        for i, result in enumerate(results):
            filename = url_filename_pairs[i][1]
            if isinstance(result, Exception):
                print(f"生成二维码 {filename} 失败: {result}")
            else:
                qr_paths[filename] = result
        
        return qr_paths
    
    async def generate_qr_with_text(
        self, 
        url: str, 
        filename: str,
        text: str,
        font_size: int = 24
    ) -> str:
        """
        生成带文字说明的二维码
        
        Args:
            url: 要编码的URL
            filename: 输出文件名
            text: 说明文字
            font_size: 字体大小
            
        Returns:
            str: 生成的二维码文件路径
        """
        try:
            # 先生成基础二维码
            qr_path = await self.generate_qr_code(url, f"temp_{filename}")
            qr_img = Image.open(qr_path)
            
            # 计算文字区域大小
            try:
                font = ImageFont.truetype("Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # 创建临时图像来测量文字大小
            temp_img = Image.new('RGB', (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            text_bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # 创建新图像（二维码 + 文字区域）
            total_width = max(qr_img.size[0], text_width + 20)
            total_height = qr_img.size[1] + text_height + 30
            
            final_img = Image.new('RGB', (total_width, total_height), 'white')
            
            # 粘贴二维码（居中）
            qr_x = (total_width - qr_img.size[0]) // 2
            final_img.paste(qr_img, (qr_x, 0))
            
            # 添加文字
            draw = ImageDraw.Draw(final_img)
            text_x = (total_width - text_width) // 2
            text_y = qr_img.size[1] + 10
            draw.text((text_x, text_y), text, fill='black', font=font)
            
            # 保存最终图像
            final_path = os.path.join(self.output_dir, f"{filename}.png")
            final_img.save(final_path)
            
            # 删除临时文件
            os.remove(qr_path)
            
            return final_path
            
        except Exception as e:
            raise Exception(f"生成带文字的二维码失败: {str(e)}")
    
    def _get_error_correction_level(self):
        """获取错误纠正级别"""
        levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        return levels.get(self.config.error_correction, qrcode.constants.ERROR_CORRECT_M)
    
    async def generate_media_qr_codes(
        self, 
        media_files: List[str],
        base_url: str
    ) -> Dict[str, str]:
        """
        为媒体文件生成二维码
        
        Args:
            media_files: 媒体文件路径列表
            base_url: 基础URL（用于构建完整的访问链接）
            
        Returns:
            Dict[str, str]: 媒体文件路径到二维码路径的映射
        """
        qr_codes = {}
        
        for media_file in media_files:
            try:
                # 构建访问URL
                filename = os.path.basename(media_file)
                media_url = f"{base_url}/media/{filename}"
                
                # 生成二维码文件名
                qr_filename = f"qr_{os.path.splitext(filename)[0]}"
                
                # 确定媒体类型
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                    media_type = "查看原图"
                elif file_ext in ['.mp4', '.avi', '.mov', '.mkv']:
                    media_type = "观看视频"
                else:
                    media_type = "查看文件"
                
                # 生成带文字的二维码
                qr_path = await self.generate_qr_with_text(
                    media_url, 
                    qr_filename,
                    f"扫码{media_type}"
                )
                
                qr_codes[media_file] = qr_path
                
            except Exception as e:
                print(f"为媒体文件 {media_file} 生成二维码失败: {e}")
        
        return qr_codes 