"""
数据模型定义
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import datetime


class ProcessingStatus(Enum):
    PENDING = "pending"
    ANALYZING_IMAGES = "analyzing_images"
    GENERATING_TEXT = "generating_text"
    CREATING_LAYOUT = "creating_layout"
    GENERATING_QR = "generating_qr"
    CREATING_PDF = "creating_pdf"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class BiographyRequest:
    """个人传记生成请求"""
    user_id: str
    image_files: List[str]  # 图片文件路径列表
    user_requirements: str  # 用户特殊要求
    template_style: str = "classic"  # PDF模板样式
    language: str = "zh-CN"  # 生成语言
    created_at: datetime.datetime = datetime.datetime.now()


@dataclass
class BiographyResponse:
    """个人传记生成响应"""
    task_id: str
    status: ProcessingStatus
    progress: float  # 0.0 - 1.0
    message: str
    pdf_url: Optional[str] = None
    preview_content: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime.datetime = datetime.datetime.now()
    updated_at: datetime.datetime = datetime.datetime.now()


@dataclass
class ImageAnalysisResult:
    """图片分析结果"""
    file_path: str
    description: str  # 图片描述
    key_elements: List[str]  # 关键元素
    people: List[Dict[str, Any]]  # 人物信息
    objects: List[Dict[str, Any]]  # 物体信息
    scene: Dict[str, Any]  # 场景信息
    emotions: List[str]  # 情感标签
    timestamp: Optional[str] = None  # 图片时间戳
    location: Optional[str] = None  # 位置信息
    confidence: float = 0.0  # 分析置信度


@dataclass
class BiographySection:
    """传记章节"""
    title: str
    content: str
    images: List[str]  # 相关图片
    order: int
    style: str = "paragraph"  # paragraph, timeline, story


@dataclass
class LayoutElement:
    """排版元素"""
    element_type: str  # text, image, qr_code, divider
    content: Any
    position: Dict[str, float]  # x, y, width, height
    style: Dict[str, Any]  # 样式配置


@dataclass
class PDFTemplate:
    """PDF模板配置"""
    name: str
    page_size: str  # A4, A5, Letter
    margins: Dict[str, float]  # top, bottom, left, right
    fonts: Dict[str, str]  # title, body, caption
    colors: Dict[str, str]  # primary, secondary, text
    layout_config: Dict[str, Any]


@dataclass
class QRCodeConfig:
    """二维码配置"""
    size: int = 150
    border: int = 4
    fill_color: str = "black"
    back_color: str = "white"
    error_correction: str = "M"  # L, M, Q, H


@dataclass
class AIModelConfig:
    """AI模型配置"""
    provider: str  # openai, anthropic, alibaba, baidu
    model_name: str  # gpt-4, claude-3, qwen-max, ernie-bot
    api_key: str
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30


@dataclass
class UserPreferences:
    """用户偏好设置"""
    user_id: str
    default_language: str = "zh-CN"
    preferred_template: str = "classic"
    ai_model_preference: str = "gpt-4"
    notification_enabled: bool = True
    privacy_level: str = "private"  # private, friends, public 