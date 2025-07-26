"""
文件服务
负责文件的上传、存储和访问管理
"""

import os
import uuid
import shutil
import asyncio
from typing import Optional, List
from fastapi import UploadFile
from pathlib import Path


class FileService:
    """文件服务"""
    
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = base_dir
        self.uploads_dir = os.path.join(base_dir, "images")
        self.media_dir = os.path.join(base_dir, "media")
        self.temp_dir = os.path.join(base_dir, "temp")
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.base_dir,
            self.uploads_dir,
            self.media_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    async def save_uploaded_file(self, file: UploadFile) -> str:
        """
        保存上传的文件
        
        Args:
            file: 上传的文件对象
            
        Returns:
            str: 保存后的文件路径
        """
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.uploads_dir, unique_filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")
    
    async def save_multiple_files(self, files: List[UploadFile]) -> List[str]:
        """
        批量保存上传的文件
        
        Args:
            files: 上传的文件列表
            
        Returns:
            List[str]: 保存后的文件路径列表
        """
        tasks = []
        for file in files:
            if file.content_type.startswith('image/'):
                tasks.append(self.save_uploaded_file(file))
        
        if not tasks:
            return []
        
        file_paths = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤出成功保存的文件路径
        valid_paths = []
        for path in file_paths:
            if isinstance(path, str):
                valid_paths.append(path)
            else:
                print(f"保存文件失败: {path}")
        
        return valid_paths
    
    def get_public_url(self, file_path: str, base_url: str = "https://biography-ai004.vercel.app") -> str:
        """
        获取文件的公共访问URL
        
        Args:
            file_path: 文件路径
            base_url: 基础URL
            
        Returns:
            str: 公共访问URL
        """
        # 将文件路径转换为相对于media目录的路径
        relative_path = os.path.relpath(file_path, self.base_dir)
        return f"{base_url}/media/{relative_path}"
    
    def copy_to_media(self, source_path: str) -> str:
        """
        将文件复制到media目录用于公共访问
        
        Args:
            source_path: 源文件路径
            
        Returns:
            str: media目录中的文件路径
        """
        try:
            filename = os.path.basename(source_path)
            media_path = os.path.join(self.media_dir, filename)
            
            # 如果文件已存在，生成新的文件名
            if os.path.exists(media_path):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(media_path):
                    new_filename = f"{name}_{counter}{ext}"
                    media_path = os.path.join(self.media_dir, new_filename)
                    counter += 1
            
            shutil.copy2(source_path, media_path)
            return media_path
            
        except Exception as e:
            raise Exception(f"复制文件到media目录失败: {str(e)}")
    
    def create_temp_file(self, suffix: str = ".tmp") -> str:
        """
        创建临时文件路径
        
        Args:
            suffix: 文件后缀
            
        Returns:
            str: 临时文件路径
        """
        temp_filename = f"{uuid.uuid4()}{suffix}"
        return os.path.join(self.temp_dir, temp_filename)
    
    async def cleanup_temp_files(self, max_age_hours: int = 24):
        """
        清理临时文件
        
        Args:
            max_age_hours: 文件最大保存时间（小时）
        """
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        print(f"清理临时文件: {filename}")
            
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    
    def get_file_info(self, file_path: str) -> dict:
        """
        获取文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            dict: 文件信息
        """
        try:
            if not os.path.exists(file_path):
                return {"error": "文件不存在"}
            
            stat = os.stat(file_path)
            return {
                "filename": os.path.basename(file_path),
                "size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "extension": os.path.splitext(file_path)[1],
                "exists": True
            }
            
        except Exception as e:
            return {"error": f"获取文件信息失败: {str(e)}"}
    
    def validate_image_file(self, file_path: str) -> bool:
        """
        验证是否为有效的图片文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否为有效图片
        """
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                img.verify()
            return True
        except Exception:
            return False
    
    def get_file_size_mb(self, file_path: str) -> float:
        """
        获取文件大小（MB）
        
        Args:
            file_path: 文件路径
            
        Returns:
            float: 文件大小（MB）
        """
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    async def compress_image(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        max_size: tuple = (1920, 1080),
        quality: int = 85
    ) -> str:
        """
        压缩图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（可选）
            max_size: 最大尺寸 (width, height)
            quality: 压缩质量 (1-100)
            
        Returns:
            str: 压缩后的图片路径
        """
        try:
            from PIL import Image
            
            if output_path is None:
                name, ext = os.path.splitext(input_path)
                output_path = f"{name}_compressed{ext}"
            
            with Image.open(input_path) as img:
                # 转换为RGB模式（如果需要）
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # 调整大小
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存压缩后的图片
                img.save(output_path, "JPEG", quality=quality, optimize=True)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"压缩图片失败: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """
        删除文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否删除成功
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {e}")
            return False
    
    def create_directory(self, dir_path: str) -> bool:
        """
        创建目录
        
        Args:
            dir_path: 目录路径
            
        Returns:
            bool: 是否创建成功
        """
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"创建目录失败: {e}")
            return False
    
    def list_files(self, directory: str, extension: Optional[str] = None) -> List[str]:
        """
        列出目录下的文件
        
        Args:
            directory: 目录路径
            extension: 文件扩展名过滤（可选）
            
        Returns:
            List[str]: 文件路径列表
        """
        try:
            if not os.path.exists(directory):
                return []
            
            files = []
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    if extension is None or filename.lower().endswith(extension.lower()):
                        files.append(file_path)
            
            return files
            
        except Exception as e:
            print(f"列出文件失败: {e}")
            return [] 