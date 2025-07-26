"""
文本生成工具
使用AI服务生成高质量的个人传记内容
"""

from typing import List, Dict, Any
from ..services.ai_service import AIService
from ..core.models import ImageAnalysisResult, BiographySection


class TextGenerator:
    """文本生成工具"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def generate_biography(
        self, 
        image_analyses: List[ImageAnalysisResult],
        user_requirements: str
    ) -> str:
        """
        生成完整的个人传记
        
        Args:
            image_analyses: 图片分析结果列表
            user_requirements: 用户特殊要求
            
        Returns:
            str: 生成的传记内容
        """
        return await self.ai_service.generate_biography_content(
            image_analyses, 
            user_requirements
        )
    
    async def generate_structured_biography(
        self, 
        image_analyses: List[ImageAnalysisResult],
        user_requirements: str
    ) -> List[BiographySection]:
        """
        生成结构化的个人传记（分章节）
        
        Args:
            image_analyses: 图片分析结果列表
            user_requirements: 用户特殊要求
            
        Returns:
            List[BiographySection]: 传记章节列表
        """
        # 首先生成整体传记内容
        full_content = await self.generate_biography(image_analyses, user_requirements)
        
        # 然后将内容分解为章节
        sections = await self._split_into_sections(full_content, image_analyses)
        
        return sections
    
    async def _split_into_sections(
        self, 
        content: str, 
        image_analyses: List[ImageAnalysisResult]
    ) -> List[BiographySection]:
        """将完整内容分解为章节"""
        
        prompt = f"""
        请将以下个人传记内容分解为逻辑清晰的章节。
        
        传记内容：
        {content}
        
        请以JSON格式返回章节信息：
        {{
            "sections": [
                {{
                    "title": "章节标题",
                    "content": "章节内容",
                    "order": 1,
                    "style": "paragraph",
                    "related_images": ["图片1", "图片2"]
                }}
            ]
        }}
        
        要求：
        1. 每个章节都要有清晰的主题
        2. 内容要连贯，逻辑清晰  
        3. 为每个章节匹配相关的图片
        4. 章节顺序要合理
        """
        
        # 调用AI服务生成结构化内容
        result = await self.ai_service.current_provider.generate_text(prompt)
        
        # 解析结果并创建BiographySection对象
        try:
            import json
            data = json.loads(result)
            sections = []
            
            for section_data in data.get("sections", []):
                section = BiographySection(
                    title=section_data.get("title", ""),
                    content=section_data.get("content", ""),
                    images=section_data.get("related_images", []),
                    order=section_data.get("order", 0),
                    style=section_data.get("style", "paragraph")
                )
                sections.append(section)
            
            return sections
            
        except json.JSONDecodeError:
            # 如果解析失败，创建一个默认章节
            return [BiographySection(
                title="我的故事",
                content=content,
                images=[analysis.file_path for analysis in image_analyses],
                order=1
            )]
    
    async def generate_timeline_biography(
        self, 
        image_analyses: List[ImageAnalysisResult],
        user_requirements: str
    ) -> List[BiographySection]:
        """
        生成时间线式传记
        
        Args:
            image_analyses: 图片分析结果列表
            user_requirements: 用户特殊要求
            
        Returns:
            List[BiographySection]: 按时间顺序排列的传记章节
        """
        # 根据图片时间戳排序
        sorted_analyses = sorted(
            image_analyses, 
            key=lambda x: x.timestamp or "9999-12-31"
        )
        
        prompt = f"""
        请根据以下按时间顺序排列的图片分析结果，创建一个时间线式的个人传记。
        
        图片分析（按时间顺序）：
        {self._format_analyses_for_prompt(sorted_analyses)}
        
        用户要求：
        {user_requirements}
        
        请创建一个时间线式的传记，每个时间段为一个章节。
        以JSON格式返回：
        {{
            "timeline_sections": [
                {{
                    "period": "时间段描述",
                    "title": "章节标题", 
                    "content": "章节内容",
                    "images": ["相关图片路径"],
                    "key_events": ["关键事件1", "关键事件2"]
                }}
            ]
        }}
        """
        
        result = await self.ai_service.current_provider.generate_text(prompt)
        
        try:
            import json
            data = json.loads(result)
            sections = []
            
            for i, section_data in enumerate(data.get("timeline_sections", [])):
                section = BiographySection(
                    title=section_data.get("title", f"第{i+1}阶段"),
                    content=section_data.get("content", ""),
                    images=section_data.get("images", []),
                    order=i + 1,
                    style="timeline"
                )
                sections.append(section)
            
            return sections
            
        except json.JSONDecodeError:
            # 回退到标准传记生成
            return await self.generate_structured_biography(image_analyses, user_requirements)
    
    async def generate_story_style_biography(
        self, 
        image_analyses: List[ImageAnalysisResult],
        user_requirements: str
    ) -> str:
        """
        生成故事式传记
        
        Args:
            image_analyses: 图片分析结果列表
            user_requirements: 用户特殊要求
            
        Returns:
            str: 故事式传记内容
        """
        context = """
        你是一位专业的故事撰写人，擅长将真实的生活经历转化为引人入胜的故事。
        请根据图片分析结果，撰写一篇故事式的个人传记。
        
        要求：
        1. 使用第三人称或第一人称叙述
        2. 包含生动的细节描写
        3. 具有故事性的开头、发展、高潮、结尾
        4. 语言优美，富有感染力
        5. 每个重要情节都要与图片内容呼应
        """
        
        image_summary = self._format_analyses_for_prompt(image_analyses)
        
        prompt = f"""
        请根据以下图片分析结果，撰写一篇故事式的个人传记：
        
        图片分析结果：
        {image_summary}
        
        用户特殊要求：
        {user_requirements}
        
        请撰写一篇完整的故事式传记，要求生动感人，具有强烈的代入感。
        """
        
        return await self.ai_service.current_provider.generate_text(prompt, context)
    
    async def optimize_biography_content(self, content: str, style: str = "professional") -> str:
        """
        优化传记内容
        
        Args:
            content: 原始传记内容
            style: 优化风格（professional, literary, casual）
            
        Returns:
            str: 优化后的内容
        """
        return await self.ai_service.optimize_biography(content)
    
    async def generate_chapter_titles(self, content: str) -> List[str]:
        """
        为传记内容生成章节标题
        
        Args:
            content: 传记内容
            
        Returns:
            List[str]: 章节标题列表
        """
        prompt = f"""
        请为以下传记内容生成合适的章节标题。
        
        内容：
        {content}
        
        请以JSON格式返回标题列表：
        {{"titles": ["标题1", "标题2", "标题3"]}}
        
        要求：
        1. 标题要简洁有力
        2. 能够概括该部分的主要内容
        3. 具有吸引力和文学性
        4. 数量控制在3-8个之间
        """
        
        result = await self.ai_service.current_provider.generate_text(prompt)
        
        try:
            import json
            data = json.loads(result)
            return data.get("titles", [])
        except json.JSONDecodeError:
            return ["我的故事"]
    
    async def generate_introduction(self, image_analyses: List[ImageAnalysisResult]) -> str:
        """
        生成传记引言
        
        Args:
            image_analyses: 图片分析结果列表
            
        Returns:
            str: 引言内容
        """
        prompt = f"""
        请根据以下图片分析结果，为个人传记撰写一段引人入胜的引言。
        
        图片分析摘要：
        {self._format_analyses_for_prompt(image_analyses)}
        
        要求：
        1. 引言要简洁有力，能够吸引读者
        2. 概括传记的主要内容和主题
        3. 设置悬念，引导读者继续阅读
        4. 字数控制在100-200字之间
        """
        
        return await self.ai_service.current_provider.generate_text(prompt)
    
    async def generate_conclusion(self, biography_content: str) -> str:
        """
        生成传记结语
        
        Args:
            biography_content: 传记主要内容
            
        Returns:
            str: 结语内容
        """
        prompt = f"""
        请根据以下传记内容，撰写一段深刻的结语。
        
        传记内容摘要：
        {biography_content[:1000]}...
        
        要求：
        1. 总结传记的主要主题和意义
        2. 表达对未来的展望或感悟
        3. 语言要富有哲理性和感染力
        4. 字数控制在100-200字之间
        """
        
        return await self.ai_service.current_provider.generate_text(prompt)
    
    def _format_analyses_for_prompt(self, analyses: List[ImageAnalysisResult]) -> str:
        """格式化图片分析结果用于提示词"""
        formatted = ""
        for i, analysis in enumerate(analyses, 1):
            formatted += f"""
            图片{i}:
            - 描述: {analysis.description}
            - 关键元素: {', '.join(analysis.key_elements)}
            - 场景: {analysis.scene}
            - 情感: {', '.join(analysis.emotions)}
            - 时间: {analysis.timestamp or '未知'}
            
            """
        return formatted 