# Biography AI - 安全配置指南

## 🔒 环境变量配置

在部署此项目之前，请确保正确配置以下环境变量：

### 1. AI 服务配置
```bash
# OpenAI API (可选)
OPENAI_API_KEY=your-openai-api-key-here

# 豆包/字节跳动 API (必需)
DOUBAO_API_KEY=your-doubao-api-key-here

# 火山引擎 ARK API (可选)
ARK_API_KEY=your-ark-api-key-here
```

### 2. Supabase 数据库配置
```bash
# Supabase 项目URL
SUPABASE_URL=https://your-project-id.supabase.co

# Supabase 匿名密钥
SUPABASE_ANON_KEY=your-supabase-anon-key-here
```

### 3. 部署配置
```bash
# API 基础URL
API_BASE_URL=https://biographyai.zeabur.app

# 服务端口
PORT=8080

# 运行环境
NODE_ENV=production
```

## 📱 iOS 应用配置

在 `AI profile/AI profile/AI profile/Services/SupabaseService.swift` 中更新：

```swift
private let supabaseURL = "https://your-project-id.supabase.co"
private let supabaseAnonKey = "your-supabase-anon-key-here"
```

## 🚀 部署步骤

### 1. Zeabur 部署
1. Fork 此仓库到您的 GitHub 账户
2. 在 Zeabur 中连接您的 GitHub 仓库
3. 设置环境变量（见上方配置）
4. 部署 `agent` 目录

### 2. Vercel 部署（备选）
1. 在 Vercel 中导入项目
2. 设置环境变量
3. 部署根目录

## ⚠️ 安全注意事项

1. **永远不要**将真实的API密钥提交到代码仓库
2. 使用 `.env` 文件存储本地环境变量（已在 .gitignore 中排除）
3. 在生产环境中通过平台环境变量设置敏感信息
4. 定期轮换API密钥和数据库凭据

## 🔧 本地开发

1. 复制 `.env.example` 为 `.env`
2. 填入您的实际API密钥和配置
3. 确保 `.env` 文件不被提交到版本控制

## 📞 获取API密钥

### Supabase
1. 访问 [supabase.com](https://supabase.com)
2. 创建新项目
3. 在项目设置中获取URL和匿名密钥

### 豆包API
1. 访问火山引擎控制台
2. 开通豆包大模型服务
3. 获取API密钥

### OpenAI (可选)
1. 访问 [platform.openai.com](https://platform.openai.com)
2. 创建API密钥

## 🆘 故障排除

如果遇到API连接问题：
1. 检查环境变量是否正确设置
2. 验证API密钥是否有效
3. 确认网络连接和防火墙设置
4. 查看应用日志获取详细错误信息
