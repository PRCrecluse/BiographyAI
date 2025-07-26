# Agent与iOS应用集成指南

## 📱 集成概览

本指南说明了如何将个人传记Agent与iOS应用进行完整集成，实现从图片上传到PDF传记生成的完整工作流程。

## 🏗️ 架构设计

### 核心组件
- **AgentService.swift**: 负责与Agent API通信
- **LocalStorageManager.swift**: 管理本地PDF文件存储  
- **BiographyGeneratorView.swift**: 传记生成界面
- **BiographyDetailView.swift**: 传记查看界面
- **AssetsView.swift**: 主要集成点，展示传记列表

## 🔄 集成流程

### 1. 图片上传
- 用户在AssetsView中上传图片
- 图片存储在state.assetsImages中
- 支持最多30张图片

### 2. 传记生成  
- 点击"开始生成"按钮
- 打开BiographyGeneratorView
- 用户输入要求，选择模板和语言
- AgentService发送请求到Agent API

### 3. 状态轮询
- 异步轮询任务状态
- 实时更新进度
- 完成后下载PDF

### 4. 本地存储
- PDF保存到Documents/Biographies/
- 更新传记列表
- 支持查看、分享、删除

## 🚀 使用说明

### 启动Agent服务
```bash
cd agent
pip install -r requirements.txt
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 配置AI模型
1. 在iOS应用中点击AI配置
2. 选择提供商（OpenAI、Claude等）
3. 输入API密钥
4. 保存配置

### 生成传记
1. 在Assets页面上传图片
2. 添加评论描述
3. 点击"开始生成"
4. 等待生成完成
5. 查看PDF传记

## 📊 技术特性

- ✅ 支持多种AI模型提供商
- ✅ 实时状态更新和进度显示  
- ✅ 本地PDF存储和管理
- ✅ 优雅的错误处理
- ✅ 流畅的用户体验

## 🔧 配置说明

### Agent服务配置
- 默认运行在localhost:8000
- 支持CORS跨域请求
- 提供完整的RESTful API

### iOS应用配置  
- 自动检测Agent连接状态
- 支持多种AI模型切换
- 本地存储配置持久化

---

*集成完成后，用户可以通过简单的界面操作完成个人传记的生成，所有生成的传记都会保存在本地并可以随时查看和分享。* 