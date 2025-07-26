"""
Vercel Serverless 函数 - 传记创建 (独立版本)
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import uuid
import base64
from datetime import datetime
from typing import List, Dict, Any
import asyncio
import tempfile
import io
from PIL import Image
import json

app = FastAPI()

# AI 服务配置
DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 添加API密钥验证
def validate_api_configuration():
    """验证API配置"""
    if DOUBAO_API_KEY == "":
        return False, "DOUBAO_API_KEY 环境变量未正确配置"
    if not DOUBAO_API_KEY or len(DOUBAO_API_KEY) < 10:
        return False, "DOUBAO_API_KEY 无效或过短"
    return True, "API配置正常"

# 任务存储 (使用内存存储，减少IO)
tasks = {}

# 文件系统持久化存储
TASKS_FILE = "/tmp/biography_tasks.json"

def save_tasks():
    """将任务数据保存到文件"""
    try:
        # 将任务数据转换为可序列化的格式
        serializable_tasks = {}
        for task_id, task_data in tasks.items():
            serializable_task = {}
            for key, value in task_data.items():
                if isinstance(value, (str, int, float, bool, list, dict)) or value is None:
                    serializable_task[key] = value
                else:
                    # 跳过不可序列化的对象
                    continue
            serializable_tasks[task_id] = serializable_task
        
        # 保存到文件
        with open(TASKS_FILE, 'w') as f:
            json.dump(serializable_tasks, f)
        print(f"任务数据已保存到文件: {TASKS_FILE}, 共{len(serializable_tasks)}个任务")
        return True
    except Exception as e:
        print(f"保存任务数据失败: {str(e)}")
        return False

def load_tasks():
    """从文件加载任务数据"""
    global tasks
    try:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                loaded_tasks = json.load(f)
            tasks.update(loaded_tasks)
            print(f"从文件加载了{len(loaded_tasks)}个任务: {TASKS_FILE}")
            return True
        else:
            print(f"任务数据文件不存在: {TASKS_FILE}")
            return False
    except Exception as e:
        print(f"加载任务数据失败: {str(e)}")
        return False

# 尝试加载任务数据
load_tasks()

# 添加测试任务
tasks["test-id"] = {
    "status": "completed",
    "progress": 100,
    "message": "传记生成完成",
    "created_at": "2024-01-01T12:00:00",
    "image_count": 0,
    "language": "zh-CN",
    "result": {
        "content": "这是一个测试传记内容...",
    }
}
save_tasks()

# 内联图片处理函数
def process_image_for_ai_inline(image_bytes: bytes) -> str:
    """
    内联的图片处理函数，转换为base64
    """
    try:
        # 加载图片
        image = Image.open(io.BytesIO(image_bytes))
        
        # 转换为RGB格式
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 调整大小以减少数据量
        max_size = (1024, 1024)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 转换为base64
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_base64
        
    except Exception as e:
        print(f"图片处理失败: {e}")
        return ""

# 内联HTML生成函数
def generate_html_content(content: str, title: str = "个人传记") -> str:
    """
    内联的HTML生成函数
    """
    html_template = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #fafafa;
            color: #333;
        }}
        
        .container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .title {{
            text-align: center;
            color: #2c3e50;
            font-size: 2.5em;
            margin-bottom: 10px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 40px;
        }}
        
        .content {{
            text-align: justify;
            font-size: 1.1em;
        }}
        
        .paragraph {{
            margin-bottom: 20px;
            text-indent: 2em;
        }}
        
        .section-title {{
            font-size: 1.4em;
            font-weight: bold;
            color: #2c3e50;
            margin: 30px 0 15px 0;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #95a5a6;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="title">{title}</div>
        <div class="subtitle">生成时间：{datetime.now().strftime('%Y年%m月%d日')}</div>
        
        <div class="content">
            {format_content_to_html(content)}
        </div>
        
        <div class="footer">
            <p>本传记由AI智能生成，仅供参考</p>
        </div>
    </div>
</body>
</html>
    """
    return html_template.strip()

