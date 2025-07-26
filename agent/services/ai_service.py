#!/usr/bin/env python3
"""
AI服务模块 - 支持豆包(Doubao)模型集成
提供图片理解、文本生成等功能，包含自动故障转移机制
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from dataclasses import dataclass
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIModelConfig:
    """AI模型配置"""
    name: str
    base_url: str
    api_key: str
    model_id: str
    max_tokens: int = 4000
    temperature: float = 0.7

class BaseAIProvider(ABC):
    """AI服务提供商基类"""
    
    def __init__(self, config: AIModelConfig):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        # 配置SSL设置，跳过证书验证（仅用于测试）
        connector = aiohttp.TCPConnector(ssl=False)
        self.session = aiohttp.ClientSession(connector=connector)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @abstractmethod
    async def analyze_image(self, image_url: str, prompt: str) -> str:
        """分析图片内容"""
        pass
    
    @abstractmethod
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """生成文本内容"""
        pass
    
    @abstractmethod
    async def optimize_text(self, text: str, style: str = "professional") -> str:
        """优化文本内容"""
        pass

class DoubaoProvider(BaseAIProvider):
    """豆包AI服务提供商"""
    
    def __init__(self, config: AIModelConfig, is_backup: bool = False):
        super().__init__(config)
        self.is_backup = is_backup
        self.provider_name = "豆包备用方案" if is_backup else "豆包主方案"
    
    async def _make_request(self, messages: List[Dict], model_override: str = None) -> str:
        """发送API请求"""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        data = {
            "model": model_override or self.config.model_id,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        try:
            logger.info(f"[{self.provider_name}] 发送请求到: {self.config.base_url}")
            logger.debug(f"[{self.provider_name}] 请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            async with self.session.post(
                f"{self.config.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=120)  # 增加超时时间
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.info(f"[{self.provider_name}] 请求成功")
                    return content
                else:
                    error_text = await response.text()
                    logger.error(f"[{self.provider_name}] API错误 {response.status}: {error_text}")
                    raise Exception(f"API请求失败: {response.status} - {error_text}")
                    
        except Exception as e:
            logger.error(f"[{self.provider_name}] 请求异常: {str(e)}")
            raise
    
    async def analyze_image(self, image_url: str, prompt: str) -> str:
        """分析图片内容"""
        # 根据是否为备用方案选择不同的模型
        model = "doubao-1-5-thinking-vision-pro-250428" if self.is_backup else "doubao-vision-pro-32k-241028"
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_url
                    }
                }
            ]
        }]
        
        return await self._make_request(messages, model)
    
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """生成文本内容"""
        # 根据是否为备用方案选择不同的模型
        model = "doubao-seed-1-6-thinking-250615" if self.is_backup else "doubao-seed-1-6-250615"
        
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": full_prompt
                }
            ]
        }]
        
        return await self._make_request(messages, model)
    
    async def optimize_text(self, text: str, style: str = "professional") -> str:
        """优化文本内容"""
        # 备用方案使用thinking模型进行文本优化
        model = "doubao-seed-1-6-thinking-250615" if self.is_backup else "doubao-seed-1-6-250615"
        
        style_prompts = {
            "professional": "请将以下文本优化为专业、正式的表达方式",
            "literary": "请将以下文本优化为文学性、富有感情色彩的表达方式", 
            "storytelling": "请将以下文本优化为生动、引人入胜的故事叙述方式",
            "warm": "请将以下文本优化为温馨、亲切的表达方式"
        }
        
        prompt = f"{style_prompts.get(style, style_prompts['professional'])}，保持原意不变，使表达更加优美流畅：\n\n{text}"
        
        messages = [{
            "role": "user", 
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        }]
        
        return await self._make_request(messages, model)

class AIService:
    """AI服务管理器 - 支持主备方案自动切换"""
    
    def __init__(self):
        # 主方案配置
        self.primary_config = AIModelConfig(
            name="豆包主方案",
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=os.getenv("DOUBAO_API_KEY", ""),
            model_id="doubao-vision-pro-32k-241028",
            max_tokens=4000,
            temperature=0.7
        )
        
        # 备用方案配置
        self.backup_config = AIModelConfig(
            name="豆包备用方案",
            base_url="https://ark.cn-beijing.volces.com/api/v3", 
            api_key=os.getenv("DOUBAO_API_KEY", ""),
            model_id="doubao-1-5-thinking-vision-pro-250428",
            max_tokens=4000,
            temperature=0.7
        )
        
        self.failure_count = 0
        self.max_failures = 3  # 最大失败次数，超过后切换到备用方案
        self.using_backup = False
    
    async def _execute_with_fallback(self, operation: str, *args, **kwargs):
        """执行操作，支持自动故障转移"""
        
        # 首先尝试主方案（除非已经切换到备用方案）
        if not self.using_backup:
            try:
                async with DoubaoProvider(self.primary_config, is_backup=False) as provider:
                    if operation == "analyze_image":
                        result = await provider.analyze_image(*args, **kwargs)
                    elif operation == "generate_text":
                        result = await provider.generate_text(*args, **kwargs)
                    elif operation == "optimize_text":
                        result = await provider.optimize_text(*args, **kwargs)
                    else:
                        raise ValueError(f"不支持的操作: {operation}")
                    
                    # 成功时重置失败计数
                    self.failure_count = 0
                    logger.info(f"✅ 主方案成功执行 {operation}")
                    return result
                    
            except Exception as e:
                self.failure_count += 1
                logger.warning(f"⚠️ 主方案失败 ({self.failure_count}/{self.max_failures}): {str(e)}")
                
                # 如果失败次数超过阈值，切换到备用方案
                if self.failure_count >= self.max_failures:
                    self.using_backup = True
                    logger.warning(f"🔄 切换到备用方案")
        
        # 使用备用方案
        try:
            async with DoubaoProvider(self.backup_config, is_backup=True) as provider:
                if operation == "analyze_image":
                    result = await provider.analyze_image(*args, **kwargs)
                elif operation == "generate_text":
                    result = await provider.generate_text(*args, **kwargs)
                elif operation == "optimize_text":
                    result = await provider.optimize_text(*args, **kwargs)
                else:
                    raise ValueError(f"不支持的操作: {operation}")
                
                logger.info(f"✅ 备用方案成功执行 {operation}")
                return result
                
        except Exception as e:
            logger.error(f"❌ 备用方案也失败了: {str(e)}")
            raise Exception(f"主备方案都失败了。主方案错误次数: {self.failure_count}, 备用方案错误: {str(e)}")
    
    async def analyze_image(self, image_url: str, prompt: str = "请详细描述这张图片的内容，包括人物、场景、活动、情绪等细节") -> str:
        """分析图片内容"""
        return await self._execute_with_fallback("analyze_image", image_url, prompt)
    
    async def generate_text(self, prompt: str, context: str = "") -> str:
        """生成文本内容（通用方法）"""
        return await self._execute_with_fallback("generate_text", prompt, context)
    
    async def generate_biography_text(self, image_analyses: List[str], user_requirements: str = "", style: str = "warm") -> str:
        """生成传记文本"""
        
        # 添加调试日志
        print(f"🤖 AI服务收到传记生成请求:")
        print(f"📊 用户需求长度: {len(user_requirements)} 字符")
        print(f"📝 用户需求内容预览: {user_requirements[:500]}...")
        
        # 检查是否包含用户真实信息
        if "生活片段" in user_requirements:
            print("✅ 发现用户真实信息片段")
        else:
            print("❌ 未发现用户真实信息片段")
            
        if "Early Years" in user_requirements or "School Days" in user_requirements:
            print("⚠️ 需求中包含通用章节，这不应该出现")
        
        # 超强化提示词 - 使用更严格的指令
        prompt = f"""
