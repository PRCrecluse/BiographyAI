"""
图片分析工具
使用AI服务分析图片内容，提取关键信息用于传记生成
"""

import os
import asyncio
from typing import Dict, Any, List
from PIL import Image, ExifTags
import cv2
import numpy as np

from ..services.ai_service import AIService
from ..core.models import ImageAnalysisResult


class ImageAnalyzer:
    """图片分析工具"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def analyze_image(self, image_path: str) -> ImageAnalysisResult:
        """
        全面分析图片内容
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            ImageAnalysisResult: 分析结果
        """
        # 基础信息提取
        basic_info = self._extract_basic_info(image_path)
        
        # AI分析
        ai_result = await self.ai_service.analyze_image_for_biography(image_path)
        
        # 合并结果
        ai_result.timestamp = basic_info.get("timestamp")
        ai_result.location = basic_info.get("location")
        
        return ai_result
    
    def _extract_basic_info(self, image_path: str) -> Dict[str, Any]:
        """提取图片基础信息（EXIF数据等）"""
        info = {}
        
        try:
            # 使用PIL读取EXIF数据
            with Image.open(image_path) as img:
                # 获取EXIF数据
                exif_data = img._getexif()
                
                if exif_data:
                    # 提取时间戳
                    for tag_id, value in exif_data.items():
                        tag = ExifTags.TAGS.get(tag_id, tag_id)
                        
                        if tag == "DateTime":
                            info["timestamp"] = str(value)
                        elif tag == "GPSInfo":
                            # 提取GPS信息
                            gps_info = self._extract_gps_info(value)
                            if gps_info:
                                info["location"] = gps_info
                
                # 获取图片基本信息
                info.update({
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode
                })
                
        except Exception as e:
            print(f"提取图片基础信息失败: {e}")
        
        return info
    
    def _extract_gps_info(self, gps_data: dict) -> str:
        """从GPS数据中提取位置信息"""
        try:
            if not gps_data:
                return None
            
            # 这里可以实现GPS坐标转换为地理位置的逻辑
            # 简化实现，返回坐标信息
            lat = gps_data.get(2)  # GPSLatitude
            lon = gps_data.get(4)  # GPSLongitude
            
            if lat and lon:
                return f"纬度: {lat}, 经度: {lon}"
            
        except Exception as e:
            print(f"提取GPS信息失败: {e}")
        
        return None
    
    async def analyze_multiple_images(self, image_paths: List[str]) -> List[ImageAnalysisResult]:
        """批量分析多张图片"""
        tasks = []
        for image_path in image_paths:
            tasks.append(self.analyze_image(image_path))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤出成功的结果
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"分析图片 {image_paths[i]} 失败: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    def detect_faces(self, image_path: str) -> List[Dict[str, Any]]:
        """检测图片中的人脸"""
        try:
            # 加载OpenCV人脸检测器
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # 读取图片
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 检测人脸
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_info = []
            for i, (x, y, w, h) in enumerate(faces):
                face_info.append({
                    "face_id": i,
                    "position": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                    "confidence": 0.8  # 简化的置信度
                })
            
            return face_info
            
        except Exception as e:
            print(f"人脸检测失败: {e}")
            return []
    
    def get_image_colors(self, image_path: str, num_colors: int = 5) -> List[str]:
        """提取图片主要颜色"""
        try:
            with Image.open(image_path) as img:
                # 转换为RGB模式
                img = img.convert('RGB')
                
                # 缩小图片以提高处理速度
                img.thumbnail((150, 150))
                
                # 转换为numpy数组
                img_array = np.array(img)
                pixels = img_array.reshape(-1, 3)
                
                # 使用KMeans聚类找出主要颜色
                from sklearn.cluster import KMeans
                
                kmeans = KMeans(n_clusters=num_colors, random_state=42)
                kmeans.fit(pixels)
                
                colors = []
                for color in kmeans.cluster_centers_:
                    # 转换为十六进制颜色码
                    hex_color = '#{:02x}{:02x}{:02x}'.format(
                        int(color[0]), int(color[1]), int(color[2])
                    )
                    colors.append(hex_color)
                
                return colors
                
        except Exception as e:
            print(f"颜色提取失败: {e}")
            return []
    
    def analyze_composition(self, image_path: str) -> Dict[str, Any]:
        """分析图片构图"""
        try:
            with Image.open(image_path) as img:
                width, height = img.size
                aspect_ratio = width / height
                
                composition_info = {
                    "aspect_ratio": round(aspect_ratio, 2),
                    "orientation": "横向" if aspect_ratio > 1 else "纵向" if aspect_ratio < 1 else "正方形",
                    "resolution": f"{width}x{height}",
                    "megapixels": round((width * height) / 1000000, 1)
                }
                
                # 简单的构图分析
                if aspect_ratio > 1.5:
                    composition_info["composition_type"] = "宽景构图"
                elif aspect_ratio < 0.7:
                    composition_info["composition_type"] = "竖向构图"
                else:
                    composition_info["composition_type"] = "标准构图"
                
                return composition_info
                
        except Exception as e:
            print(f"构图分析失败: {e}")
            return {}
    
    async def get_comprehensive_analysis(self, image_path: str) -> Dict[str, Any]:
        """获取图片全面分析结果"""
        # AI分析
        ai_analysis = await self.analyze_image(image_path)
        
        # 技术分析
        basic_info = self._extract_basic_info(image_path)
        faces = self.detect_faces(image_path)
        colors = self.get_image_colors(image_path)
        composition = self.analyze_composition(image_path)
        
        return {
            "ai_analysis": ai_analysis,
            "basic_info": basic_info,
            "faces": faces,
            "main_colors": colors,
            "composition": composition
        } 