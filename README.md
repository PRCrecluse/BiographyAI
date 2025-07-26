# Biography AI 1.0 🤖📖

一个智能个人传记生成系统，使用AI技术根据用户上传的图片和描述自动生成精美的PDF传记。

## ✨ 功能特性

- 🖼️ **图片分析**: 使用AI分析用户上传的照片
- 📝 **智能生成**: 基于图片和用户描述生成个人传记
- 🎨 **多种模板**: 支持经典、现代、优雅、创意四种风格
- 🌍 **多语言支持**: 支持中文、英文、意大利语、法语、葡萄牙语、西班牙语
- 📱 **API接口**: 提供完整的RESTful API
- ☁️ **云部署**: 支持Vercel无服务器部署

## 🚀 快速开始

### 本地开发

1. **克隆仓库**
```bash
git clone git@github.com:PRCrecluse/Biography-AI1.0-.git
cd Biography-AI1.0-
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
创建 `.env` 文件：
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. **启动服务**
```bash
python dashboard_server.py
```

服务将在 `http://localhost:8000` 启动

### Vercel部署

1. **Fork此仓库到你的GitHub账户**

2. **在Vercel中导入项目**
   - 登录 [Vercel](https://vercel.com)
   - 点击 "New Project"
   - 导入你fork的仓库

3. **配置环境变量**
   在Vercel项目设置中添加：
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

4. **部署**
   Vercel会自动部署，使用配置文件 `vercel.json`

## 📊 API文档

### 健康检查
```
GET /api/health
```

### 创建传记
```
POST /api/biography/create
Content-Type: multipart/form-data

参数:
- user_requirements: 用户需求描述
- template_style: 模板风格 (classic/modern/elegant/creative)
- language: 语言 (zh-CN/en/it/fr/pt/es)
- files: 图片文件 (可选)
```

### 查询状态
```
GET /api/biography/status/{task_id}
```

### 下载传记
```
GET /api/biography/download/{task_id}
```

### 获取统计
```
GET /api/stats
```

## 🏗️ 项目结构

```
├── api/                    # API路由
│   ├── biography/          # 传记相关API
│   ├── health.py          # 健康检查
│   ├── stats.py           # 统计API
│   └── main.py            # FastAPI主应用
├── core/                   # 核心模块
│   ├── agent_orchestrator.py
│   └── models.py
├── services/               # 服务层
│   ├── ai_service.py
│   └── file_service.py
├── tools/                  # 工具模块
│   ├── image_analyzer.py
│   ├── pdf_generator.py
│   ├── text_generator.py
│   └── qr_generator.py
├── config/                 # 配置文件
├── static/                 # 静态文件
├── uploads/                # 上传文件目录
├── output/                 # 输出文件目录
├── dashboard_server.py     # 主服务器
├── vercel.json            # Vercel配置
└── requirements.txt       # Python依赖
```

## 🔧 技术栈

- **后端**: FastAPI, Python 3.8+
- **AI服务**: OpenAI GPT-4, Vision API
- **数据库**: Supabase
- **PDF生成**: ReportLab
- **图片处理**: Pillow
- **部署**: Vercel, Uvicorn
- **容器化**: Docker支持

## 📝 使用示例

```python
import requests

# 创建传记
response = requests.post('http://localhost:8000/api/biography/create', 
    data={
        'user_requirements': '描述我的人生故事',
        'template_style': 'modern',
        'language': 'zh-CN'
    },
    files={'files': open('photo.jpg', 'rb')}
)

task_id = response.json()['task_id']

# 查询状态
status = requests.get(f'http://localhost:8000/api/biography/status/{task_id}')

# 下载PDF
if status.json()['status'] == 'completed':
    pdf = requests.get(f'http://localhost:8000/api/biography/download/{task_id}')
    with open('biography.pdf', 'wb') as f:
        f.write(pdf.content)
```

## 🤝 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- Email: 1765591779@qq.com
- GitHub: [@PRCrecluse](https://github.com/PRCrecluse)

## 🙏 致谢

- OpenAI提供的强大AI服务
- Supabase提供的数据库服务
- Vercel提供的部署平台 # BiographyAI