🚨 CRITICAL INSTRUCTION: You MUST strictly follow these rules. Violation of ANY rule means COMPLETE FAILURE 🚨

用户的真实信息：
{user_requirements if user_requirements else "请写一篇个人传记"}

图片参考信息：
{chr(10).join([f"{i+1}. {analysis}" for i, analysis in enumerate(image_analyses)])}

❌❌❌ ABSOLUTELY FORBIDDEN CONTENT (INSTANT FAILURE IF USED) ❌❌❌
- "Early Years" / "童年时光" / "早年时期" / "幼年时代"  
- "School Days" / "学生时代" / "求学时光" / "校园生活"
- "Family Time" / "家庭时光" / "家庭生活" / "家人陪伴"  
- "Growing Up" / "成长历程" / "青春岁月" / "成长时光"
- "Childhood" / "Youth" / "Education" / "Career"
- ANY fabricated childhood stories, school experiences, family descriptions
- ANY content not explicitly provided by the user

✅✅✅ MANDATORY REQUIREMENTS (ALL MUST BE FOLLOWED) ✅✅✅
1. 【ONLY USER'S REAL INFO】: Base EVERYTHING on user's provided information
2. 【PERSONALIZED TITLES】: Chapter titles MUST reflect user's specific periods (e.g., "2020年夏天的时光", "西藏之旅的回忆")  
3. 【NO FABRICATION】: Do NOT add any people, places, events not mentioned by user
4. 【USER-DRIVEN CHAPTERS】: Each chapter corresponds to ONE user-provided life segment
5. 【AUTHENTIC CONTENT】: If information is insufficient, write brief authentic content rather than fabricate

