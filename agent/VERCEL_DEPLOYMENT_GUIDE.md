# 个人传记 Agent - Vercel 部署指南

## 📋 概述

本指南帮助你将个人传记 Agent 系统部署到 Vercel 平台，采用 Serverless 架构实现高可用性和自动扩展。

## 🔍 资源需求分析

### Vercel vs 自建服务器对比

| 特性 | Vercel (推荐) | 自建服务器 |
|------|---------------|------------|
| **成本** | 免费额度高，按需付费 | 固定月费 (¥50-200/月) |
| **维护** | 零维护 | 需要运维 |
| **扩展性** | 自动扩展 | 手动扩展 |
| **可用性** | 99.9%+ SLA | 取决于配置 |
| **部署** | Git推送即部署 | 需要配置CI/CD |
| **SSL** | 自动HTTPS | 需要配置 |

### 💰 Vercel 费用预估

- **免费版限制**：
  - 100GB 月流量
  - 100GB-小时 函数执行时间
  - 10秒函数超时
  - 无商用限制

- **Pro 版 ($20/月)**：
  - 1TB 月流量
  - 1000GB-小时 函数执行时间
  - 60秒函数超时
  - 优先支持

**结论：对于中小型应用，Vercel 免费版完全够用！**

## 🚀 快速部署步骤

### 1. 准备工作

```bash
# 克隆项目
git clone <your-repo>
cd agent

# 安装 Vercel CLI
npm install -g vercel

# 登录 Vercel
vercel login
```

### 2. 配置环境变量

在 Vercel 仪表板中设置以下环境变量：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
DOUBAO_API_KEY=your-doubao-api-key
```

### 3. 部署到 Vercel

```bash
# 在 agent 目录下运行
vercel

# 按提示选择：
# - 项目名称
# - 确认部署设置
# - 等待部署完成
```

### 4. 验证部署

访问分配的域名，测试以下接口：
- `https://your-app.vercel.app/` - 主页面
- `https://your-app.vercel.app/api/health` - 健康检查
- `https://your-app.vercel.app/api/stats` - 统计信息

## 📁 项目结构

```
agent/
├── api/                          # Serverless 函数
│   ├── index.py                  # 主页面
│   ├── health.py                 # 健康检查
│   ├── stats.py                  # 统计信息
│   └── biography/
│       ├── create.py             # 传记创建
│       ├── status.py             # 状态查询
│       └── download.py           # 文件下载
├── static/                       # 静态文件
├── vercel.json                   # Vercel 配置
├── requirements_vercel.txt       # 优化的依赖
└── VERCEL_DEPLOYMENT_GUIDE.md    # 本文档
```

## ⚙️ 架构设计

### Serverless 函数拆分

原来的单体 FastAPI 应用已拆分为独立的 Serverless 函数：

1. **主页面** (`api/index.py`) - 统计仪表板
2. **健康检查** (`api/health.py`) - 服务状态
3. **统计信息** (`api/stats.py`) - 用户数据统计
4. **传记创建** (`api/biography/create.py`) - 处理文件上传和AI调用
5. **状态查询** (`api/biography/status.py`) - 查询生成进度
6. **文件下载** (`api/biography/download.py`) - 下载生成的传记

### 核心优化

1. **依赖精简**：移除大型库（reportlab、opencv等）
2. **函数拆分**：避免单一函数过大
3. **超时控制**：关键函数设置60秒超时
4. **错误处理**：完善的异常处理机制

## 🔧 技术限制及解决方案

### 1. 执行时间限制

**问题**：传记生成可能超过 Vercel 时间限制

**解决方案**：
```python
# 采用异步任务模式
asyncio.create_task(process_biography_task(task_id, ...))
# 客户端轮询查询进度
```

### 2. 文件存储限制

**问题**：Vercel 函数存储是临时的

**解决方案**：
- 使用 Vercel Blob 存储
- 或集成 AWS S3、阿里云 OSS

### 3. 依赖包大小限制

**问题**：某些库太大无法部署

**解决方案**：
```python
# 原来：使用 reportlab 生成PDF
# 现在：返回文本格式或使用在线PDF服务
def generate_simple_pdf_content(content: str) -> bytes:
    return content.encode('utf-8')
```

## 📊 监控与调试

### 查看日志

```bash
# 实时查看函数日志
vercel logs --follow

# 查看特定函数日志
vercel logs --follow --function=api/biography/create.py
```

### 性能监控

访问 Vercel 仪表板查看：
- 函数执行时间
- 内存使用情况
- 错误率统计
- 流量分析

## 🔄 持续部署

### 自动部署

配置 GitHub 集成实现自动部署：

1. 连接 GitHub 仓库
2. 推送到 main 分支自动触发部署
3. 预览环境用于测试

### 版本管理

```bash
# 部署到预览环境
vercel --prod=false

# 部署到生产环境  
vercel --prod
```

## 🚧 已知限制

1. **AI调用时间**：可能需要30-60秒
2. **文件上传**：限制在32MB以内
3. **并发处理**：免费版有并发限制
4. **PDF生成**：目前为简化版本

## 🔮 后续优化建议

### 短期优化

1. **集成真正的PDF生成**：
   - 使用在线PDF API（如 PDFShift、HTML/CSS to PDF）
   - 或客户端PDF生成

2. **添加文件存储**：
   ```bash
   npm install @vercel/blob
   ```

3. **优化AI调用**：
   - 添加缓存机制
   - 实现请求去重

### 长期规划

1. **数据库集成**：
   - Vercel Postgres
   - PlanetScale
   - 或保持 Supabase

2. **队列系统**：
   - Vercel KV (Redis)
   - 或外部队列服务

3. **实时通知**：
   - WebSocket 支持
   - Server-Sent Events

## 💡 最佳实践

1. **环境变量管理**：使用 Vercel 环境变量，不要硬编码
2. **错误处理**：完善的异常捕获和用户反馈
3. **日志记录**：关键操作添加详细日志
4. **性能优化**：避免冷启动，预热关键函数
5. **安全考虑**：API 限流、输入验证

## 📞 支持与帮助

- [Vercel 官方文档](https://vercel.com/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [豆包 API 文档](https://console.volcengine.com/ark)

---

**总结**：Vercel 部署简单快捷，免费额度足够中小型应用使用。建议先用 Vercel 验证产品，后期如有特殊需求再考虑自建服务器。 