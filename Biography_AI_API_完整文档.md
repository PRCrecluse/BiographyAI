# Biography AI - 完整API端点文档

## 🌐 生产环境基础URL
```
https://biographyai.zeabur.app
```

## 📋 API端点总览

### 1. 系统管理API

#### 1.1 健康检查
- **端点**: `GET /api/health`
- **用途**: 检查API服务状态和可用端点
- **响应示例**:
```json
{
  "status": "healthy",
  "message": "Agent API运行正常",
  "timestamp": "2025-01-25T12:50:43.205272",
  "version": "3.0-fixed",
  "environment": "vercel-serverless",
  "endpoints": {
    "health": "/api/health",
    "create": "/api/biography/create",
    "status": "/api/biography/status/{task_id}",
    "download": "/api/biography/download/{task_id}"
  },
  "connection_test": "success"
}
```

#### 1.2 统计信息
- **端点**: `GET /api/stats`
- **用途**: 获取API使用统计
- **响应**: 包含任务数量、成功率等统计信息

### 2. 传记生成核心API

#### 2.1 创建传记任务
- **端点**: `POST /api/biography/create`
- **用途**: 创建新的传记生成任务
- **请求格式**: `multipart/form-data`
- **请求参数**:
  - `user_requirements` (string): 用户需求描述
  - `language` (string): 语言设置 (如: "zh-CN", "en-US")
  - `template_style` (string): 模板风格 (如: "professional", "modern", "classic")
  - `image_0`, `image_1`, ... (file): 用户上传的图片文件

- **响应示例**:
```json
{
  "task_id": "test-task-a1b2c3d4",
  "status": "submitted",
  "message": "传记生成任务已提交，请使用task_id查询进度"
}
```

#### 2.2 查询任务状态
- **端点**: `GET /api/biography/status/{task_id}`
- **用途**: 查询传记生成任务的当前状态
- **路径参数**: `task_id` - 任务ID
- **响应示例**:
```json
{
  "task_id": "test-task-a1b2c3d4",
  "status": "completed",
  "progress": 100,
  "message": "传记生成完成",
  "created_at": "2025-01-25T12:00:00.000Z",
  "completed_at": "2025-01-25T12:05:00.000Z",
  "result_url": "/api/biography/download/test-task-a1b2c3d4"
}
```

**状态值说明**:
- `submitted`: 任务已提交
- `processing`: 正在处理
- `completed`: 处理完成
- `failed`: 处理失败

#### 2.3 下载传记结果
- **端点**: `GET /api/biography/download/{task_id}`
- **用途**: 下载生成的传记HTML文件
- **路径参数**: `task_id` - 任务ID
- **响应**: HTML文件内容或错误信息

### 3. 首页/仪表板
- **端点**: `GET /`
- **用途**: 显示API仪表板页面
- **响应**: HTML页面，包含API状态和使用说明

## 🔧 iOS应用集成要点

### AgentService配置
```swift
class AgentService {
    private let baseURL = "https://biographyai.zeabur.app"
    
    // 数据模型
    struct BiographyCreateRequest: Codable {
        let userRequirements: String
        let templateStyle: String
        let language: String
    }
    
    struct BiographyTaskResponse: Codable {
        let taskId: String
        let status: String
        let message: String
    }
}
```

### 关键实现细节
1. **multipart请求**: 使用标准multipart/form-data格式发送图片和表单数据
2. **任务轮询**: 创建任务后定期轮询状态直到完成
3. **错误处理**: 处理网络错误、JSON解析错误、API错误响应
4. **网络连接检查**: 在离线时禁用生成按钮

## 🚀 API使用流程

1. **健康检查**: 调用 `/api/health` 确认API可用
2. **创建任务**: POST到 `/api/biography/create` 提交用户数据和图片
3. **轮询状态**: 定期GET `/api/biography/status/{task_id}` 检查进度
4. **获取结果**: 任务完成后GET `/api/biography/download/{task_id}` 下载结果

## 🔒 安全和限制

- **超时设置**: 
  - 健康检查: 5秒
  - 统计信息: 10秒
  - 传记创建: 60秒
  - 状态查询: 5秒
  - 结果下载: 15秒

- **CORS支持**: 允许跨域请求
- **环境变量**: 需要配置 `DOUBAO_API_KEY` 用于AI服务

## 📝 测试和调试

### 测试脚本
- `test_multipart_api.py`: 测试multipart请求处理
- `test_api_connectivity.py`: 测试API连通性
- `test_status_api.py`: 测试状态查询API

### 调试信息
- API提供详细的控制台日志
- 健康检查端点显示所有可用端点
- 错误响应包含具体错误信息

## 🎯 重要修复记录

### multipart解析修复 (2025-01-25)
- **问题**: iOS应用发送的multipart请求返回"创建传记失败"
- **原因**: API的multipart解析逻辑过于简化
- **修复**: 重构解析逻辑，使用boundary正确分割数据，支持提取所有表单字段

### Vercel部署路径修复
- **问题**: API文件路径不符合Vercel要求
- **解决**: 将API文件复制到根目录api文件夹，更新vercel.json配置

## 🌟 API特性

- ✅ 支持多图片上传
- ✅ 多语言支持 (中文/英文)
- ✅ 多种模板风格
- ✅ 实时状态跟踪
- ✅ 详细错误信息
- ✅ 跨域请求支持
- ✅ 生产环境稳定运行

---

**最后更新**: 2025-01-25  
**API版本**: 3.0-fixed  
**部署状态**: ✅ 生产环境正常运行  
**测试状态**: ✅ 所有端点正常工作