=== STRICT WRITING FRAMEWORK ===
- 开篇: Brief introduction based ONLY on user's provided info (max 1 paragraph)
- 主体章节: Each chapter = One user's real life segment with personalized title
- 结尾: Brief conclusion based ONLY on user's real experiences (max 1 paragraph)

=== CONTENT VALIDATION ===
Before generating, ask yourself:
- Does this contain ANY forbidden terms? → If YES, REWRITE
- Is every sentence based on user's real info? → If NO, REMOVE  
- Are chapter titles personalized? → If NO, CHANGE
- Am I fabricating anything? → If YES, STOP and use only real info

=== OUTPUT REQUIREMENTS ===
- 语言: 中文
- 字数: 800-1200字
- 语调: 温馨真实，基于用户真实经历
- 结构: 完全个性化，绝无通用模板

🔥 FINAL WARNING: If you generate "Early Years", "School Days" or any forbidden content, this is a COMPLETE FAILURE. 
SUCCESS = 100% personalized content based ONLY on user's real information.

现在请严格按照上述要求创作传记：
        """
        
        print(f"📏 最终提示词长度: {len(prompt)} 字符")
        
        result = await self._execute_with_fallback("generate_text", prompt)
        
        # 检查生成结果质量
        print(f"📖 生成结果长度: {len(result)} 字符")
        
        # 验证是否包含禁用词汇
        forbidden_terms = ["Early Years", "School Days", "Family Time", "Growing Up", 
                          "童年时光", "学生时代", "家庭时光", "成长历程"]
        found_forbidden = []
        for term in forbidden_terms:
            if term in result:
                found_forbidden.append(term)
        
        if found_forbidden:
            print(f"❌ AI仍然生成了禁用词汇: {found_forbidden}")
        else:
            print("✅ AI成功避免了所有禁用词汇")
            
        # 检查是否包含用户真实信息
        user_info_keywords = []
        if "2020" in result: user_info_keywords.append("2020")
        if "2022" in result: user_info_keywords.append("2022") 
        if "2024" in result: user_info_keywords.append("2024")
        if "西藏" in result or "Xizang" in result: user_info_keywords.append("西藏/Xizang")
        
        print(f"✅ 发现用户真实信息: {user_info_keywords}")
        
        return result
    
    async def optimize_text(self, text: str, style: str = "professional") -> str:
        """优化文本内容"""
        return await self._execute_with_fallback("optimize_text", text, style)
    
    def validate_generated_content(self, content: str, user_requirements: str) -> tuple[bool, list]:
        """验证生成内容是否符合要求"""
        issues = []
        
        # 检查禁用词汇
        forbidden_terms = ["Early Years", "School Days", "Family Time", "Growing Up", 
                          "童年时光", "学生时代", "家庭时光", "成长历程", "青春岁月",
                          "幼年时代", "校园生活", "家人陪伴", "成长时光"]
        
        for term in forbidden_terms:
            if term in content:
                issues.append(f"包含禁用词汇: {term}")
        
        # 检查用户信息融入
        if "生活片段" in user_requirements:
            # 提取用户提到的时期
            time_matches = re.findall(r'时期：([^\n]+)', user_requirements)
            found_periods = 0
            for time_period in time_matches:
                # 检查时期是否在内容中被提及
                if time_period in content or any(keyword in content for keyword in time_period.split()):
                    found_periods += 1
            
            if len(time_matches) > 0 and found_periods == 0:
                issues.append("未融入任何用户提供的时期信息")
            elif found_periods < len(time_matches) * 0.5:  # 至少融入50%的时期信息
                issues.append(f"用户信息融入不足: {found_periods}/{len(time_matches)}")
        
        return len(issues) == 0, issues
    
    async def generate_biography_with_validation(self, image_analyses: List[str], user_requirements: str = "", style: str = "warm", max_attempts: int = 3) -> str:
        """带验证的传记生成，如果内容不合格会自动重新生成"""
        original_requirements = user_requirements
        
        for attempt in range(max_attempts):
            print(f"🔄 第{attempt+1}次生成尝试...")
            
            try:
                content = await self.generate_biography_text(image_analyses, user_requirements, style)
                is_valid, issues = self.validate_generated_content(content, original_requirements)
                
                if is_valid:
                    print("✅ 生成内容通过验证")
                    return content
                else:
                    print(f"❌ 生成内容不合格: {issues}")
                    if attempt < max_attempts - 1:
                        print("🔄 准备重新生成...")
                        # 加强提示词，明确指出上次的问题
                        user_requirements = original_requirements + f"\n\n⚠️ 上次生成失败原因: {', '.join(issues)}\n请务必避免这些问题！绝对不要使用任何通用章节标题！"
                    else:
                        print(f"❌ 经过{max_attempts}次尝试仍无法生成合格内容")
                        # 即使不合格也返回最后一次的结果，避免完全失败
                        return content
                        
            except Exception as e:
                print(f"❌ 第{attempt+1}次生成出现异常: {str(e)}")
                if attempt == max_attempts - 1:
                    raise e
        
        raise Exception(f"经过{max_attempts}次尝试仍无法生成内容")
    
    async def generate_chapter_titles(self, biography_text: str) -> List[str]:
        """生成章节标题"""
        prompt = f"""
