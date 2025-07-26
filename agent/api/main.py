"""
个人传记撰写Agent API服务
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yaml

from ..core.agent_orchestrator import AgentOrchestrator
from ..core.models import BiographyRequest, BiographyResponse, AIModelConfig
from ..services.ai_service import AIService
from ..services.file_service import FileService


# API数据模型
class BiographyCreateRequest(BaseModel):
    user_requirements: str
    template_style: str = "classic"
    language: str = "zh-CN"


class ModelConfigRequest(BaseModel):
    provider: str
    model_name: str
    api_key: str
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


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
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
ai_service = AIService()
file_service = FileService()
agent_orchestrator = AgentOrchestrator(ai_service, file_service)


# 依赖注入
def get_ai_service():
    return ai_service


def get_file_service():
    return file_service


def get_agent_orchestrator():
    return agent_orchestrator


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 加载配置文件
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ai_models.yaml")
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 自动配置默认的AI模型
        await setup_default_models(config_data)
    
    print("个人传记撰写Agent API服务已启动")


async def setup_default_models(config_data: Dict[str, Any]):
    """设置默认AI模型"""
    try:
        # 获取默认配置
        default_config = config_data.get("default", {})
        
        # 设置文本生成模型
        text_model_path = default_config.get("text_model", "openai.gpt4")
        if text_model_path:
            provider, model_name = text_model_path.split(".")
            model_config = config_data.get(provider, {}).get("models", {}).get(model_name)
            
            if model_config:
                # 替换环境变量
                api_key = os.getenv(model_config["api_key"].replace("${", "").replace("}", ""))
                if api_key:
                    ai_config = AIModelConfig(
                        provider=model_config["provider"],
                        model_name=model_config["model_name"],
                        api_key=api_key,
                        api_base=model_config.get("api_base"),
                        temperature=model_config.get("temperature", 0.7),
                        max_tokens=model_config.get("max_tokens", 2000),
                        timeout=model_config.get("timeout", 30)
                    )
                    ai_service.add_provider("default_text", ai_config)
        
        print("默认AI模型配置完成")
    except Exception as e:
        print(f"配置默认AI模型时出错: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "个人传记撰写Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/biography/create")
async def create_biography(
    request: BiographyCreateRequest,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    创建个人传记
    
    Args:
        request: 传记创建请求
        files: 上传的图片文件
        
    Returns:
        任务ID和状态信息
    """
    try:
        # 保存上传的文件
        file_paths = []
        for file in files:
            if file.content_type.startswith('image/'):
                file_path = await file_service.save_uploaded_file(file)
                file_paths.append(file_path)
        
        if not file_paths:
            raise HTTPException(status_code=400, detail="至少需要上传一张图片")
        
        # 创建传记请求
        biography_request = BiographyRequest(
            user_id="user_001",  # 实际应用中从认证获取
            image_files=file_paths,
            user_requirements=request.user_requirements,
            template_style=request.template_style,
            language=request.language
        )
        
        # 提交任务
        task_id = await orchestrator.create_biography(biography_request)
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "传记生成任务已提交，请使用task_id查询进度"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建传记失败: {str(e)}")


@app.get("/api/biography/status/{task_id}")
async def get_task_status(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    查询任务状态
    
    Args:
        task_id: 任务ID
        
    Returns:
        任务状态信息
    """
    try:
        task = orchestrator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        response = TaskStatusResponse(
            task_id=task.task_id,
            status=task.status.value,
            progress=task.progress,
            message=task.message,
            error_message=task.error
        )
        
        # 如果任务完成，添加PDF下载链接
        if task.status.value == "completed" and task.result:
            pdf_path = task.result.get("pdf_path")
            if pdf_path:
                response.pdf_url = f"/api/biography/download/{task_id}"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询任务状态失败: {str(e)}")


@app.get("/api/biography/download/{task_id}")
async def download_biography(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator)
):
    """
    下载生成的传记PDF
    
    Args:
        task_id: 任务ID
        
    Returns:
        PDF文件
    """
    try:
        task = orchestrator.get_task_status(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        if task.status.value != "completed":
            raise HTTPException(status_code=400, detail="任务尚未完成")
        
        if not task.result or not task.result.get("pdf_path"):
            raise HTTPException(status_code=404, detail="PDF文件不存在")
        
        pdf_path = task.result["pdf_path"]
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF文件不存在")
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"biography_{task_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载PDF失败: {str(e)}")


@app.post("/api/models/configure")
async def configure_ai_model(
    config: ModelConfigRequest,
    ai_svc: AIService = Depends(get_ai_service)
):
    """
    配置AI模型
    
    Args:
        config: 模型配置信息
        
    Returns:
        配置结果
    """
    try:
        ai_config = AIModelConfig(
            provider=config.provider,
            model_name=config.model_name,
            api_key=config.api_key,
            api_base=config.api_base,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        ai_svc.add_provider("user_configured", ai_config)
        ai_svc.switch_provider("user_configured")
        
        return {
            "message": "AI模型配置成功",
            "provider": config.provider,
            "model": config.model_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置AI模型失败: {str(e)}")


@app.get("/api/models/available")
async def get_available_models():
    """获取可用的AI模型列表"""
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ai_models.yaml")
    
    if not os.path.exists(config_path):
        return {"models": []}
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        models = []
        for provider, provider_data in config_data.items():
            if provider in ["default", "scenarios"]:
                continue
            
            provider_models = provider_data.get("models", {})
            for model_name, model_config in provider_models.items():
                models.append({
                    "provider": provider,
                    "model_name": model_name,
                    "display_name": f"{provider}.{model_name}",
                    "description": model_config.get("description", "")
                })
        
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "ai_service": len(ai_service.get_available_providers()) > 0,
        "current_model": ai_service.get_current_provider_info()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 