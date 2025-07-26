#!/usr/bin/env python3
"""
个人传记撰写Agent Web测试应用
支持多媒体上传、传记生成、PDF导出等功能
"""

import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys
import json
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import base64
import io
import mimetypes
import shutil

# 添加服务目录到Python路径
sys.path.append(str(Path(__file__).parent))

from services.ai_service import ai_service, analyze_image, generate_biography, optimize_text
from tools.pdf_generator import PDFGenerator

# PDF生成
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

app = FastAPI(title="个人传记撰写Agent测试平台", version="2.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建必要的目录
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("output")
STATIC_DIR = Path("static")
THUMBNAILS_DIR = Path("thumbnails")

for dir_path in [UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR, THUMBNAILS_DIR]:
    dir_path.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/thumbnails", StaticFiles(directory=THUMBNAILS_DIR), name="thumbnails")

# 初始化PDF生成器
pdf_generator = PDFGenerator()

# 全局变量存储任务状态
task_status = {}

class BiographyTask:
    """传记生成任务类"""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.status = "pending"
        self.progress = 0
        self.message = "等待开始"
        self.error = None
        self.result = None
        self.created_at = datetime.now()
        self.uploaded_files = []
        self.uploaded_files = []
        
    def update_status(self, status: str, progress: int, message: str, error: str = None):
        self.status = status
        self.progress = progress
        self.message = message
        self.error = error
        
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "result": self.result,
            "uploaded_files": self.uploaded_files
        }

async def save_uploaded_file(file: UploadFile) -> dict:
    """保存上传的文件并返回文件信息"""
    try:
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 获取文件信息
        file_info = {
            "original_name": file.filename,
            "saved_name": unique_filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "content_type": file.content_type,
            "is_image": file.content_type.startswith('image/') if file.content_type else False,
            "is_video": file.content_type.startswith('video/') if file.content_type else False,
            "url": f"/uploads/{unique_filename}"
        }
        
        # 如果是图片，生成缩略图
        if file_info["is_image"]:
            try:
                from PIL import Image as PILImage
                with PILImage.open(file_path) as img:
                    # 生成缩略图
                    img.thumbnail((200, 200))
                    thumbnail_path = THUMBNAILS_DIR / f"thumb_{unique_filename}"
                    img.save(thumbnail_path, "JPEG")
                    file_info["thumbnail_url"] = f"/thumbnails/thumb_{unique_filename}"
            except Exception as e:
                print(f"生成缩略图失败: {e}")
                file_info["thumbnail_url"] = file_info["url"]
        
        return file_info
        
    except Exception as e:
        raise Exception(f"保存文件失败: {str(e)}")

