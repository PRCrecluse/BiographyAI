#!/usr/bin/env python3
"""
Agent服务启动脚本
简化版本，避免复杂的模块导入问题
"""

import os
import sys
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# API数据模型
class BiographyCreateRequest(BaseModel):
    user_requirements: str
    template_style: str = "classic"
    language: str = "zh-CN"

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None

# 创建FastAPI应用
app = FastAPI(
    title="个人传记撰写Agent API",
    description="基于AI的个人传记自动生成服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储任务状态
tasks_storage = {}

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "个人传记撰写Agent API",
        "version": "1.0.0", 
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "features": {
            "biography_generation": True,
            "ai_service": True,
            "pdf_generation": True
        },
        "timestamp": asyncio.get_event_loop().time()
    }

@app.post("/api/biography/create")
async def create_biography(
    user_requirements: str,
    template_style: str = "classic",
    language: str = "en",
    files: List[UploadFile] = File(...)
):
    """
    创建个人传记
    """
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        # 模拟任务创建
        tasks_storage[task_id] = {
            "status": "submitted",
            "progress": 0.0,
            "message": "Task submitted successfully",
            "user_requirements": user_requirements,
            "template_style": template_style,
            "language": language,
            "files": len(files)
        }
        
        # 开始后台处理
        asyncio.create_task(process_biography_task(task_id))
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "传记生成任务已提交"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建传记失败: {str(e)}")

@app.get("/api/biography/status/{task_id}")
async def get_task_status(task_id: str):
    """
    查询任务状态
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    task = tasks_storage[task_id]
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        pdf_url=task.get("pdf_url"),
        error_message=task.get("error_message")
    )

@app.get("/api/biography/download/{task_id}")
async def download_biography(task_id: str):
    """
    下载生成的传记PDF
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    task = tasks_storage[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")
    
    # 生成简单的PDF内容
    pdf_content = generate_simple_pdf(task)
    
    return JSONResponse({
        "success": True,
        "task_id": task_id,
        "content": pdf_content
    })

async def process_biography_task(task_id: str):
    """
    后台处理传记生成任务
    """
    try:
        task = tasks_storage[task_id]
        
        # 模拟处理步骤
        steps = [
            (0.2, "Analyzing uploaded images..."),
            (0.4, "Processing user requirements..."), 
            (0.6, "Generating biography content..."),
            (0.8, "Creating PDF document..."),
            (1.0, "Biography generation completed!")
        ]
        
        for progress, message in steps:
            await asyncio.sleep(2)  # 模拟处理时间
            tasks_storage[task_id].update({
                "status": "processing",
                "progress": progress,
                "message": message
            })
        
        # 完成任务
        tasks_storage[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "Biography generated successfully!",
            "pdf_url": f"/api/biography/download/{task_id}"
        })
        
    except Exception as e:
        tasks_storage[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"Generation failed: {str(e)}",
            "error_message": str(e)
        })

def generate_simple_pdf(task: Dict[str, Any]) -> str:
    """
    生成简单的PDF内容
    """
    return f"""
    Personal Biography
    
    Generated based on your requirements:
    {task['user_requirements']}
    
    Template Style: {task['template_style']}
    Language: {task['language']}
    Images uploaded: {task['files']}
    
    [This is a simplified version for testing. Full AI generation would be implemented here.]
    """

if __name__ == "__main__":
    print("🚀 启动Agent服务...")
            print("📍 服务地址: https://biography-ai004.vercel.app")
        print("📋 API文档: https://biography-ai004.vercel.app/docs")
        print("❤️ 健康检查: https://biography-ai004.vercel.app/api/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 