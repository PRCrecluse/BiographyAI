"""
Vercel Serverless 函数 - 传记创建
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import httpx
import aiofiles
import os
import uuid
import json
import base64
from datetime import datetime
from typing import List
import asyncio

app = FastAPI()

# AI 服务配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 任务存储 (使用外部存储或数据库在生产环境)
tasks = {}

class AIService:
    """轻量级 AI 服务"""
    
    def __init__(self):
        self.api_key = DOUBAO_API_KEY
        self.base_url = DOUBAO_BASE_URL
    
    async def analyze_image(self, image_base64: str, prompt: str) -> str:
        """分析图片内容"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": "doubao-vision-pro-32k-241028",
            "messages": [{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"AI API错误: {response.status_code}")
    
    async def generate_biography(self, image_analyses: List[str], user_requirements: str, language: str = "en") -> str:
        """生成传记内容"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 根据语言选择提示词
        prompts = {
            "zh-CN": f"""请根据以下图片分析和用户要求，撰写一篇个人传记：

用户要求：{user_requirements}

图片分析：
{chr(10).join([f"图片 {i+1}: {analysis}" for i, analysis in enumerate(image_analyses)])}

请用中文撰写一篇完整的个人传记，包含：
1. 引言
2. 早期生活 
3. 重要经历
4. 成就与贡献
5. 个人特质
6. 结语

要求：温馨感人，真实可信，约1000-1500字。""",
            
            "en": f"""Please write a personal biography based on the following image analyses and user requirements:

User Requirements: {user_requirements}

Image Analyses:
{chr(10).join([f"Image {i+1}: {analysis}" for i, analysis in enumerate(image_analyses)])}

Please write a complete personal biography in English, including:
1. Introduction
2. Early Life
3. Important Experiences  
4. Achievements & Contributions
5. Personal Qualities
6. Conclusion

Requirements: Warm and touching, authentic and credible, approximately 1000-1500 words.""",
            
            "it": f"""Per favore scrivi una biografia personale basata sulle seguenti analisi delle immagini e sui requisiti dell'utente:

Requisiti dell'utente: {user_requirements}

Analisi delle immagini:
{chr(10).join([f"Immagine {i+1}: {analysis}" for i, analysis in enumerate(image_analyses)])}

Per favore scrivi una biografia personale completa in italiano, includendo:
1. Introduzione
2. Vita Iniziale
3. Esperienze Importanti
4. Risultati e Contributi
5. Qualità Personali
6. Conclusione

Requisiti: Calorosa e toccante, autentica e credibile, circa 1000-1500 parole.""",
            
            "fr": f"""Veuillez écrire une biographie personnelle basée sur les analyses d'images suivantes et les exigences de l'utilisateur:

Exigences de l'utilisateur: {user_requirements}

Analyses d'images:
{chr(10).join([f"Image {i+1}: {analysis}" for i, analysis in enumerate(image_analyses)])}

Veuillez écrire une biographie personnelle complète en français, incluant:
1. Introduction
2. Première Vie
3. Expériences Importantes
4. Réalisations et Contributions
5. Qualités Personnelles
6. Conclusion

Exigences: Chaleureuse et touchante, authentique et crédible, environ 1000-1500 mots."""
        }
        
        prompt = prompts.get(language, prompts["en"])
        
        data = {
            "model": "doubao-seed-1-6-250615",
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }],
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception(f"传记生成失败: {response.status_code}")

ai_service = AIService()

async def process_biography_task(task_id: str, image_files: List[bytes], user_requirements: str, language: str):
    """异步处理传记生成任务"""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        
        # 分析图片
        image_analyses = []
        if image_files:
            for i, image_data in enumerate(image_files):
                tasks[task_id]["progress"] = 20 + (i * 30 // len(image_files))
                
                # 转换为base64
                image_base64 = base64.b64encode(image_data).decode()
                
                # 分析图片
                analysis = await ai_service.analyze_image(
                    image_base64, 
                    "请详细描述这张图片的内容，包括人物、场景、活动、情绪等细节，用于创建个人传记。"
                )
                image_analyses.append(analysis)
        
        tasks[task_id]["progress"] = 60
        
        # 生成传记
        biography_content = await ai_service.generate_biography(
            image_analyses, 
            user_requirements, 
            language
        )
        
        tasks[task_id]["progress"] = 90
        
        # 保存结果 (在生产环境中应该保存到永久存储)
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["result"] = {
            "content": biography_content,
            "image_count": len(image_files),
            "language": language,
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)

@app.post("/")
async def create_biography(
    user_requirements: str = Form(None),
    template_style: str = Form("classic"), 
    language: str = Form("en"),
    files: List[UploadFile] = File(default=[])
):
    """创建传记生成任务"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 读取上传的文件
        image_files = []
        for file in files:
            if file.filename:
                content = await file.read()
                image_files.append(content)
        
        # 初始化任务状态
        tasks[task_id] = {
            "status": "submitted",
            "progress": 0,
            "user_requirements": user_requirements,
            "template_style": template_style,
            "language": language,
            "image_count": len(image_files),
            "created_at": datetime.now().isoformat()
        }
        
        # 异步启动处理任务 (注意：在Vercel中可能需要外部队列)
        asyncio.create_task(process_biography_task(
            task_id, image_files, user_requirements, language
        ))
        
        return JSONResponse({
            "task_id": task_id,
            "status": "submitted",
            "message": "传记生成任务已提交，请稍后查询进度"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

# Vercel 函数入口
def handler(request):
    """Vercel 函数处理器"""
    return app(request) 