def format_content_to_html(content: str) -> str:
    """将纯文本内容格式化为HTML"""
    if not content:
        return "<p>暂无内容</p>"
    
    # 简单的段落分割
    paragraphs = content.split('\n\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # 检查是否为标题（简单检测）
        if (len(paragraph) < 50 and 
            any(keyword in paragraph for keyword in ['章', '节', '部分', '引言', '结语', '总结', '#'])):
            # 移除可能的标记符号
            clean_title = paragraph.lstrip('#').strip()
            formatted_paragraphs.append(f'<div class="section-title">{clean_title}</div>')
        else:
            # 普通段落
            formatted_paragraphs.append(f'<div class="paragraph">{paragraph}</div>')
    
    return '\n'.join(formatted_paragraphs)

class OptimizedAIService:
    """内存优化的AI服务"""
    
    def __init__(self):
        self.api_key = DOUBAO_API_KEY
        self.base_url = DOUBAO_BASE_URL
        self.timeout = 30.0  # 减少超时时间
        
        # 验证API配置
        is_valid, message = validate_api_configuration()
        if not is_valid:
            print(f"⚠️ API配置警告: {message}")
    
    async def analyze_image(self, image_base64: str, prompt: str) -> str:
        """分析图片内容 - 优化版本"""
        # 检查API密钥
        if self.api_key == "":
            return "API密钥未配置，请在Vercel Dashboard中设置DOUBAO_API_KEY环境变量"
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 使用更轻量的模型参数
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
            "max_tokens": 2000,  # 减少token数量
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "API密钥无效，请检查DOUBAO_API_KEY配置"
                elif response.status_code == 429:
                    return "API调用频率限制，请稍后重试"
                else:
                    error_details = ""
                    try:
                        error_data = response.json()
                        error_details = f": {error_data.get('error', {}).get('message', '')}"
                    except:
                        pass
                    return f"图片分析失败，HTTP {response.status_code}{error_details}"
        except httpx.TimeoutException:
            return "图片分析超时，请检查网络连接"
        except Exception as e:
            return f"图片分析出现错误: {str(e)[:100]}..."
    
    async def generate_biography(self, image_analyses: List[str], user_requirements: str, language: str = "zh-CN") -> str:
        """生成传记内容 - 优化版本"""
        # 检查API密钥
        if self.api_key == "":
            return "❌ API密钥未配置！\n\n请在Vercel Dashboard中设置DOUBAO_API_KEY环境变量。\n\n步骤：\n1. 访问 vercel.com\n2. 进入项目设置\n3. 添加环境变量 DOUBAO_API_KEY\n4. 重新部署项目"
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # 精简的提示词模板
        prompt_templates = {
            "zh-CN": f"""根据图片分析和用户要求撰写个人传记：

用户要求：{user_requirements}

图片信息：
{chr(10).join([f"图片{i+1}: {analysis[:200]}..." for i, analysis in enumerate(image_analyses)])}

请撰写一篇1000字左右的中文传记，包含：引言、成长经历、重要时刻、个人特质、总结。要求真实感人。""",
            
            "en": f"""Write a personal biography based on image analysis and user requirements:

Requirements: {user_requirements}

Image Analysis:
{chr(10).join([f"Image {i+1}: {analysis[:200]}..." for i, analysis in enumerate(image_analyses)])}

Write a 1000-word English biography including: introduction, growth, achievements, qualities, conclusion."""
        }
        
        prompt = prompt_templates.get(language, prompt_templates["zh-CN"])
        
        data = {
            "model": "doubao-seed-1-6-250615",
            "messages": [{
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }],
            "max_tokens": 3000,  # 适中的token数量
            "temperature": 0.7
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                elif response.status_code == 401:
                    return "❌ API密钥无效\n\n请检查DOUBAO_API_KEY环境变量是否正确配置。"
                elif response.status_code == 429:
                    return "❌ API调用频率限制\n\n请稍后重试，或检查API配额是否充足。"
                else:
                    error_details = ""
                    try:
                        error_data = response.json()
                        error_details = f": {error_data.get('error', {}).get('message', '')}"
                    except:
                        pass
                    return f"❌ 传记生成失败\n\nHTTP {response.status_code}{error_details}\n\n请检查API配置和网络连接。"
        except httpx.TimeoutException:
            return "❌ 传记生成超时\n\n请检查网络连接，或稍后重试。"
        except Exception as e:
            return f"❌ 传记生成出现错误\n\n{str(e)[:200]}..."

ai_service = OptimizedAIService()

async def process_biography_task_optimized(task_id: str, image_files: List[bytes], user_requirements: str, language: str):
    """内存优化的传记生成任务处理"""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 10
        save_tasks()  # 保存任务状态
        
        # 图片分析 - 使用内联处理
        image_analyses = []
        if image_files:
            for i, image_data in enumerate(image_files):
                try:
                    tasks[task_id]["progress"] = 20 + (i * 40 // len(image_files))
                    save_tasks()  # 保存任务进度
                    
                    # 使用内联图像处理器
                    image_base64 = process_image_for_ai_inline(image_data)
                    
                    if image_base64:
                        analysis = await ai_service.analyze_image(
                            image_base64,
                            "请简要描述这张图片的内容，包括人物、场景、活动等关键信息。"
                        )
                        image_analyses.append(analysis)
                    else:
                        image_analyses.append("图片处理失败")
                    
                except Exception as e:
                    image_analyses.append(f"图片{i+1}处理出错")
                    continue
        
        tasks[task_id]["progress"] = 70
        save_tasks()  # 保存任务进度
        
        # 生成传记内容
        if not image_analyses:
            image_analyses = ["用户未上传图片或图片处理失败"]
        
        biography_content = await ai_service.generate_biography(
            image_analyses, user_requirements, language
        )
        
        tasks[task_id]["progress"] = 90
        save_tasks()  # 保存任务进度
        
        # 生成HTML内容 - 使用内联函数
        html_content = generate_html_content(biography_content, "个人传记")
        
        # 更新任务状态
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["content"] = html_content
        tasks[task_id]["filename"] = f"biography_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        tasks[task_id]["completed_at"] = datetime.now().isoformat()
        save_tasks()  # 保存完成的任务
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)[:200]  # 限制错误信息长度
        save_tasks()  # 保存失败的任务

@app.post("/")
@app.post("/api/biography/create")
async def create_biography_optimized(
    user_requirements: str = Form(None),
    template_style: str = Form("classic"), 
    language: str = Form("zh-CN"),
    files: List[UploadFile] = File(default=[])
):
    """创建传记 - 内存优化版本"""
    try:
        # 生成任务ID
        task_id = str(uuid.uuid4())[:8]
        
        # 初始化任务状态
        tasks[task_id] = {
            "status": "submitted",
            "progress": 0,
            "created_at": datetime.now().isoformat(),
            "user_requirements": user_requirements or "请根据图片内容撰写个人传记",
            "language": language,
            "style": template_style
        }
        save_tasks()  # 保存新创建的任务
        
        # 处理上传的文件
        image_files = []
        if files:
            for file in files[:5]:  # 限制最多5张图片
                if file.content_type and file.content_type.startswith('image/'):
                    try:
                        content = await file.read()
                        # 限制文件大小（5MB）
                        if len(content) <= 5 * 1024 * 1024:
                            image_files.append(content)
                    except Exception:
                        continue
        
        # 启动后台任务
        asyncio.create_task(process_biography_task_optimized(
            task_id, image_files, user_requirements or "请根据图片内容撰写个人传记", language
        ))
        
        return JSONResponse({
            "task_id": task_id,
            "status": "submitted",
            "message": "传记生成任务已提交"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@app.get("/status/{task_id}")
async def get_task_status_optimized(task_id: str):
    """查询任务状态 - 优化版本"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    response = {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "created_at": task["created_at"]
    }
    
    if task["status"] == "completed":
        response["download_url"] = f"/download/{task_id}"
        response["completed_at"] = task.get("completed_at")
    elif task["status"] == "failed":
        response["error"] = task.get("error", "未知错误")
    
    return JSONResponse(response)

@app.get("/download/{task_id}")
async def download_biography_optimized(task_id: str):
    """下载传记 - 优化版本"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务未完成")
    
    content = task.get("content", "")
    filename = task.get("filename", f"biography_{task_id}.html")
    
    from fastapi.responses import Response
    return Response(
        content=content,
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/debug")
async def debug_configuration():
    """调试端点 - 检查API配置状态"""
    is_valid, message = validate_api_configuration()
    
    config_status = {
        "api_key_configured": DOUBAO_API_KEY != "",
        "api_key_length": len(DOUBAO_API_KEY) if DOUBAO_API_KEY else 0,
        "api_key_preview": f"{DOUBAO_API_KEY[:8]}..." if DOUBAO_API_KEY and len(DOUBAO_API_KEY) > 8 else "未设置",
        "base_url": DOUBAO_BASE_URL,
        "validation_status": message,
        "is_valid": is_valid,
        "timestamp": datetime.now().isoformat()
    }
    
    return JSONResponse(config_status)

# 对于Vercel Python Runtime，直接暴露 FastAPI `app` 对象即可，不需要额外的 handler 变量

# Vercel Serverless Handler
from http.server import BaseHTTPRequestHandler
import cgi

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """处理POST请求 - 传记创建"""
        try:
            print(f"📡 收到传记创建请求: {self.path}")
            print(f"📋 请求头: {dict(self.headers)}")
            
            # 检查Content-Type
            content_type = self.headers.get('Content-Type', '')
            print(f"📄 Content-Type: {content_type}")
            
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                print(f"📦 接收到 {len(post_data)} 字节数据")
            else:
                print("⚠️ 没有接收到POST数据")
                post_data = b''
            
            # 生成任务ID
            task_id = f"test-task-{uuid.uuid4().hex[:8]}"
            print(f"🆔 生成任务ID: {task_id}")
            
            # 解析multipart数据（改进版本）
            user_requirements = "默认传记需求"
            language = "zh-CN"
            template_style = "classic"
            image_count = 0
            
            if content_type.startswith('multipart/form-data'):
                try:
                    # 提取boundary
                    boundary = None
                    if 'boundary=' in content_type:
                        boundary = content_type.split('boundary=')[1].strip()
                        print(f"🔍 提取到boundary: {boundary}")
                    
                    if boundary:
                        # 使用boundary分割数据
                        boundary_bytes = f'--{boundary}'.encode('utf-8')
                        parts = post_data.split(boundary_bytes)
                        
                        for part in parts:
                            if not part.strip():
                                continue
                                
                            part_str = part.decode('utf-8', errors='ignore')
                            
                            # 解析表单字段
                            if 'name="user_requirements"' in part_str:
                                lines = part_str.split('\r\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == '' and i + 1 < len(lines):
                                        user_requirements = lines[i + 1].strip()
                                        break
                            
                            elif 'name="language"' in part_str:
                                lines = part_str.split('\r\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == '' and i + 1 < len(lines):
                                        language = lines[i + 1].strip()
                                        break
                            
                            elif 'name="template_style"' in part_str:
                                lines = part_str.split('\r\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == '' and i + 1 < len(lines):
                                        template_style = lines[i + 1].strip()
                                        break
                            
                            # 计算图片数量
                            elif 'Content-Type: image/' in part_str:
                                image_count += 1
                    
                    print(f"📸 检测到 {image_count} 张图片")
                    print(f"📝 用户需求: {user_requirements[:100]}...")
                    print(f"🌐 语言: {language}")
                    print(f"🎨 模板: {template_style}")
                    
                except Exception as parse_error:
                    print(f"⚠️ 解析multipart数据时出错: {parse_error}")
                    # 使用默认值继续处理，不抛出异常
                    image_count = 1  # 假设至少有一张图片
            
            # 创建任务
            tasks[task_id] = {
                "status": "submitted",
                "progress": 0,
                "message": "传记生成任务已提交，请使用task_id查询进度",
                "created_at": datetime.now().isoformat(),
                "image_count": max(1, image_count),
                "language": language,
                "template_style": template_style,
                "user_requirements": user_requirements
            }
            
            save_tasks()
            print(f"💾 任务已保存: {task_id}")
            
            # 构造响应数据（确保字段名匹配iOS期望）
            response_data = {
                "task_id": task_id,
                "status": "submitted", 
                "message": "传记生成任务已提交，请使用task_id查询进度"
            }
            
            # 发送成功响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            response_json = json.dumps(response_data, ensure_ascii=False)
            print(f"✅ 返回响应: {response_json}")
            self.wfile.write(response_json.encode('utf-8'))
            
        except Exception as e:
            print(f"❌ 处理POST请求时出错: {str(e)}")
            import traceback
            print(f"🔍 错误堆栈: {traceback.format_exc()}")
            
            # 发送错误响应
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"detail": f"创建传记任务失败: {str(e)}"}
            error_json = json.dumps(error_response, ensure_ascii=False)
            print(f"❌ 返回错误响应: {error_json}")
            self.wfile.write(error_json.encode('utf-8'))

    def do_GET(self):
        """处理GET请求 - 调试信息"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            is_valid, message = validate_api_configuration()
            
            response_data = {
                "api_configuration": {
                    "is_valid": is_valid,
                    "message": message,
                    "doubao_key_length": len(DOUBAO_API_KEY) if DOUBAO_API_KEY else 0
                },
                "task_storage": {
                    "total_tasks": len(tasks),
                    "task_ids": list(tasks.keys())
                },
                "environment": {
                    "python_version": "3.x",
                    "platform": "vercel"
                }
            }
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {"detail": f"获取调试信息失败: {str(e)}"}
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 