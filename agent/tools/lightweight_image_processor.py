#!/usr/bin/env python3
"""
轻量级图像处理器
为Vercel部署优化，使用PIL/Pillow替代OpenCV
提供基本的图像处理功能
"""

import os
import io
import base64
from typing import List, Tuple, Optional, Union
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import logging

logger = logging.getLogger(__name__)

class LightweightImageProcessor:
    """轻量级图像处理器"""
    
    def __init__(self):
        self.max_image_size = (1920, 1080)  # 最大图像尺寸
        self.compression_quality = 85
        self.supported_formats = {'JPEG', 'PNG', 'WEBP', 'BMP', 'GIF'}
    
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """加载图像文件"""
        try:
            with Image.open(image_path) as img:
                return img.copy()
        except Exception as e:
            logger.error(f"加载图像失败 {image_path}: {e}")
            return None
    
    def load_image_from_bytes(self, image_bytes: bytes) -> Optional[Image.Image]:
        """从字节数据加载图像"""
        try:
            return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"从字节数据加载图像失败: {e}")
            return None
    
    def load_image_from_base64(self, base64_string: str) -> Optional[Image.Image]:
        """从base64字符串加载图像"""
        try:
            # 移除可能的data URL前缀
            if base64_string.startswith('data:'):
                base64_string = base64_string.split(',', 1)[1]
            
            image_bytes = base64.b64decode(base64_string)
            return self.load_image_from_bytes(image_bytes)
        except Exception as e:
            logger.error(f"从base64加载图像失败: {e}")
            return None
    
    def resize_image(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """调整图像大小"""
        if max_size is None:
            max_size = self.max_image_size
        
        # 计算新的尺寸，保持宽高比
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        return image
    
    def compress_image(self, image: Image.Image, quality: int = None) -> bytes:
        """压缩图像"""
        if quality is None:
            quality = self.compression_quality
        
        # 转换为RGB格式（如果需要）
        if image.mode in ('RGBA', 'LA', 'P'):
            # 创建白色背景
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # 保存为JPEG格式
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    
    def to_base64(self, image: Image.Image, format: str = 'JPEG', quality: int = None) -> str:
        """将图像转换为base64字符串"""
        if quality is None:
            quality = self.compression_quality
        
        output = io.BytesIO()
        
        # 根据格式调整图像
        if format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
            # JPEG不支持透明度，创建白色背景
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # 保存图像
        save_kwargs = {'format': format, 'optimize': True}
        if format.upper() == 'JPEG':
            save_kwargs['quality'] = quality
        
        image.save(output, **save_kwargs)
        
        # 转换为base64
        image_bytes = output.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def enhance_image(self, image: Image.Image, 
                     brightness: float = 1.0,
                     contrast: float = 1.0, 
                     saturation: float = 1.0,
                     sharpness: float = 1.0) -> Image.Image:
        """增强图像质量"""
        try:
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation)
            
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpness)
            
            return image
        except Exception as e:
            logger.error(f"图像增强失败: {e}")
            return image
    
    def apply_filter(self, image: Image.Image, filter_type: str = "none") -> Image.Image:
        """应用滤镜效果"""
        try:
            if filter_type == "blur":
                return image.filter(ImageFilter.BLUR)
            elif filter_type == "sharpen":
                return image.filter(ImageFilter.SHARPEN)
            elif filter_type == "smooth":
                return image.filter(ImageFilter.SMOOTH)
            elif filter_type == "edge_enhance":
                return image.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == "detail":
                return image.filter(ImageFilter.DETAIL)
            else:
                return image
        except Exception as e:
            logger.error(f"应用滤镜失败: {e}")
            return image
    
    def auto_orient(self, image: Image.Image) -> Image.Image:
        """自动调整图像方向（基于EXIF数据）"""
        try:
            return ImageOps.exif_transpose(image)
        except Exception as e:
            logger.error(f"自动调整方向失败: {e}")
            return image
    
    def create_thumbnail(self, image: Image.Image, size: Tuple[int, int] = (300, 300)) -> Image.Image:
        """创建缩略图"""
        try:
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
            return thumbnail
        except Exception as e:
            logger.error(f"创建缩略图失败: {e}")
            return image
    
    def process_image_for_analysis(self, image_path: str) -> Optional[str]:
        """
        为AI分析优化图像
        返回base64编码的图像数据
        """
        try:
            # 加载图像
            image = self.load_image(image_path)
            if image is None:
                return None
            
            # 自动调整方向
            image = self.auto_orient(image)
            
            # 调整大小（AI分析不需要太大的图片）
            analysis_size = (1024, 1024)
            image = self.resize_image(image, analysis_size)
            
            # 轻微增强图像质量
            image = self.enhance_image(image, 
                                     brightness=1.1,
                                     contrast=1.1,
                                     sharpness=1.1)
            
            # 转换为base64
            return self.to_base64(image, 'JPEG', 85)
            
        except Exception as e:
            logger.error(f"处理图像用于分析失败 {image_path}: {e}")
            return None
    
    def batch_process_images(self, image_paths: List[str], 
                           output_dir: str = None,
                           max_size: Tuple[int, int] = None,
                           quality: int = None) -> List[str]:
        """批量处理图像"""
        processed_paths = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # 加载图像
                image = self.load_image(image_path)
                if image is None:
                    continue
                
                # 处理图像
                image = self.auto_orient(image)
                image = self.resize_image(image, max_size)
                
                # 生成输出路径
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    output_path = os.path.join(output_dir, f"{base_name}_processed.jpg")
                else:
                    output_path = image_path.replace('.', '_processed.')
                
                # 压缩并保存
                compressed_bytes = self.compress_image(image, quality)
                with open(output_path, 'wb') as f:
                    f.write(compressed_bytes)
                
                processed_paths.append(output_path)
                logger.info(f"已处理图像 {i+1}/{len(image_paths)}: {output_path}")
                
            except Exception as e:
                logger.error(f"处理图像失败 {image_path}: {e}")
                continue
        
        return processed_paths
    
    def get_image_info(self, image_path: str) -> Optional[dict]:
        """获取图像信息"""
        try:
            with Image.open(image_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                }
        except Exception as e:
            logger.error(f"获取图像信息失败 {image_path}: {e}")
            return None

