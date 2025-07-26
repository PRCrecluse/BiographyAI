"""
Agent编排器 - 协调各个工具的调用，实现个人传记生成的完整流程
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .models import BiographyRequest, BiographyResponse, ProcessingStatus
from ..tools.image_analyzer import ImageAnalyzer
from ..tools.text_generator import TextGenerator
from ..tools.layout_engine import LayoutEngine
from ..tools.qr_generator import QRGenerator
from ..tools.pdf_generator import PDFGenerator
from ..services.ai_service import AIService
from ..services.file_service import FileService


class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProcessingTask:
    task_id: str
    status: TaskStatus
    progress: float
    message: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AgentOrchestrator:
    """
    Agent编排器 - 核心控制器
    负责协调各个工具，实现完整的个人传记生成流程
    """
    
    def __init__(
        self,
        ai_service: AIService,
        file_service: FileService
    ):
        self.ai_service = ai_service
        self.file_service = file_service
        
        # 初始化各个工具
        self.image_analyzer = ImageAnalyzer(ai_service)
        self.text_generator = TextGenerator(ai_service)
        self.layout_engine = LayoutEngine()
        self.qr_generator = QRGenerator()
        self.pdf_generator = PDFGenerator()
        
        # 任务管理
        self.tasks: Dict[str, ProcessingTask] = {}
        
        # 日志配置
        self.logger = logging.getLogger(__name__)
    
    async def create_biography(
        self, 
        request: BiographyRequest
    ) -> str:
        """
        创建个人传记的主要流程
        
        Args:
            request: 传记生成请求，包含图片文件和用户要求
            
        Returns:
            task_id: 任务ID，用于跟踪处理进度
        """
        task_id = f"biography_{request.user_id}_{asyncio.get_event_loop().time()}"
        
        # 创建任务
        task = ProcessingTask(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0.0,
            message="开始处理个人传记生成请求"
        )
        self.tasks[task_id] = task
        
        # 异步执行处理流程
        asyncio.create_task(self._process_biography(task_id, request))
        
        return task_id
    
    async def _process_biography(
        self, 
        task_id: str, 
        request: BiographyRequest
    ):
        """
        执行完整的传记生成流程
        """
        task = self.tasks[task_id]
        
        try:
            # 步骤1: 图片分析 (0-30%)
            task.status = TaskStatus.PROCESSING
            task.message = "正在分析上传的图片..."
            task.progress = 0.1
            
            image_analysis_results = await self._analyze_images(request.image_files)
            task.progress = 0.3
            
            # 步骤2: 生成传记内容 (30-60%)
            task.message = "正在生成个人传记内容..."
            
            biography_content = await self._generate_biography_text(
                image_analysis_results, 
                request.user_requirements
            )
            task.progress = 0.6
            
            # 步骤3: 生成二维码 (60-70%)
            task.message = "正在生成图片和视频的二维码..."
            
            qr_codes = await self._generate_qr_codes(request.image_files)
            task.progress = 0.7
            
            # 步骤4: 图文排版 (70-85%)
            task.message = "正在进行图文排版..."
            
            layout_result = await self._create_layout(
                biography_content,
                image_analysis_results,
                qr_codes
            )
            task.progress = 0.85
            
            # 步骤5: 生成PDF (85-100%)
            task.message = "正在生成PDF故事书..."
            
            pdf_path = await self._generate_pdf(layout_result)
            task.progress = 1.0
            
            # 完成任务
            task.status = TaskStatus.COMPLETED
            task.message = "个人传记生成完成！"
            task.result = {
                "pdf_path": pdf_path,
                "biography_content": biography_content,
                "image_analysis": image_analysis_results,
                "qr_codes": qr_codes
            }
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.message = f"处理失败: {str(e)}"
            self.logger.error(f"Biography processing failed for task {task_id}: {e}")
    
    async def _analyze_images(self, image_files: List[str]) -> List[Dict[str, Any]]:
        """分析图片内容"""
        results = []
        for image_file in image_files:
            analysis = await self.image_analyzer.analyze_image(image_file)
            results.append(analysis)
        return results
    
    async def _generate_biography_text(
        self, 
        image_analyses: List[Dict[str, Any]], 
        user_requirements: str
    ) -> str:
        """生成传记文本"""
        return await self.text_generator.generate_biography(
            image_analyses, 
            user_requirements
        )
    
    async def _generate_qr_codes(
        self, 
        media_files: List[str]
    ) -> Dict[str, str]:
        """为媒体文件生成二维码"""
        qr_codes = {}
        for media_file in media_files:
            # 生成可访问的URL（这里需要根据实际的文件存储方式调整）
            media_url = self.file_service.get_public_url(media_file)
            qr_code_path = await self.qr_generator.generate_qr_code(
                media_url, 
                f"qr_{media_file}"
            )
            qr_codes[media_file] = qr_code_path
        return qr_codes
    
    async def _create_layout(
        self,
        biography_content: str,
        image_analyses: List[Dict[str, Any]],
        qr_codes: Dict[str, str]
    ) -> Dict[str, Any]:
        """创建图文排版"""
        return await self.layout_engine.create_layout(
            biography_content,
            image_analyses,
            qr_codes
        )
    
    async def _generate_pdf(self, layout_result: Dict[str, Any]) -> str:
        """生成PDF文件"""
        return await self.pdf_generator.generate_pdf(layout_result)
    
    def get_task_status(self, task_id: str) -> Optional[ProcessingTask]:
        """获取任务状态"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self, user_id: str) -> List[ProcessingTask]:
        """获取用户的所有任务"""
        return [
            task for task in self.tasks.values() 
            if task.task_id.startswith(f"biography_{user_id}_")
        ] 