请为以下传记内容生成5-8个章节标题，要求：
1. 标题简洁有力，富有感情色彩
2. 体现人生的重要阶段和转折点
3. 每个标题不超过10个字
4. 按时间顺序排列

传记内容：
{biography_text}

请只返回章节标题列表，每行一个标题：
        """
        
        result = await self._execute_with_fallback("generate_text", prompt)
        # 解析章节标题
        titles = [line.strip() for line in result.split('\n') if line.strip() and not line.strip().startswith('章节标题')]
        return titles[:8]  # 最多8个章节
    
    def get_status(self) -> Dict[str, Any]:
        """获取AI服务状态"""
        return {
            "using_backup": self.using_backup,
            "failure_count": self.failure_count,
            "max_failures": self.max_failures,
            "primary_model": self.primary_config.model_id,
            "backup_model": self.backup_config.model_id,
            "current_provider": "豆包备用方案" if self.using_backup else "豆包主方案"
        }
    
    def reset_to_primary(self):
        """重置为主方案"""
        self.using_backup = False
        self.failure_count = 0
        logger.info("🔄 已重置为主方案")

# 全局AI服务实例
ai_service = AIService()

# 便捷函数
async def analyze_image(image_url: str, prompt: str = None) -> str:
    """分析图片（便捷函数）"""
    return await ai_service.analyze_image(image_url, prompt or "请详细描述这张图片的内容")

async def generate_biography(image_analyses: List[str], user_requirements: str = "", style: str = "warm") -> str:
    """生成传记（便捷函数）- 使用验证机制"""
    return await ai_service.generate_biography_with_validation(image_analyses, user_requirements, style)

async def optimize_text(text: str, style: str = "professional") -> str:
    """优化文本（便捷函数）"""
    return await ai_service.optimize_text(text, style)

if __name__ == "__main__":
    # 测试代码
    async def test_ai_service():
        print("🧪 测试AI服务...")
        
        # 测试图片分析
        test_image_url = "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
        
        try:
            result = await analyze_image(test_image_url, "这张图片主要讲了什么？")
            print(f"✅ 图片分析成功: {result[:100]}...")
        except Exception as e:
            print(f"❌ 图片分析失败: {e}")
        
        # 测试文本生成
        try:
            result = await generate_biography(
                ["一张温馨的家庭照片"], 
                "请写一篇关于家庭温暖的传记"
            )
            print(f"✅ 传记生成成功: {result[:100]}...")
        except Exception as e:
            print(f"❌ 传记生成失败: {e}")
        
        # 显示状态
        status = ai_service.get_status()
        print(f"📊 AI服务状态: {status}")
    
    # 运行测试
    asyncio.run(test_ai_service()) 