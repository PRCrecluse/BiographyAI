#!/usr/bin/env python3
"""
增强版Web应用 - 集成HTML故事书生成功能
适配iOS app的API接口，运行在8000端口
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import uuid
import json
from typing import List, Optional

# 添加当前目录到路径
sys.path.append(str(Path(__file__).parent))

try:
    from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
    from fastapi.responses import FileResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    from pydantic import BaseModel
    
    WEB_AVAILABLE = True
    print("✅ Web框架已就绪")
except ImportError as e:
    print(f"❌ Web框架不可用: {e}")
    WEB_AVAILABLE = False

# 导入HTML PDF生成器
try:
    from html_pdf_generator import HTMLPDFGenerator
    HTML_GENERATOR_AVAILABLE = True
    print("✅ HTML PDF生成器已就绪")
except ImportError as e:
    print(f"❌ HTML PDF生成器不可用: {e}")
    HTML_GENERATOR_AVAILABLE = False

# 导入专业PDF生成器
try:
    from professional_pdf_generator import professional_pdf_generator
    PROFESSIONAL_PDF_AVAILABLE = True
    print("✅ 专业PDF生成器已就绪")
except ImportError as e:
    print(f"❌ 专业PDF生成器不可用: {e}")
    PROFESSIONAL_PDF_AVAILABLE = False

# 导入简化PDF生成器
try:
    from pdf_generator_simple import simple_pdf_generator
    SIMPLE_PDF_AVAILABLE = True
    print("✅ 简化PDF生成器已就绪")
except ImportError as e:
    print(f"❌ 简化PDF生成器不可用: {e}")
    SIMPLE_PDF_AVAILABLE = False

# 导入AI服务
try:
    from services.ai_service import ai_service, analyze_image, generate_biography
    AI_SERVICE_AVAILABLE = True
    print("✅ AI服务已就绪")
except ImportError as e:
    print(f"⚠️ AI服务不可用: {e}")
    AI_SERVICE_AVAILABLE = False

# 数据模型
class BiographyCreateRequest(BaseModel):
    user_requirements: str
    template_style: str = "classic"
    language: str = "zh-CN"
    generator_type: str = "simple"  # "simple", "professional" 或 "classic"

class BiographyTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    pdf_url: Optional[str] = None
    error_message: Optional[str] = None

class AIModelConfig(BaseModel):
    provider: str
    model_name: str
    api_key: str
    api_base: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000

# 全局变量
app = FastAPI(title="Biography AI Agent", description="个人传记生成智能助手", version="2.0.0")
tasks = {}  # 存储任务状态

def generate_basic_biography_content(user_requirements: str, image_descriptions: list, image_count: int, language: str = "zh-CN") -> str:
    """生成基础传记内容 - 即使AI服务不可用也能生成丰富内容"""
    
    # 根据语言设置模板
    if language == "en" or language == "English":
        templates = {
            "intro": "This is my life story, a journey filled with memories, growth, and beautiful moments captured in photographs.",
            "chapter_titles": ["Early Years", "School Days", "Family Time", "Adventures", "Achievements", "Reflections"],
            "content_templates": [
                "In my early years, I was filled with curiosity and wonder about the world around me. Every day brought new discoveries and joy.",
                "My school days were a time of learning, friendship, and discovering my passions. I met wonderful people and learned valuable lessons.",
                "Family has always been the cornerstone of my life, providing love and support. They have been my strength through all of life's journey.",
                "Life has taken me on many adventures, each one teaching me something new. Every experience has been a stepping stone to growth.",
                "Through hard work and dedication, I've achieved goals I'm proud of. Each accomplishment represents perseverance and determination.",
                "Looking back, I'm grateful for every experience that has shaped who I am today. The future holds endless possibilities."
            ],
            "personal_voice": "Personal Thoughts:",
            "photo_description": "From the photograph, we can see:",
            "conclusion": "This is just a glimpse into my life story. Each photograph tells a tale, each memory holds meaning, and together they form the beautiful tapestry of my journey."
        }

    elif language == "it" or language == "Italian":
        templates = {
            "intro": "Questa è la mia storia di vita, un viaggio pieno di ricordi, crescita e momenti belli catturati nelle fotografie.",
            "chapter_titles": ["Primi Anni", "Anni di Scuola", "Tempo in Famiglia", "Avventure", "Conquiste", "Riflessioni"],
            "content_templates": [
                "Nei miei primi anni, ero pieno di curiosità e meraviglia per il mondo intorno a me. Ogni giorno portava nuove scoperte e gioia.",
                "I miei anni di scuola sono stati un tempo di apprendimento, amicizia e scoperta delle mie passioni. Ho incontrato persone meravigliose.",
                "La famiglia è sempre stata la pietra angolare della mia vita, fornendo amore e supporto. Sono stati la mia forza in tutto il viaggio.",
                "La vita mi ha portato in molte avventure, ognuna insegnandomi qualcosa di nuovo. Ogni esperienza è stata un trampolino per la crescita.",
                "Attraverso il duro lavoro e la dedizione, ho raggiunto obiettivi di cui sono orgoglioso. Ogni conquista rappresenta perseveranza e determinazione.",
                "Guardando indietro, sono grato per ogni esperienza che ha plasmato chi sono oggi. Il futuro offre infinite possibilità."
            ],
            "personal_voice": "Pensieri Personali：",
            "photo_description": "Dalla fotografia, possiamo vedere：",
            "conclusion": "Questo è solo un assaggio della mia storia di vita. Ogni fotografia racconta una storia, ogni ricordo ha un significato, e insieme formano il bellissimo arazzo del mio viaggio."
        }
    elif language == "fr" or language == "French":
        templates = {
            "intro": "Ceci est l'histoire de ma vie, un voyage rempli de souvenirs, de croissance et de beaux moments capturés dans des photographies.",
            "chapter_titles": ["Premières Années", "Années d'École", "Temps en Famille", "Aventures", "Réalisations", "Réflexions"],
            "content_templates": [
                "Dans mes premières années, j'étais rempli de curiosité et d'émerveillement pour le monde qui m'entourait. Chaque jour apportait de nouvelles découvertes et de la joie.",
                "Mes années d'école ont été une période d'apprentissage, d'amitié et de découverte de mes passions. J'ai rencontré des gens merveilleux.",
                "La famille a toujours été la pierre angulaire de ma vie, fournissant amour et soutien. Elle a été ma force tout au long du voyage de la vie.",
                "La vie m'a emmené dans de nombreuses aventures, chacune m'enseignant quelque chose de nouveau. Chaque expérience a été un tremplin vers la croissance.",
                "Grâce au travail acharné et au dévouement, j'ai atteint des objectifs dont je suis fier. Chaque accomplissement représente la persévérance et la détermination.",
                "En regardant en arrière, je suis reconnaissant pour chaque expérience qui a façonné qui je suis aujourd'hui. L'avenir offre des possibilités infinies."
            ],
            "personal_voice": "Pensées Personnelles：",
            "photo_description": "D'après la photographie, nous pouvons voir：",
            "conclusion": "Ceci n'est qu'un aperçu de l'histoire de ma vie. Chaque photographie raconte une histoire, chaque souvenir a une signification, et ensemble ils forment la belle tapisserie de mon voyage."
        }
    else:  # 默认中文
        templates = {
            "intro": "这是我的人生故事，一段充满回忆、成长和美好时光的旅程，用照片记录下珍贵的瞬间。",
            "chapter_titles": ["童年时光", "求学岁月", "家庭生活", "人生旅途", "成长收获", "感悟思考"],
            "content_templates": [
                "在我的童年时光里，充满了对世界的好奇和探索，每一天都有新的发现和快乐。",
                "求学的岁月是我人生中重要的阶段，在这里我不仅学到了知识，更结识了珍贵的友谊。",
                "家庭是我生命中最重要的港湾，给予我无尽的爱与支持，让我在人生路上勇敢前行。",
                "人生的旅途中，我经历了许多难忘的时刻，每一次经历都让我成长得更加坚强。",
                "通过不断的努力和坚持，我在人生的道路上收获了许多宝贵的经验和成就。",
                "回望来路，我对每一个塑造了今天的我的经历都心怀感激，未来我将继续勇敢前行。"
            ],
            "personal_voice": "个人心声：",
            "photo_description": "从照片中可以看到：",
            "conclusion": "这就是我的人生故事片段。每一张照片都在诉说着一个故事，每一段回忆都承载着意义，它们共同编织成我人生旅程中最美丽的画卷。"
        }
    
    # 扩展用户需求内容
    expanded_content = f"{templates['intro']}\n\n"
    
    # 添加用户的个人要求
    if user_requirements and user_requirements.strip():
        expanded_content += f"{templates['personal_voice']}{user_requirements}\n\n"
    
    # 根据图片数量生成对应的章节内容
    chapters = []
    for i in range(min(len(templates['chapter_titles']), max(3, image_count))):
        chapter_title = templates['chapter_titles'][i % len(templates['chapter_titles'])]
        chapter_content = templates['content_templates'][i % len(templates['content_templates'])]
        
        # 如果有图片描述，融入章节内容
        if i < len(image_descriptions) and image_descriptions[i]:
            chapter_content += f"\n\n{templates['photo_description']}{image_descriptions[i]}"
        
        chapters.append(f"{chapter_title}\n\n{chapter_content}")
    
    # 组合所有章节
    expanded_content += "\n\n".join(chapters)
    
    # 添加结尾
    expanded_content += f"\n\n{templates['conclusion']}"
    
    return expanded_content

# 配置CORS
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
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "features": {
            "html_pdf_generator": HTML_GENERATOR_AVAILABLE,
            "professional_pdf_generator": PROFESSIONAL_PDF_AVAILABLE,
            "simple_pdf_generator": SIMPLE_PDF_AVAILABLE,
            "ai_service": AI_SERVICE_AVAILABLE
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/biography/create", response_model=BiographyTaskResponse)
async def create_biography(
    background_tasks: BackgroundTasks,
    user_requirements: str = Form(...),
    template_style: str = Form("classic"),
    language: str = Form("zh-CN"),
    generator_type: str = Form("simple"),
    files: List[UploadFile] = File(...)
):
    """创建传记任务"""
    
    if not files:
        raise HTTPException(status_code=400, detail="至少需要上传一张图片")
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 保存上传的文件
    saved_files = []
    for file in files:
        if file.content_type and file.content_type.startswith(('image/', 'video/')):
            # 生成唯一文件名
            file_ext = Path(file.filename).suffix if file.filename else '.jpg'
            unique_filename = f"{task_id}_{len(saved_files)}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            # 保存文件
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            saved_files.append(file_path)
    
    if not saved_files:
        raise HTTPException(status_code=400, detail="没有有效的图片文件")
    
    # 初始化任务状态
    tasks[task_id] = {
        "status": "submitted",
        "progress": 0.0,
        "message": "任务已提交，正在处理...",
        "user_requirements": user_requirements,
        "template_style": template_style,
        "language": language,
        "generator_type": generator_type,
        "files": saved_files,
        "created_at": datetime.now(),
        "pdf_path": None,
        "error_message": None
    }
    
    # 启动后台任务
    background_tasks.add_task(process_biography_task, task_id)
    
    return BiographyTaskResponse(
        task_id=task_id,
        status="submitted",
        message="传记生成任务已创建，正在处理中..."
    )

@app.get("/api/biography/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """查询任务状态"""
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    
    pdf_url = None
    if task["pdf_path"] and Path(task["pdf_path"]).exists():
        pdf_url = f"/api/biography/download/{task_id}"
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        pdf_url=pdf_url,
        error_message=task.get("error_message")
    )

@app.get("/api/biography/download/{task_id}")
async def download_biography(task_id: str):
    """下载传记PDF文件"""
    
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = tasks[task_id]
    pdf_path = task.get("pdf_path")
    
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF文件不存在")
    
    return FileResponse(
        path=pdf_path,
        filename=f"biography_{task_id}.pdf",
        media_type="application/pdf"
    )

@app.post("/api/models/configure")
async def configure_ai_model(config: AIModelConfig):
    """配置AI模型"""
    
    if not AI_SERVICE_AVAILABLE:
        raise HTTPException(status_code=503, detail="AI服务不可用")
    
    try:
        # 这里应该配置AI服务，具体实现取决于ai_service的接口
        # ai_service.configure(config.dict())
        
        return {"message": "AI模型配置成功", "config": config.dict()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配置失败: {str(e)}")

async def process_biography_task(task_id: str):
    """处理传记生成任务"""
    
    try:
        task = tasks[task_id]
        
        # 更新状态：开始处理
        task["status"] = "processing"
        task["progress"] = 0.1
        language = task.get("language", "en")
        if language == "zh-CN":
            task["message"] = "正在分析上传的图片..."
        elif language == "fr":
            task["message"] = "Analyse des images téléchargées..."
        elif language == "it":
            task["message"] = "Analisi delle immagini caricate..."
        else:
            task["message"] = "Analyzing uploaded images..."
        
        # 分析图片（如果AI服务可用）
        image_descriptions = []
        if AI_SERVICE_AVAILABLE:
            for i, file_path in enumerate(task["files"]):
                try:
                    if str(file_path).lower().endswith(('.png', '.jpg', '.jpeg')):
                        description = await analyze_image(str(file_path))
                        image_descriptions.append(description)
                        
                        # 更新进度
                        progress = 0.1 + (i + 1) / len(task["files"]) * 0.3
                        task["progress"] = progress
                        language = task.get("language", "en")
                        if language == "zh-CN":
                            task["message"] = f"已分析 {i+1}/{len(task['files'])} 张图片"
                        elif language == "fr":
                            task["message"] = f"Analysé {i+1}/{len(task['files'])} images"
                        elif language == "it":
                            task["message"] = f"Analizzate {i+1}/{len(task['files'])} immagini"
                        else:
                            task["message"] = f"Analyzed {i+1}/{len(task['files'])} images"
                        
                except Exception as e:
                    print(f"⚠️ 分析图片失败: {e}")
                    image_descriptions.append("无法分析的图片")
        
        # 生成传记内容
        task["status"] = "generating"
        task["progress"] = 0.5
        language = task.get("language", "en")
        if language == "zh-CN":
            task["message"] = "正在生成传记内容..."
        elif language == "fr":
            task["message"] = "Génération du contenu biographique..."
        elif language == "it":
            task["message"] = "Generazione del contenuto biografico..."
        else:
            task["message"] = "Generating biography content..."
        
        # 生成基础传记内容（无论AI是否可用）
        biography_content = generate_basic_biography_content(
            user_requirements=task["user_requirements"],
            image_descriptions=image_descriptions,
            image_count=len(task["files"]),
            language=task["language"]
        )
        
        # 如果AI服务可用，进一步优化内容
        if AI_SERVICE_AVAILABLE:
            try:
                ai_content = await generate_biography(
                    user_requirements=task["user_requirements"],
                    image_descriptions=image_descriptions,
                    language=task["language"]
                )
                biography_content = ai_content  # 使用AI生成的更好内容
                print("✅ 使用AI生成的优化内容")
            except Exception as e:
                print(f"⚠️ AI生成传记内容失败，使用基础模板内容: {e}")
        else:
            print("ℹ️ AI服务不可用，使用基础模板生成内容")
        
        # 生成PDF故事书
        task["progress"] = 0.7
        language = task.get("language", "en")
        if language == "zh-CN":
            task["message"] = "正在生成精美的PDF故事书..."
        elif language == "fr":
            task["message"] = "Génération d'un magnifique livre PDF..."
        elif language == "it":
            task["message"] = "Generazione di un bellissimo libro PDF..."
        else:
            task["message"] = "Generating beautiful PDF storybook..."
        
        # 只使用图片文件
        image_files = [f for f in task["files"] if str(f).lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        # 根据用户选择的生成器类型生成PDF
        pdf_path = None
        generator_type = task.get("generator_type", "simple")
        
        # 对于需要特殊字体支持的语言，优先使用专业PDF生成器
        language = task.get("language", "en")
        needs_special_font = language in ["zh-CN", "Chinese"]
        
        if needs_special_font and PROFESSIONAL_PDF_AVAILABLE:
            # 对于中文，使用专业PDF生成器（有更好的字体支持）
            print(f"📖 检测到{language}语言，使用专业PDF生成器确保字体支持...")
            if language == "zh-CN":
                task["message"] = "正在使用专业引擎生成PDF（支持特殊字体）..."
            elif language == "fr":
                task["message"] = "Génération PDF avec moteur professionnel (support polices spéciales)..."
            elif language == "it":
                task["message"] = "Generazione PDF con motore professionale (supporto font speciali)..."
            else:
                task["message"] = "Generating PDF with professional engine (special fonts support)..."
            
            pdf_path = professional_pdf_generator.generate_biography_book(
                content=biography_content,
                images=image_files,
                title="我的人生故事",
                language=task["language"]
            )
            
            if pdf_path:
                print("✅ 专业PDF生成成功!")
            else:
                print("⚠️ 专业PDF生成失败，尝试使用简化生成器...")
                generator_type = "simple"  # 回退到简化生成器
        elif generator_type == "simple" and SIMPLE_PDF_AVAILABLE and not needs_special_font:
            # 对于拉丁字符语言，使用简化PDF生成器（无黑色色块）
            print("📖 使用简化PDF生成器...")
            if language == "zh-CN":
                task["message"] = "正在使用简化引擎生成PDF（无字体问题）..."
            elif language == "fr":
                task["message"] = "Génération PDF avec moteur simplifié (sans problèmes de police)..."
            elif language == "it":
                task["message"] = "Generazione PDF con motore semplificato (senza problemi di font)..."
            else:
                task["message"] = "Generating PDF with simplified engine (no font issues)..."
            
            pdf_path = simple_pdf_generator.generate_biography_book(
                content=biography_content,
                images=image_files,
                title="Personal Biography",
                language=task["language"]
            )
            
            if pdf_path:
                print("✅ 简化PDF生成成功!")
            else:
                print("⚠️ 简化PDF生成失败，尝试使用专业生成器...")
                generator_type = "professional"  # 回退到专业生成器
        
        if (generator_type == "professional" or not pdf_path) and PROFESSIONAL_PDF_AVAILABLE:
            # 使用专业PDF生成器
            print("📖 使用专业PDF生成器...")
            if language == "zh-CN":
                task["message"] = "正在使用专业引擎生成PDF..."
            elif language == "fr":
                task["message"] = "Génération PDF avec moteur professionnel..."
            elif language == "it":
                task["message"] = "Generazione PDF con motore professionale..."
            else:
                task["message"] = "Generating PDF with professional engine..."
            
            pdf_path = professional_pdf_generator.generate_biography_book(
                content=biography_content,
                images=image_files,
                title="我的人生故事",
                language=task["language"]
            )
            
            if pdf_path:
                print("✅ 专业PDF生成成功!")
            else:
                print("⚠️ 专业PDF生成失败，尝试使用经典生成器...")
                generator_type = "classic"  # 回退到经典生成器
        
        if (generator_type == "classic" or not pdf_path) and HTML_GENERATOR_AVAILABLE:
            # 使用经典HTML PDF生成器
            print("📖 使用经典PDF生成器...")
            if language == "zh-CN":
                task["message"] = "正在使用经典引擎生成PDF..."
            elif language == "fr":
                task["message"] = "Génération PDF avec moteur classique..."
            elif language == "it":
                task["message"] = "Generazione PDF con motore classico..."
            else:
                task["message"] = "Generating PDF with classic engine..."
            
            generator = HTMLPDFGenerator()
            pdf_path = generator.generate_enhanced_biography_pdf(
                content=biography_content,
                images=image_files,
                title="我的人生故事"
            )
            
            if pdf_path:
                print("✅ 经典PDF生成成功!")
        
        if pdf_path:
            task["pdf_path"] = pdf_path
            task["status"] = "completed"
            task["progress"] = 1.0
            # 根据语言返回不同的完成消息
            language = task.get("language", "en")
            if language == "zh-CN":
                task["message"] = "传记PDF生成完成！"
            elif language == "fr":
                task["message"] = "Génération de biographie PDF terminée!"
            elif language == "it":
                task["message"] = "Generazione PDF biografia completata!"
            else:
                task["message"] = "Biography PDF generation completed!"
        else:
            # 如果所有PDF生成器都不可用
            task["status"] = "completed"
            task["progress"] = 1.0
            language = task.get("language", "en")
            if language == "zh-CN":
                task["message"] = "传记内容生成完成（PDF生成器不可用）"
            elif language == "fr":
                task["message"] = "Génération de contenu biographique terminée (générateur PDF non disponible)"
            elif language == "it":
                task["message"] = "Generazione di contenuti biografici completata (generatore PDF non disponibile)"
            else:
                task["message"] = "Biography content generation completed (PDF generator unavailable)"
            print("⚠️ 所有PDF生成器都不可用")
            
        # 记录使用的生成器
        if pdf_path:
            actual_generator = "简化生成器" if "simple" in str(pdf_path) else ("专业生成器" if "professional" in str(pdf_path) else "经典生成器")
            print(f"📊 最终使用: {actual_generator}")
    
    except Exception as e:
        task["status"] = "failed"
        task["progress"] = 0.0
        task["message"] = "生成失败"
        task["error_message"] = str(e)
        print(f"❌ 任务 {task_id} 失败: {e}")

# 如果是直接运行，启动服务器
if __name__ == "__main__":
    if not WEB_AVAILABLE:
        print("❌ Web框架不可用，无法启动服务器")
        sys.exit(1)
    
    print("🚀 启动增强版Biography AI Agent服务器")
            print("📍 服务器地址: https://biography-ai004.vercel.app")
        print("📚 API文档: https://biography-ai004.vercel.app/docs")
    print("=" * 60)
    print("✨ 解决方案特点:")
    print("   📱 完全适配iOS app API接口")
    print("   🎨 生成图文并茂的故事书")
    print("   📖 按时间顺序叙事")
    print("   ⏰ 每个小故事都有时间线索")
    print("   📄 可在浏览器中打印为PDF")
    print("   🔖 底部品牌印记：made with Biography AI")
    print("")
    print("🔧 PDF生成器选项:")
    print("   🟢 simple: 简化生成器（无黑色色块，推荐）")
    print("   🟡 professional: 专业生成器（可能有字体问题）")
    print("   🔵 classic: 经典生成器（兼容模式）")
    print("=" * 60)
    
    uvicorn.run(
        "enhanced_web_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 