# Biography AI 1.0 🤖📖

Turn your lifestories into a storybook!


关于我为什么要做这个
✨我觉得把自己的人生记忆封存到一本书里，不是以日记而是以更丰富的形式留存，如果可以把图文、视频和叙事串联到一起微缩到一起，肯定会是很酷的事（当然你会说bilibili录视频也可以啊～）。我觉得这是非常个人的事情，所以专门造了一个空间。但当时我只花了非常简陋的手写草稿，却一直没有开始做这件事。
 
·如果你的人生故事可以直接打印出来变成一本书，你一定非常愿意看（划掉）或者，
当你垂垂老矣，
坐在床边，
伴着些许烛光，
用已经染上浊黄的双眼，
轻启扉页…
.
.
这时仿佛一切都会变得不同。
目前在demo阶段，AI和排版功能还没优化（几乎只有UI壳子还是拼了命做出来的一点点md登录注册还要加）but27号会在Github开源，欢迎大家来看～
## ✨ 功能特性

- 🖼️ **图片分析**: 使用AI分析用户上传的照片
- 📝 **智能生成**: 基于图片和用户描述生成个人传记
- 🎨 **多种模板**: 支持经典、现代、优雅、创意四种风格
- 🌍 **多语言支持**: 支持中文、英文、意大利语、法语、葡萄牙语、西班牙语
- 📱 **API接口**: 提供完整的RESTful API
- ☁️ **云部署**: 支持Vercel无服务器部署


## 联系我们
My Wechat

你也可以在我们的社区找到我们，我们正在为未来的超级个体们打造一个社区：
www.ideaspark.asia，我们是Vibe Coding的忠实爱好者，也在不定期举办Meetup

小红书：智创AI工作室
## 📞 联系我们

**WeChat QR Code:**

![WeChat QR Code](assets/wechat-qr.png)

你也可以在我们的社区找到我们，我们正在为未来的超级个体们打造一个社区：
www.ideaspark.asia，我们是Vibe Coding的忠实爱好者，也在不定期举办Meetup

小红书：智创AI工作室

## 🚀 Quick Start

### Local Development

1. **Clone Repository**
```bash
git clone git@github.com:PRCrecluse/BiographyAI.git
cd BiographyAI
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. **Start Service**
```bash
python dashboard_server.py
```

Service will start at `http://localhost:8000`

### Vercel Deployment

1. **Fork this repository to your GitHub account**

2. **Import project in Vercel**
   - Login to [Vercel](https://vercel.com)
   - Click "New Project"
   - Import your forked repository

3. **Configure Environment Variables**
   Add in Vercel project settings:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

4. **Deploy**
   Vercel will automatically deploy using `vercel.json` configuration

## 📊 API Documentation

### Health Check
```
GET /api/health
```

### Create Biography
```
POST /api/biography/create
Content-Type: multipart/form-data

Parameters:
- user_requirements: User requirements description
- template_style: Template style (classic/modern/elegant/creative)
- language: Language (zh-CN/en/it/fr/pt/es)
- files: Image files (optional)
```

### Query Status
```
GET /api/biography/status/{task_id}
```

### Download Biography
```
GET /api/biography/download/{task_id}
```

### Get Statistics
```
GET /api/stats
```

## 🏗️ Project Structure

```
├── api/                    # API routes
│   ├── biography/          # Biography related APIs
│   ├── health.py          # Health check
│   ├── stats.py           # Statistics API
│   └── main.py            # FastAPI main application
├── core/                   # Core modules
│   ├── agent_orchestrator.py
│   └── models.py
├── services/               # Service layer
│   ├── ai_service.py
│   └── file_service.py
├── tools/                  # Tool modules
│   ├── image_analyzer.py
│   ├── pdf_generator.py
│   ├── text_generator.py
│   └── qr_generator.py
├── config/                 # Configuration files
├── static/                 # Static files
├── uploads/                # Upload directory
├── output/                 # Output directory
├── dashboard_server.py     # Main server
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## 🔧 Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Services**: OpenAI GPT-4, Vision API
- **Database**: Supabase
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow
- **Deployment**: Vercel, Uvicorn
- **Containerization**: Docker support

## 📝 Usage Example

```python
import requests

# Create biography
response = requests.post('http://localhost:8000/api/biography/create', 
    data={
        'user_requirements': 'Describe my life story',
        'template_style': 'modern',
        'language': 'en'
    },
    files={'files': open('photo.jpg', 'rb')}
)

task_id = response.json()['task_id']

# Query status
status = requests.get(f'http://localhost:8000/api/biography/status/{task_id}')

# Download PDF
if status.json()['status'] == 'completed':
    pdf = requests.get(f'http://localhost:8000/api/biography/download/{task_id}')
    with open('biography.pdf', 'wb') as f:
        f.write(pdf.content)
```

## 🤝 Contributing

1. Fork this repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 📞 Contact

- Email: 1765591779@qq.com
- GitHub: [@PRCrecluse](https://github.com/PRCrecluse)

## 🙏 Acknowledgments

- OpenAI for powerful AI services
- Supabase for database services
- Vercel for deployment platform