def generate_pdf_from_text(content: str, title: str, uploaded_files: List[dict]) -> str:
    """从文本内容生成PDF"""
    try:
        filename = f"biography_{uuid.uuid4()}.pdf"
        pdf_path = OUTPUT_DIR / filename
        
        doc = SimpleDocTemplate(str(pdf_path), pagesize=A4, 
                              leftMargin=72, rightMargin=72, 
                              topMargin=72, bottomMargin=72)
        story = []
        styles = getSampleStyleSheet()
        
        # 创建自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#2C3E50'),
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=20
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=40
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#2C3E50'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=18,
            leftIndent=20,
            rightIndent=20
        )
        
        # 添加封面
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"生成时间：{datetime.now().strftime('%Y年%m月%d日')}", subtitle_style))
        
        # 添加上传文件的预览（如果有图片）
        image_files = [f for f in uploaded_files if f.get('is_image', False)]
        if image_files:
            story.append(Paragraph("相关图片", subtitle_style))
            
            # 最多显示6张图片
            for i, img_file in enumerate(image_files[:6]):
                if i % 2 == 0:  # 每行两张图片
                    story.append(Spacer(1, 20))
                
                try:
                    img_path = img_file['file_path']
                    if os.path.exists(img_path):
                        from reportlab.platypus import Image as RLImage
                        # 调整图片大小
                        img = RLImage(img_path, width=2*inch, height=1.5*inch)
                        story.append(img)
                        story.append(Spacer(1, 10))
                except Exception as e:
                    print(f"添加图片到PDF失败: {e}")
        
        story.append(PageBreak())
        
        # 添加传记内容
        story.append(Paragraph("传记内容", title_style))
        story.append(Spacer(1, 20))
        
        # 分段添加内容
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
                story.append(Spacer(1, 10))
        
        # 添加文件信息页
        if uploaded_files:
            story.append(PageBreak())
            story.append(Paragraph("文件信息", title_style))
            story.append(Spacer(1, 20))
            
            for file_info in uploaded_files:
                file_text = f"""
                文件名：{file_info['original_name']}<br/>
                文件大小：{file_info['file_size'] / 1024:.1f} KB<br/>
                文件类型：{file_info['content_type']}<br/>
                """
                story.append(Paragraph(file_text, body_style))
                story.append(Spacer(1, 15))
        
        # 构建PDF
        doc.build(story)
        return str(pdf_path)
        
    except Exception as e:
        print(f"生成PDF失败: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def test_page():
    """增强的测试页面首页"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>个人传记撰写Agent - 增强测试平台</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; color: white; margin-bottom: 40px; }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; }
            .header p { font-size: 1.1rem; opacity: 0.9; }
            .section {
                background: white; border-radius: 15px; padding: 30px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 30px;
            }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #2c3e50; }
            .form-group input, .form-group textarea, .form-group select {
                width: 100%; padding: 12px; border: 2px solid #e1e5e9;
                border-radius: 8px; font-size: 1rem; transition: border-color 0.3s;
            }
            .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
                outline: none; border-color: #667eea;
            }
            .file-upload-area {
                border: 2px dashed #667eea; border-radius: 12px; padding: 40px;
                text-align: center; transition: all 0.3s; cursor: pointer;
            }
            .file-upload-area:hover { background: #f8f9ff; }
            .file-upload-area.dragover { border-color: #5a67d8; background: #f0f4ff; }
            .file-previews {
                display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px; margin-top: 20px;
            }
            .file-preview {
                position: relative; border: 1px solid #e1e5e9; border-radius: 8px;
                overflow: hidden; text-align: center; padding: 10px;
            }
            .file-preview img { width: 100%; height: 100px; object-fit: cover; border-radius: 4px; }
            .file-preview .file-info { 
                font-size: 0.8rem; color: #666; margin-top: 5px; 
                word-break: break-all;
            }
            .file-preview .remove-btn {
                position: absolute; top: 5px; right: 5px; background: #e74c3c;
                color: white; border: none; border-radius: 50%; width: 20px; height: 20px;
                cursor: pointer; font-size: 12px;
            }
            .btn {
                background: #667eea; color: white; border: none;
                padding: 12px 24px; border-radius: 8px; cursor: pointer;
                font-size: 1rem; font-weight: 600; width: 100%;
                transition: background 0.3s;
            }
            .btn:hover { background: #5a67d8; }
            .btn:disabled { background: #ccc; cursor: not-allowed; }
            .btn-secondary {
                background: #95a5a6; margin-left: 10px; width: auto;
            }
            .btn-secondary:hover { background: #7f8c8d; }
            .progress-bar {
                width: 100%; height: 25px; background: #e1e5e9;
                border-radius: 12px; overflow: hidden; margin: 15px 0;
            }
            .progress-fill {
                height: 100%; background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s ease; width: 0%; display: flex;
                align-items: center; justify-content: center; color: white; font-weight: 600;
            }
            .result-area {
                background: #f8f9fa; border-left: 4px solid #667eea;
                padding: 20px; margin: 20px 0; border-radius: 8px;
                max-height: 400px; overflow-y: auto;
            }
            .error { background: #ffebee; color: #c62828; padding: 15px; border-radius: 8px; }
            .success { background: #e8f5e8; color: #2e7d32; padding: 15px; border-radius: 8px; }
            .download-buttons { display: flex; gap: 10px; margin-top: 20px; }
            .stats { display: flex; justify-content: space-between; margin: 15px 0; }
            .stat-item { text-align: center; }
            .stat-number { font-size: 1.5rem; font-weight: bold; color: #667eea; }
            .stat-label { font-size: 0.9rem; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 个人传记撰写Agent</h1>
                <p>多媒体支持 • PDF生成 • 智能分析 • 专业排版</p>
            </div>
            
            <div class="section">
                <h2>📤 上传多媒体文件</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>上传图片和视频文件:</label>
                        <div class="file-upload-area" id="fileUploadArea">
                            <input type="file" id="files" name="files" multiple 
                                   accept="image/*,video/*" style="display: none;">
                            <div class="upload-text">
                                <h3>📁 拖拽文件到这里或点击选择</h3>
                                <p>支持图片 (JPG, PNG, GIF) 和视频 (MP4, MOV, AVI) 文件</p>
                                <p>最大文件大小: 50MB</p>
                            </div>
                        </div>
                        <div class="file-previews" id="filePreviews"></div>
                    </div>
                    
                    <div class="form-group">
                        <label for="requirements">传记生成要求:</label>
                        <textarea id="requirements" name="requirements" rows="5" 
                            placeholder="详细描述您希望的传记风格、重点内容和特殊要求...">请为我创作一篇温馨感人的个人传记，重点关注：
1. 人生中的重要时刻和转折点
2. 家庭关系和人际交往  
3. 个人成长和心路历程
4. 从上传的图片和视频中提取故事元素

希望传记风格温馨亲切，富有情感色彩，字数在1000-2000字之间。</textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">传记风格:</label>
                        <select id="style" name="style">
                            <option value="warm">温馨亲切 - 注重情感表达和人际关系</option>
                            <option value="professional">专业正式 - 突出成就和职业发展</option>
                            <option value="literary">文学优美 - 诗意表达和深度思考</option>
                            <option value="humorous">幽默风趣 - 轻松愉快的叙述风格</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn" id="generateBtn">🚀 开始智能分析与生成</button>
                </form>
            </div>
            
            <div class="section" id="progressSection" style="display: none;">
                <h2>⏳ 处理进度</h2>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill">0%</div>
                </div>
                <div id="statusMessage">等待开始...</div>
                <div class="stats" id="processingStats" style="display: none;">
                    <div class="stat-item">
                        <div class="stat-number" id="fileCount">0</div>
                        <div class="stat-label">上传文件</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="imageCount">0</div>
                        <div class="stat-label">图片</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number" id="videoCount">0</div>
                        <div class="stat-label">视频</div>
                    </div>
                </div>
            </div>
            
            <div class="section" id="resultSection" style="display: none;">
                <h2>📖 生成结果</h2>
                <div id="resultContent"></div>
                <div class="download-buttons" id="downloadButtons" style="display: none;">
                    <button class="btn" id="downloadTxtBtn">📄 下载文本版</button>
                    <button class="btn" id="downloadPdfBtn">📑 下载PDF版</button>
                    <button class="btn btn-secondary" id="viewOnlineBtn">👁️ 在线预览</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentTaskId = null;
            let uploadedFiles = [];
            
            // 文件上传区域事件处理
            const fileUploadArea = document.getElementById('fileUploadArea');
            const fileInput = document.getElementById('files');
            const filePreviews = document.getElementById('filePreviews');
            
            fileUploadArea.addEventListener('click', () => fileInput.click());
            fileUploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                fileUploadArea.classList.add('dragover');
            });
            fileUploadArea.addEventListener('dragleave', () => {
                fileUploadArea.classList.remove('dragover');
            });
            fileUploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                fileUploadArea.classList.remove('dragover');
                handleFiles(e.dataTransfer.files);
            });
            
            fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
            
            function handleFiles(files) {
                for (let file of files) {
                    if (file.size > 50 * 1024 * 1024) {
                        alert(`文件 ${file.name} 超过50MB限制`);
                        continue;
                    }
                    
                    if (!file.type.startsWith('image/') && !file.type.startsWith('video/')) {
                        alert(`文件 ${file.name} 不是支持的图片或视频格式`);
                        continue;
                    }
                    
                    uploadedFiles.push(file);
                    displayFilePreview(file);
                }
                updateFileStats();
            }
            
            function displayFilePreview(file) {
                const preview = document.createElement('div');
                preview.className = 'file-preview';
                
                const isImage = file.type.startsWith('image/');
                const isVideo = file.type.startsWith('video/');
                
                if (isImage) {
                    const img = document.createElement('img');
                    img.src = URL.createObjectURL(file);
                    preview.appendChild(img);
                } else if (isVideo) {
                    const video = document.createElement('video');
                    video.src = URL.createObjectURL(file);
                    video.style.width = '100%';
                    video.style.height = '100px';
                    video.style.objectFit = 'cover';
                    video.muted = true;
                    preview.appendChild(video);
                }
                
                const fileInfo = document.createElement('div');
                fileInfo.className = 'file-info';
                fileInfo.textContent = `${file.name} (${(file.size / 1024).toFixed(1)}KB)`;
                preview.appendChild(fileInfo);
                
                const removeBtn = document.createElement('button');
                removeBtn.className = 'remove-btn';
                removeBtn.textContent = '×';
                removeBtn.onclick = () => {
                    const index = uploadedFiles.indexOf(file);
                    if (index > -1) {
                        uploadedFiles.splice(index, 1);
                        preview.remove();
                        updateFileStats();
                    }
                };
                preview.appendChild(removeBtn);
                
                filePreviews.appendChild(preview);
            }
            
            function updateFileStats() {
                const imageCount = uploadedFiles.filter(f => f.type.startsWith('image/')).length;
                const videoCount = uploadedFiles.filter(f => f.type.startsWith('video/')).length;
                
                document.getElementById('fileCount').textContent = uploadedFiles.length;
                document.getElementById('imageCount').textContent = imageCount;
                document.getElementById('videoCount').textContent = videoCount;
            }
            
            // 表单提交处理
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                if (uploadedFiles.length === 0) {
                    alert('请至少上传一个文件');
                    return;
                }
                
                const formData = new FormData();
                const requirements = document.getElementById('requirements').value;
                const style = document.getElementById('style').value;
                
                for (let file of uploadedFiles) {
                    formData.append('files', file);
                }
                formData.append('requirements', requirements);
                formData.append('style', style);
                
                try {
                    const btn = document.getElementById('generateBtn');
                    btn.disabled = true;
                    btn.textContent = '⏳ 处理中...';
                    
                    document.getElementById('progressSection').style.display = 'block';
                    document.getElementById('processingStats').style.display = 'flex';
                    document.getElementById('resultSection').style.display = 'none';
                    
                    const response = await fetch('/api/generate-biography-enhanced', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (result.task_id) {
                        currentTaskId = result.task_id;
                        startPolling();
                    } else {
                        throw new Error(result.error || '生成失败');
                    }
                } catch (error) {
                    showError('生成失败: ' + error.message);
                    resetForm();
                }
            });
            
            function startPolling() {
                const interval = setInterval(async () => {
                    try {
                        const response = await fetch(`/api/task-status/${currentTaskId}`);
                        const status = await response.json();
                        
                        updateProgress(status.progress, status.message);
                        
                        if (status.status === 'completed') {
                            clearInterval(interval);
                            showResult(status.result);
                            resetForm();
                        } else if (status.status === 'failed') {
                            clearInterval(interval);
                            showError(status.error || '处理失败');
                            resetForm();
                        }
                    } catch (error) {
                        console.error('Polling error:', error);
                    }
                }, 2000);
            }
            
            function updateProgress(progress, message) {
                const progressFill = document.getElementById('progressFill');
                progressFill.style.width = progress + '%';
                progressFill.textContent = progress + '%';
                document.getElementById('statusMessage').textContent = message;
            }
            
            function showResult(result) {
                const resultContent = document.getElementById('resultContent');
                resultContent.innerHTML = `
                    <div class="success">🎉 传记生成成功！</div>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-number">${result.word_count}</div>
                            <div class="stat-label">字数</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${result.file_count}</div>
                            <div class="stat-label">处理文件</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-number">${result.has_pdf ? '✓' : '✗'}</div>
                            <div class="stat-label">PDF生成</div>
                        </div>
                    </div>
                    <div class="result-area">
                        <h3>传记内容预览</h3>
                        <p>${result.biography.substring(0, 500)}${result.biography.length > 500 ? '...' : ''}</p>
                    </div>
                `;
                
                document.getElementById('resultSection').style.display = 'block';
                document.getElementById('downloadButtons').style.display = 'flex';
                
                // 设置下载按钮
                document.getElementById('downloadTxtBtn').onclick = () => downloadFile(currentTaskId, 'txt');
                document.getElementById('downloadPdfBtn').onclick = () => downloadFile(currentTaskId, 'pdf');
                document.getElementById('viewOnlineBtn').onclick = () => viewOnline(currentTaskId);
            }
            
            function showError(message) {
                const resultContent = document.getElementById('resultContent');
                resultContent.innerHTML = `<div class="error">❌ ${message}</div>`;
                document.getElementById('resultSection').style.display = 'block';
            }
            
            function resetForm() {
                const btn = document.getElementById('generateBtn');
                btn.disabled = false;
                btn.textContent = '🚀 开始智能分析与生成';
            }
            
            function downloadFile(taskId, format) {
                window.open(`/api/download-${format}/${taskId}`, '_blank');
            }
            
            function viewOnline(taskId) {
                window.open(`/api/view-result/${taskId}`, '_blank');
            }
        </script>
    </body>
    </html>
    """)

