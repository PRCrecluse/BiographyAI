# 🚨 紧急路由修复指南

## 问题诊断

### 当前问题
iOS应用在查询任务状态时收到HTML而不是JSON，导致解析错误：
```
❌ JSON解析错误: dataCorrupted(...debugDescription: "Unexpected character '<' around line 2, column 9.")
```

### 根本原因
1. **Vercel路由配置未更新**：生产环境仍使用旧的路由配置
2. **状态API路由失效**：`/api/biography/status/{task_id}` 被路由到默认仪表板页面
3. **创建API正常工作**：能够成功创建任务并返回task_id

## 当前状态

### ✅ 已修复（本地）
- [x] 更新了 `agent/vercel.json` 路由配置
- [x] 修复了状态API的任务ID提取逻辑
- [x] 增强了创建API的multipart解析
- [x] 添加了测试任务ID `test-task-f43f7806` 和 `test-task-aa5da9b3`

### ❌ 待部署
- [ ] 将更新的路由配置部署到Vercel生产环境
- [ ] 验证状态API返回正确的JSON格式

## 修复方案

### 方案1：立即部署修复（推荐）
```bash
cd agent
vercel --prod
```

### 方案2：手动验证修复
1. 检查当前Vercel配置：
   ```json
   {
     "src": "/api/biography/status/(.*)",
     "dest": "/api/biography/status.py"
   }
   ```

2. 确认状态API文件存在：
   - `agent/api/biography/status.py`

3. 测试本地状态API：
   ```bash
   curl -X GET "http://localhost:8000/api/biography/status/test-task-aa5da9b3"
   ```

## 预期结果

### 修复后的状态API应返回：
```json
{
  "task_id": "test-task-aa5da9b3",
  "status": "completed",
  "progress": 100.0,
  "message": "传记生成完成",
  "created_at": "2025-01-25T19:35:00",
  "result": {
    "content": "这是一个为iOS应用测试的传记内容...",
    "title": "测试用户的个人传记"
  }
}
```

## 验证步骤

1. **部署后验证**：
   ```bash
   curl -H "Accept: application/json" \
        "https://biography-ai006-prcrecluse-prcrecluses-projects.vercel.app/api/biography/status/test-task-aa5da9b3"
   ```

2. **iOS应用测试**：
   - 创建新的传记任务
   - 观察状态查询是否返回JSON而不是HTML
   - 确认不再出现JSON解析错误

## 关键文件

### 已修复的文件
1. `agent/vercel.json` - 路由配置
2. `agent/api/biography/status.py` - 状态查询API
3. `agent/api/biography/create_optimized.py` - 创建API

### 需要部署的更改
- Vercel路由模式从 `:id` 改为 `(.*)`
- 增强的任务ID提取逻辑
- 添加的测试任务数据

## 紧急联系

如果部署后仍有问题，请检查：
1. Vercel部署日志
2. API端点响应头
3. 路由匹配规则

---
**创建时间**: 2025-07-25 20:04
**状态**: 🔴 等待部署
**优先级**: 🚨 紧急