# 便捷函数
def process_image_for_ai(image_path: str) -> Optional[str]:
    """
    为AI分析处理图像
    返回base64编码的图像数据
    """
    processor = LightweightImageProcessor()
    return processor.process_image_for_analysis(image_path)

def compress_image_file(image_path: str, output_path: str = None, 
                       quality: int = 85, max_size: Tuple[int, int] = None) -> str:
    """
    压缩图像文件
    """
    processor = LightweightImageProcessor()
    
    # 加载图像
    image = processor.load_image(image_path)
    if image is None:
        raise ValueError(f"无法加载图像: {image_path}")
    
    # 处理图像
    image = processor.auto_orient(image)
    if max_size:
        image = processor.resize_image(image, max_size)
    
    # 生成输出路径
    if output_path is None:
        base, ext = os.path.splitext(image_path)
        output_path = f"{base}_compressed.jpg"
    
    # 压缩并保存
    compressed_bytes = processor.compress_image(image, quality)
    with open(output_path, 'wb') as f:
        f.write(compressed_bytes)
    
    return output_path

# 测试代码
if __name__ == "__main__":
    # 测试用例
    processor = LightweightImageProcessor()
    
    # 测试图像信息获取
    test_image = "test_image.jpg"  # 需要一个测试图像
    if os.path.exists(test_image):
        info = processor.get_image_info(test_image)
        print(f"图像信息: {info}")
        
        # 测试处理
        base64_data = processor.process_image_for_analysis(test_image)
        if base64_data:
            print(f"Base64数据长度: {len(base64_data)}")
    else:
        print("测试图像不存在，跳过测试") 