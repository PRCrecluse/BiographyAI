#!/usr/bin/env python3
"""
个人传记Agent - 统计仪表板服务器
集成Supabase数据库，展示用户统计信息
"""
import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import requests
import json
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, Any, List

# Supabase配置
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-supabase-anon-key-here"

# 创建FastAPI应用
app = FastAPI(title="个人传记Agent - 统计仪表板", version="1.0.0")

def get_supabase_headers():
    """获取Supabase API请求头"""
    return {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }

async def fetch_user_stats() -> Dict[str, Any]:
    """从Supabase获取用户统计信息"""
    try:
        # 获取总用户数
        profiles_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?select=*",
            headers=get_supabase_headers()
        )
        
        total_users = 0
        active_users = 0
        recent_users = 0
        
        if profiles_response.status_code == 200:
            profiles_data = profiles_response.json()
            total_users = len(profiles_data)
            
            # 计算活跃用户（最近30天有更新的用户）
            thirty_days_ago = datetime.now() - timedelta(days=30)
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            for profile in profiles_data:
                if profile.get('updated_at'):
                    try:
                        updated_at = datetime.fromisoformat(profile['updated_at'].replace('Z', '+00:00'))
                        if updated_at > thirty_days_ago:
                            active_users += 1
                        if updated_at > seven_days_ago:
                            recent_users += 1
                    except:
                        continue
        
        # 获取笔记统计
        notes_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/notes?select=*",
            headers=get_supabase_headers()
        )
        
        total_notes = 0
        if notes_response.status_code == 200:
            notes_data = notes_response.json()
            total_notes = len(notes_data)
        
        # 获取名片统计
        cards_response = requests.get(
            f"{SUPABASE_URL}/rest/v1/business_cards?select=*",
            headers=get_supabase_headers()
        )
        
        total_cards = 0
        if cards_response.status_code == 200:
            cards_data = cards_response.json()
            total_cards = len(cards_data)
        
        return {
            "total_users": total_users,
            "active_users_30d": active_users,
            "recent_users_7d": recent_users,
            "total_notes": total_notes,
            "total_business_cards": total_cards,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {
            "total_users": 0,
            "active_users_30d": 0,
            "recent_users_7d": 0,
            "total_notes": 0,
            "total_business_cards": 0,
            "error": str(e),
            "last_updated": datetime.now().isoformat()
        }

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """统计仪表板首页"""
    html_content = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>个人传记Agent - 统计仪表板</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            
            .header p {
                font-size: 1.1rem;
                opacity: 0.9;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .stat-card {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .stat-card:hover {
                transform: translateY(-5px);
            }
            
            .stat-number {
                font-size: 3rem;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 10px;
            }
            
            .stat-label {
                font-size: 1.1rem;
                color: #666;
                margin-bottom: 5px;
            }
            
            .stat-description {
                font-size: 0.9rem;
                color: #999;
            }
            
            .status-section {
                background: white;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            
            .status-title {
                font-size: 1.5rem;
                margin-bottom: 20px;
                color: #333;
            }
            
            .status-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 10px 0;
                border-bottom: 1px solid #eee;
            }
            
            .status-item:last-child {
                border-bottom: none;
            }
            
            .status-indicator {
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 10px;
            }
            
            .status-online {
                background-color: #4CAF50;
            }
            
            .status-offline {
                background-color: #f44336;
            }
            
            .refresh-btn {
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                transition: background 0.3s ease;
            }
            
            .refresh-btn:hover {
                background: #5a67d8;
            }
            
            .loading {
                opacity: 0.6;
            }
            
            .error {
                color: #f44336;
                background: #ffebee;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
            }
            
            .last-updated {
                text-align: center;
                color: white;
                opacity: 0.8;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 个人传记Agent</h1>
                <p>实时统计仪表板 - 用户活跃度与数据概览</p>
            </div>
            
            <div class="stats-grid" id="statsGrid">
                <div class="stat-card">
                    <div class="stat-number" id="totalUsers">-</div>
                    <div class="stat-label">注册用户总数</div>
                    <div class="stat-description">累计注册的用户数量</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number" id="activeUsers">-</div>
                    <div class="stat-label">活跃用户 (30天)</div>
                    <div class="stat-description">最近30天内有活动的用户</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number" id="recentUsers">-</div>
                    <div class="stat-label">近期用户 (7天)</div>
                    <div class="stat-description">最近7天内有活动的用户</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number" id="totalNotes">-</div>
                    <div class="stat-label">笔记总数</div>
                    <div class="stat-description">用户创建的笔记数量</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-number" id="totalCards">-</div>
                    <div class="stat-label">名片总数</div>
                    <div class="stat-description">用户创建的名片数量</div>
                </div>
            </div>
            
            <div class="status-section">
                <div class="status-title">🔧 系统状态</div>
                <div class="status-item">
                    <div style="display: flex; align-items: center;">
                        <div class="status-indicator status-online"></div>
                        <span>Agent服务器</span>
                    </div>
                    <span>运行中</span>
                </div>
                <div class="status-item">
                    <div style="display: flex; align-items: center;">
                        <div class="status-indicator" id="supabaseStatus"></div>
                        <span>Supabase数据库</span>
                    </div>
                    <span id="supabaseStatusText">检查中...</span>
                </div>
                <div class="status-item">
                    <div style="display: flex; align-items: center;">
                        <div class="status-indicator status-online"></div>
                        <span>API端点</span>
                    </div>
                    <span>正常</span>
                </div>
            </div>
            
            <div style="text-align: center;">
                <button class="refresh-btn" onclick="refreshStats()">🔄 刷新数据</button>
            </div>
            
            <div class="last-updated" id="lastUpdated">
                数据更新时间: 加载中...
            </div>
        </div>
        
        <script>
            // 获取统计数据
            async function fetchStats() {
                try {
                    document.getElementById('statsGrid').classList.add('loading');
                    
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    // 更新统计数字
                    document.getElementById('totalUsers').textContent = data.total_users || 0;
                    document.getElementById('activeUsers').textContent = data.active_users_30d || 0;
                    document.getElementById('recentUsers').textContent = data.recent_users_7d || 0;
                    document.getElementById('totalNotes').textContent = data.total_notes || 0;
                    document.getElementById('totalCards').textContent = data.total_business_cards || 0;
                    
                    // 更新Supabase状态
                    const supabaseStatus = document.getElementById('supabaseStatus');
                    const supabaseStatusText = document.getElementById('supabaseStatusText');
                    
                    if (data.error) {
                        supabaseStatus.className = 'status-indicator status-offline';
                        supabaseStatusText.textContent = '连接异常';
                        console.error('Supabase error:', data.error);
                    } else {
                        supabaseStatus.className = 'status-indicator status-online';
                        supabaseStatusText.textContent = '连接正常';
                    }
                    
                    // 更新时间
                    if (data.last_updated) {
                        const updateTime = new Date(data.last_updated).toLocaleString('zh-CN');
                        document.getElementById('lastUpdated').textContent = `数据更新时间: ${updateTime}`;
                    }
                    
                } catch (error) {
                    console.error('Error fetching stats:', error);
                    
                    // 显示错误状态
                    const supabaseStatus = document.getElementById('supabaseStatus');
                    const supabaseStatusText = document.getElementById('supabaseStatusText');
                    supabaseStatus.className = 'status-indicator status-offline';
                    supabaseStatusText.textContent = '连接失败';
                    
                } finally {
                    document.getElementById('statsGrid').classList.remove('loading');
                }
            }
            
            // 刷新统计数据
            function refreshStats() {
                fetchStats();
            }
            
            // 页面加载时获取数据
            window.addEventListener('load', fetchStats);
            
            // 每30秒自动刷新一次
            setInterval(fetchStats, 30000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/api/stats")
async def get_stats():
    """获取统计数据API"""
    stats = await fetch_user_stats()
    return JSONResponse(content=stats)

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "message": "个人传记Agent统计服务运行正常",
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test-supabase")
async def test_supabase():
    """测试Supabase连接"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/profiles?select=count",
            headers=get_supabase_headers()
        )
        
        return {
            "status": "success" if response.status_code == 200 else "error",
            "status_code": response.status_code,
            "response": response.text[:200] if response.text else "Empty response"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# 添加传记生成相关的API端点
tasks_storage = {}
uploaded_files_storage = {}  # 存储上传的文件信息

@app.post("/api/biography/create")
async def create_biography(
    user_requirements: str = Form(None),
    template_style: str = Form("classic"), 
    language: str = Form("en"),
    files: List[UploadFile] = File(default=[])
):
    """创建个人传记"""
    try:
        import uuid
        import os
        task_id = str(uuid.uuid4())
        
        # 处理可能的空值
        user_requirements = user_requirements or "请为我生成一份个人传记"
        template_style = template_style or "classic"
        
        print(f"📝 收到传记创建请求:")
        print(f"   用户需求: {user_requirements}")
        print(f"   模板风格: {template_style}")
        print(f"   语言: {language}")
        print(f"   文件数量: {len(files)}")
        
        # 保存上传的图片文件
        uploaded_files = []
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            
        for i, file in enumerate(files):
            if file.content_type and file.content_type.startswith('image/'):
                # 生成文件名
                file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
                file_name = f"{task_id}_{i}{file_extension}"
                file_path = os.path.join(upload_dir, file_name)
                
                # 保存文件
                content = await file.read()
                with open(file_path, "wb") as f:
                    f.write(content)
                
                uploaded_files.append({
                    "path": file_path,
                    "filename": file.filename or f"image_{i}",
                    "content_type": file.content_type
                })
                print(f"   保存图片: {file_path}")
        
        # 存储文件信息
        uploaded_files_storage[task_id] = uploaded_files
        
        # 模拟任务创建
        tasks_storage[task_id] = {
            "status": "submitted",
            "progress": 0.0,
            "message": "Task submitted successfully",
            "user_requirements": user_requirements,
            "template_style": template_style,
            "language": language,
            "file_count": len(uploaded_files),
            "uploaded_files": uploaded_files,
            "created_at": datetime.now().isoformat()
        }
        
        # 开始后台处理
        import asyncio
        asyncio.create_task(process_biography_task(task_id))
        
        return {
            "task_id": task_id,
            "status": "submitted",
            "message": "传记生成任务已提交"
        }
        
    except Exception as e:
        print(f"❌ 创建传记失败: {str(e)}")
        return {"error": f"创建传记失败: {str(e)}"}

@app.get("/api/biography/status/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in tasks_storage:
        return {"error": "任务未找到"}
    
    task = tasks_storage[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "message": task["message"],
        "pdf_url": task.get("pdf_url"),
        "error_message": task.get("error_message")
    }

@app.get("/api/biography/download/{task_id}")
async def download_biography(task_id: str):
    """下载生成的传记PDF"""
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_storage[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    # 生成绘本风格的人生故事书PDF
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportlabImage, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
        from io import BytesIO
        import os
        
        # 创建PDF内容
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=0.8*inch, rightMargin=0.8*inch, topMargin=0.8*inch, bottomMargin=0.8*inch)
        
        # 创建绘本风格的样式
        styles = getSampleStyleSheet()
        
        # 绘本标题样式
        storybook_title = ParagraphStyle(
            'StorybookTitle',
            parent=styles['Title'],
            fontSize=24,
            leading=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor='navy'
        )
        
        # 章节标题样式
        chapter_title = ParagraphStyle(
            'ChapterTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            textColor='darkblue'
        )
        
        # 故事文字样式
        story_text = ParagraphStyle(
            'StoryText',
            parent=styles['Normal'],
            fontSize=14,
            leading=20,
            spaceAfter=15,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20
        )
        
        # 图片说明样式
        image_caption = ParagraphStyle(
            'ImageCaption',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            textColor='gray',
            fontName='Helvetica-Oblique'
        )
        
        story = []
        
        # 添加故事书标题
        title = Paragraph("My Life Story", storybook_title)
        story.append(title)
        story.append(Spacer(1, 30))
        
        # 添加副标题
        subtitle = Paragraph("A Personal Journey in Pictures and Words", image_caption)
        story.append(subtitle)
        story.append(Spacer(1, 40))
        
        # 获取上传的图片和用户问答数据
        uploaded_files = uploaded_files_storage.get(task_id, [])
        image_files = [f for f in uploaded_files if f.get('content_type', '').startswith('image/')]
        
        # 从用户需求中提取生活片段
        user_requirements = task.get('user_requirements', '')
        life_segments = extract_life_segments(user_requirements)
        
        print(f"📖 创建绘本：{len(image_files)} 张图片，{len(life_segments)} 个生活片段")
        
        # 为每张图片创建一个章节
        for i, image_file in enumerate(image_files):
            if os.path.exists(image_file['path']):
                try:
                    # 章节标题
                    chapter_num = i + 1
                    chapter_title_text = f"Chapter {chapter_num}"
                    
                    # 如果有对应的生活片段，使用其时期作为章节标题
                    if i < len(life_segments):
                        segment = life_segments[i]
                        period = segment.get('time', f'Memory {chapter_num}')
                        chapter_title_text = f"Chapter {chapter_num}: {period}"
                    
                    # 添加章节标题
                    chapter_header = Paragraph(chapter_title_text, chapter_title)
                    story.append(chapter_header)
                    story.append(Spacer(1, 20))
                    
                    # 添加图片（占页面主要空间）
                    img = ReportlabImage(image_file['path'])
                    # 计算图片大小（绘本风格，图片较大）
                    max_width = 5.5 * inch  # 更大的图片
                    max_height = 4 * inch
                    
                    img_width, img_height = img.imageWidth, img.imageHeight
                    
                    # 保持比例缩放
                    width_ratio = max_width / img_width
                    height_ratio = max_height / img_height
                    ratio = min(width_ratio, height_ratio)
                    
                    img.drawWidth = img_width * ratio
                    img.drawHeight = img_height * ratio
                    
                    story.append(img)
                    story.append(Spacer(1, 15))
                    
                    # 添加图片说明
                    caption_text = f"Memory from: {image_file['filename']}"
                    caption = Paragraph(caption_text, image_caption)
                    story.append(caption)
                    story.append(Spacer(1, 20))
                    
                    # 添加这张图片对应的故事文字
                    if i < len(life_segments):
                        segment = life_segments[i]
                        story_content = generate_chapter_story(segment, chapter_num)
                    else:
                        story_content = generate_default_chapter_story(chapter_num, image_file['filename'])
                    
                    story_para = Paragraph(story_content, story_text)
                    story.append(story_para)
                    story.append(Spacer(1, 30))
                    
                    # 除了最后一章，每章后添加分页
                    if i < len(image_files) - 1:
                        story.append(PageBreak())
                    
                    print(f"✅ 成功创建第{chapter_num}章: {chapter_title_text}")
                    
                except Exception as e:
                    print(f"❌ 创建章节失败 {image_file['filename']}: {e}")
        
        # 如果没有图片，创建一个简单的文字页面
        if not image_files:
            story.append(Paragraph("Your story begins here...", story_text))
            story.append(Spacer(1, 20))
            story.append(Paragraph("Upload some photos to create your personal storybook!", story_text))
        
        # 构建PDF
        try:
            doc.build(story)
            print("✅ 绘本风格PDF构建成功")
        except Exception as e:
            print(f"❌ PDF构建失败: {e}")
            # 简化重试
            story = [
                Paragraph("My Life Story", storybook_title),
                Spacer(1, 20),
                Paragraph("Your personal storybook is being created...", story_text)
            ]
            doc.build(story)
        
        # 获取PDF数据
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # 返回PDF文件
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=biography_{task_id}.pdf"}
        )
        
    except ImportError:
        # 如果没有reportlab库，生成简单的文本PDF
        from fastapi.responses import PlainTextResponse
        simple_content = f"""Personal Biography

Based on your requirements: {task['user_requirements']}
Template style: {task['template_style']}
Language: {task['language']}

This is a simplified version for testing.
"""
        return Response(
            content=simple_content.encode('utf-8'),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=biography_{task_id}.pdf"}
        )

async def process_biography_task(task_id: str):
    """后台处理传记生成任务"""
    try:
        import asyncio
        task = tasks_storage[task_id]
        
        # 模拟处理步骤
        steps = [
            (0.2, "Analyzing user requirements..."),
            (0.4, "Processing biography content..."),
            (0.6, "Generating biography text..."),
            (0.8, "Creating PDF document..."),
            (1.0, "Biography generation completed!")
        ]
        
        for progress, message in steps:
            await asyncio.sleep(3)  # 模拟处理时间
            tasks_storage[task_id].update({
                "status": "processing",
                "progress": progress,
                "message": message
            })
        
        # 完成任务
        tasks_storage[task_id].update({
            "status": "completed",
            "progress": 1.0,
            "message": "Biography generation completed!",
            "pdf_url": f"/api/biography/download/{task_id}"
        })
        
    except Exception as e:
        tasks_storage[task_id].update({
            "status": "failed",
            "progress": 0.0,
            "message": f"生成失败: {str(e)}",
            "error_message": str(e)
        })

def generate_biography_content(task):
    """基于用户需求和上传的图片生成真正的传记内容"""
    user_requirements = task.get('user_requirements', '')
    template_style = task.get('template_style', 'classic')
    language = task.get('language', 'en')
    file_count = task.get('file_count', 0)
    
    # 根据语言生成基础传记内容
    if language == 'zh-CN':
        content = f"""这是一段关于我的个人传记。

根据您的要求：{user_requirements}

我的人生充满了许多珍贵的回忆和经历。每一张照片都记录着我生命中的重要时刻，从童年的天真烂漫到青春的激情澎湃，再到成年后的沉稳坚定。

在我的人生旅程中，我经历过许多挑战和机遇。每一次的成长都让我更加坚强，每一次的体验都让我更加明智。这些珍贵的记忆如同璀璨的星星，点亮了我前进的道路。

我相信每个人都有属于自己的故事，而我的故事就藏在这{file_count}张照片中。它们见证了我的成长，记录了我的足迹，承载了我的梦想。

愿这份传记能够成为我人生的美好回忆，也希望能够激励我继续勇敢地走向未来。"""
    elif language == 'fr':
        content = f"""Voici mon autobiographie personnelle.

Selon vos exigences : {user_requirements}

Ma vie est remplie de nombreux souvenirs précieux et d'expériences. Chaque photo capture un moment important de ma vie, de l'innocence de l'enfance à la passion de la jeunesse, jusqu'à la maturité stable de l'âge adulte.

Au cours de mon voyage dans la vie, j'ai traversé de nombreux défis et opportunités. Chaque croissance m'a rendu plus fort, chaque expérience m'a rendu plus sage. Ces souvenirs précieux sont comme des étoiles brillantes qui illuminent mon chemin.

Je crois que chacun a sa propre histoire, et mon histoire se cache dans ces {file_count} photos. Elles témoignent de ma croissance, enregistrent mes traces et portent mes rêves.

Puisse cette biographie devenir un beau souvenir de ma vie et m'inspirer à continuer courageusement vers l'avenir."""
    elif language == 'it':
        content = f"""Questa è la mia autobiografia personale.

Secondo le tue richieste: {user_requirements}

La mia vita è piena di molti ricordi preziosi ed esperienze. Ogni foto cattura un momento importante della mia vita, dall'innocenza dell'infanzia alla passione della gioventù, fino alla maturità stabile dell'età adulta.

Durante il mio viaggio nella vita, ho attraversato molte sfide e opportunità. Ogni crescita mi ha reso più forte, ogni esperienza mi ha reso più saggio. Questi ricordi preziosi sono come stelle brillanti che illuminano il mio cammino.

Credo che ognuno abbia la propria storia, e la mia storia si nasconde in queste {file_count} foto. Esse testimoniano la mia crescita, registrano le mie orme e portano i miei sogni.

Possa questa biografia diventare un bel ricordo della mia vita e ispirarmi a continuare coraggiosamente verso il futuro."""
    else:  # English
        content = f"""This is my personal biography.

Based on your requirements: {user_requirements}

My life is filled with many precious memories and experiences. Each photograph captures an important moment in my life, from the innocence of childhood to the passion of youth, to the steady maturity of adulthood.

Throughout my life's journey, I have faced many challenges and opportunities. Each growth has made me stronger, each experience has made me wiser. These precious memories are like brilliant stars that light up my path forward.

I believe that everyone has their own story, and my story is hidden within these {file_count} photographs. They witness my growth, record my footsteps, and carry my dreams.

May this biography become a beautiful memory of my life and inspire me to continue courageously toward the future.

Each image tells a part of my story - moments of joy, reflection, adventure, and discovery. Together, they form the tapestry of my life, a unique narrative that is mine alone.

As I look back on these captured moments, I am filled with gratitude for the journey that has brought me to where I am today. These photographs are not just images; they are windows into my soul, reflections of my growth, and promises of the adventures yet to come."""
    
    return content

def extract_life_segments(user_requirements):
    """从用户需求中提取生活片段信息"""
    import re
    
    segments = []
    
    # 查找生活片段模式
    segment_pattern = r'【生活片段\d+】\s*\n时期：([^\n]+)\s*\n经历：([^\n]+)'
    matches = re.findall(segment_pattern, user_requirements)
    
    for time_period, activity in matches:
        segments.append({
            'time': time_period.strip(),
            'activity': activity.strip()
        })
    
    print(f"📝 提取到 {len(segments)} 个生活片段")
    for i, segment in enumerate(segments):
        print(f"  片段{i+1}: {segment['time']} - {segment['activity']}")
    
    return segments

def generate_chapter_story(segment, chapter_num):
    """为每个章节生成绘本风格的故事内容"""
    time_period = segment['time']
    activity = segment['activity']
    
    # 根据活动内容生成富有情感的故事文字
    story_templates = {
        'hide and seek': f"In {time_period}, life was filled with simple joys and endless games. {activity.capitalize()} was more than just a game - it was a moment of pure happiness, laughter echoing through the air, and the thrill of discovery. These were the days when every corner held a new adventure, and every moment was a treasure waiting to be found.",
        
        'photography': f"During {time_period}, I discovered the art of capturing moments. {activity.capitalize()} became my way of seeing the world through a different lens. Each click of the camera was like freezing time, preserving memories that would tell stories for years to come. Through the viewfinder, ordinary moments transformed into extraordinary memories.",
        
        'hometown': f"In {time_period}, returning to my roots brought a sense of peace and belonging. {activity.capitalize()} reminded me of where I came from and the values that shaped me. There's something magical about familiar places - they hold our history, our growth, and the comfort of knowing we're always welcome home.",
        
        'mountain': f"The adventure in {time_period} took me to new heights, both literally and metaphorically. {activity.capitalize()} was a journey of self-discovery, where each step upward brought new perspectives. Mountains teach us about perseverance, about the beauty that awaits those who dare to climb higher.",
        
        'spring': f"In {time_period}, nature became my teacher and companion. {activity.capitalize()} connected me to the natural rhythms of life. The gentle sounds of water reminded me that life flows continuously, carving beautiful paths through time, just as we carve our own unique journeys."
    }
    
    # 选择合适的模板
    activity_lower = activity.lower()
    for keyword, template in story_templates.items():
        if keyword in activity_lower:
            return template
    
    # 默认模板
    return f"In {time_period}, this was a significant moment in my journey. {activity.capitalize()} represents a chapter of growth, learning, and discovery. Every experience shapes us, and this memory holds a special place in the story of who I am becoming. It reminds me that life is a collection of moments, each one contributing to the beautiful tapestry of our personal narrative."

def generate_default_chapter_story(chapter_num, filename):
    """为没有对应生活片段的图片生成默认绘本故事"""
    default_stories = [
        "This photograph captures a moment in time that speaks to the heart. Every image tells a story, and this one whispers of memories made, experiences lived, and the beautiful journey of life unfolding one moment at a time.",
        
        "Here lies a memory worth cherishing - a glimpse into a day that mattered, a moment that shaped the story. Sometimes the most profound experiences are captured not in words, but in the silent testimony of a single photograph.",
        
        "This image holds within it the essence of a lived experience. Like all great stories, it invites us to wonder, to imagine, and to appreciate the rich tapestry of moments that make up a life well-lived.",
        
        "In this frame, time stands still, preserving a fragment of a larger story. Each photograph is a chapter, each moment a verse in the poem of life that continues to be written with every passing day."
    ]
    
    # 循环使用默认故事
    story_index = (chapter_num - 1) % len(default_stories)
    return default_stories[story_index]

if __name__ == "__main__":
    print("🚀 启动个人传记Agent - 集成服务...")
    print("📊 本地访问地址: http://localhost:8000")
    print("📈 统计API: http://localhost:8000/api/stats")
    print("🔍 健康检查: http://localhost:8000/api/health")
    print("📝 传记生成: http://localhost:8000/api/biography/create")
    print("🧪 Supabase测试: http://localhost:8000/api/test-supabase")
    print("⏹️  按 Ctrl+C 停止服务")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 