@app.post("/api/generate-biography-enhanced")
async def generate_biography_enhanced(
    files: List[UploadFile] = File(...),
    requirements: str = Form(""),
    style: str = Form("warm")
):
    """增强的传记生成API"""
    task_id = str(uuid.uuid4())
    task = BiographyTask(task_id)
    task_status[task_id] = task
    
    # 异步处理任务
    asyncio.create_task(process_enhanced_biography_task(task, files, requirements, style))
    
    return {"task_id": task_id, "status": "started"}

async def process_enhanced_biography_task(task: BiographyTask, files: List[UploadFile], requirements: str, style: str):
    """处理增强传记生成任务"""
    try:
        task.update_status("processing", 10, "保存上传文件...")
        
        # 保存所有上传的文件
        uploaded_files = []
        for file in files:
            try:
                file_info = await save_uploaded_file(file)
                uploaded_files.append(file_info)
                task.uploaded_files.append(file_info)
            except Exception as e:
                print(f"保存文件失败: {e}")
                continue
        
        if not uploaded_files:
            raise Exception("没有成功保存任何文件")
        
        task.update_status("processing", 30, f"分析 {len(uploaded_files)} 个文件...")
        
        # 分析文件内容（优先处理图片）
        analysis_results = []
        image_files = [f for f in uploaded_files if f.get('is_image', False)]
        
        for i, img_file in enumerate(image_files[:5]):  # 最多分析5张图片
            try:
                task.update_status("processing", 30 + (i * 10), f"分析图片 {i+1}...")
                
                # 构建分析提示词
        prompt = f"""
                请从个人传记撰写的角度详细分析这张图片。
                
                用户要求：{requirements}
                传记风格：{style}
                
                请提取图片中的关键信息，包括：
                1. 场景和环境描述
                2. 人物和情感表达
                3. 时间和生活阶段推断
                4. 可能的故事背景和意义
                
                请用简洁但富有情感的语言描述。
                """
                
                # 使用文件路径分析图片
                result = await analyze_image(img_file['file_path'], prompt)
                analysis_results.append({
                    'file': img_file,
                    'analysis': result
                })
                
            except Exception as e:
                print(f"分析图片失败: {e}")
                continue
        
        task.update_status("processing", 70, "整合分析结果，生成传记...")
        
        # 整合分析结果生成传记
        combined_analysis = "\n\n".join([r['analysis'] for r in analysis_results])
        
        # 生成传记的提示词
        biography_prompt = f"""
        基于以下图片分析结果，请撰写一篇完整的个人传记：
        
        {combined_analysis}
        
        用户要求：{requirements}
        
        请创作一篇{style}风格的个人传记，要求：
        1. 字数在1000-2000字之间
        2. 结构完整，有开头、发展和结尾
        3. 融入图片中的具体场景和情感
        4. 体现个人成长和人生感悟
        5. 语言生动，富有画面感
        
        请直接输出传记内容，不需要额外说明。
        """
        
        # 生成传记
        biography_text = await generate_biography(biography_prompt)
        
        task.update_status("processing", 90, "生成PDF文件...")
        
        # 生成PDF
        pdf_path = None
        try:
            pdf_path = generate_pdf_from_text(
                content=biography_text,
                title="我的个人传记",
                uploaded_files=uploaded_files
            )
        except Exception as e:
            print(f"生成PDF失败: {e}")
        
        # 保存文本文件
        txt_path = OUTPUT_DIR / f"biography_{task.task_id}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"个人传记\n\n{biography_text}\n\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n")
            f.write(f"处理文件数：{len(uploaded_files)}\n")
            f.write(f"图片数量：{len(image_files)}\n")
        
        # 完成任务
        result = {
            "biography": biography_text,
            "txt_path": str(txt_path),
            "pdf_path": pdf_path,
            "word_count": len(biography_text),
            "file_count": len(uploaded_files),
            "image_count": len(image_files),
            "has_pdf": pdf_path is not None,
            "analysis_results": analysis_results
        }
        
        task.result = result
        task.update_status("completed", 100, "传记生成完成！")
        
    except Exception as e:
        error_msg = str(e)
        print(f"Enhanced task failed: {error_msg}")
        task.update_status("failed", 0, "处理失败", error_msg)

@app.get("/api/download-txt/{task_id}")
async def download_txt(task_id: str):
    """下载文本文件"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_status[task_id]
    if task.status != "completed" or not task.result:
        raise HTTPException(status_code=400, detail="任务未完成")
    
    txt_path = task.result.get("txt_path")
    if not txt_path or not os.path.exists(txt_path):
        raise HTTPException(status_code=404, detail="文本文件不存在")
    
    return FileResponse(
        txt_path, 
        filename=f"biography_{task_id}.txt", 
        media_type="text/plain; charset=utf-8"
    )

@app.get("/api/download-pdf/{task_id}")
async def download_pdf(task_id: str):
    """下载PDF文件"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_status[task_id]
    if task.status != "completed" or not task.result:
        raise HTTPException(status_code=400, detail="任务未完成")
    
    pdf_path = task.result.get("pdf_path")
    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF文件不存在")
    
    return FileResponse(
        pdf_path, 
        filename=f"biography_{task_id}.pdf", 
        media_type="application/pdf"
    )

@app.get("/api/view-result/{task_id}")
async def view_result(task_id: str):
    """在线查看结果"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = task_status[task_id]
    if task.status != "completed" or not task.result:
        raise HTTPException(status_code=400, detail="任务未完成")
    
    result = task.result
    uploaded_files = task.uploaded_files
    
    # 生成在线查看页面
    file_previews = ""
    for file_info in uploaded_files:
        if file_info.get('is_image'):
            file_previews += f"""
            <div class="file-preview">
                <img src="{file_info.get('thumbnail_url', file_info['url'])}" alt="{file_info['original_name']}">
                <p>{file_info['original_name']}</p>
            </div>
            """
        elif file_info.get('is_video'):
            file_previews += f"""
            <div class="file-preview">
                <video controls width="200">
                    <source src="{file_info['url']}" type="{file_info['content_type']}">
                </video>
                <p>{file_info['original_name']}</p>
            </div>
            """
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>传记查看 - {task_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .files-section {{ margin-bottom: 30px; }}
            .file-previews {{ display: flex; flex-wrap: wrap; gap: 15px; }}
            .file-preview {{ text-align: center; }}
            .file-preview img, .file-preview video {{ max-width: 200px; border-radius: 8px; }}
            .content {{ line-height: 1.8; text-align: justify; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat {{ text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📖 个人传记</h1>
            <div class="stats">
                <div class="stat">
                    <strong>{result['word_count']}</strong><br>字数
                </div>
                <div class="stat">
                    <strong>{result['file_count']}</strong><br>文件数
                </div>
                <div class="stat">
                    <strong>{result['image_count']}</strong><br>图片数
                </div>
            </div>
        </div>
        
        <div class="files-section">
            <h2>📁 相关文件</h2>
            <div class="file-previews">
                {file_previews}
            </div>
        </div>
        
        <div class="content">
            <h2>📝 传记内容</h2>
            {result['biography'].replace(chr(10), '<br>')}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 启动个人传记撰写Agent增强测试平台")
    print("📱 访问地址: http://localhost:8002")
    print("✨ 新功能：多媒体上传、PDF生成、在线预览")
    uvicorn.run(app, host="0.0.0.0", port=8002) 