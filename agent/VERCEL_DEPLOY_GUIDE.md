# 🚀 Vercel部署指南

## ✅ 问题已修复

**修复的错误：**
1. **配置冲突错误：**
   ```
   The functions property cannot be used in conjunction with the builds property. Please remove one of them.
   ```

2. **环境变量错误：**
   ```
   Environment Variable "SUPABASE_URL" references Secret "supabase_url", which does not exist.
   ```

**修复说明：**
- ❌ 移除了冲突的 `functions` 属性
- ✅ 保留了 `builds` 配置
- ✅ 增加 `maxLambdaSize` 到 50mb
- ❌ 移除了vercel.json中的环境变量引用
- ✅ 改为在Vercel Dashboard中直接设置环境变量

## 🚀 现在可以正常部署！

### 1. 快速部署
```bash
# 确保使用修复后的配置
cp vercel_optimized.json vercel.json

# 部署到Vercel
vercel --prod
```

### 2. 环境变量配置
在Vercel Dashboard的项目设置 → Environment Variables中添加：

**必需的环境变量：**
```
DOUBAO_API_KEY=your-doubao-api-key
```

**可选的环境变量（如果你的项目需要）：**
```
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
```

⚠️ **重要：** 不要在vercel.json中引用这些环境变量，直接在Dashboard中设置即可。

### 3. 验证部署
部署成功后访问：
- `/api/health` - 健康检查
- `/api/biography/create` - 核心功能

## 📋 修复后的Vercel配置

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    },
    {
      "src": "static/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/health",
      "dest": "/api/health.py"
    },
    {
      "src": "/api/biography/create",
      "dest": "/api/biography/create_optimized.py"
    },
    {
      "src": "/api/biography/status/(.*)",
      "dest": "/api/biography/status.py?task_id=$1"
    },
    {
      "src": "/api/biography/download/(.*)",
      "dest": "/api/biography/download.py?task_id=$1"
    }
  ],
  "regions": ["hkg1"]
}
```

## 🎯 部署检查清单

- ✅ 使用优化后的 `requirements_optimized.txt`
- ✅ 使用修复后的 `vercel.json`
- ✅ 设置 `DOUBAO_API_KEY` 环境变量
- ✅ 确保项目大小 < 50MB
- ✅ 确保没有大文件目录（output/，uploads/）

## 🚨 常见问题

**Q: 提示"Environment Variable references Secret which does not exist"？**
A: 这个错误已修复！现在不在vercel.json中引用环境变量，而是直接在Vercel Dashboard中设置。

**Q: 仍然提示包太大？**
A: 检查是否有大文件目录未被 `.gitignore` 排除

**Q: 函数超时？**
A: 默认超时已优化，复杂任务会异步处理

**Q: 环境变量无法读取？**
A: 确保在Vercel Dashboard → Settings → Environment Variables中正确设置了`DOUBAO_API_KEY`

**Q: 部署成功但API无法访问？**
A: 检查路由配置，确保API文件存在于正确位置

## 📞 成功部署后

项目现在应该能够：
1. ✅ 正常部署到Vercel
2. ✅ 上传图片并分析
3. ✅ 生成个人传记
4. ✅ 支持多语言
5. ✅ 异步任务处理

---

**🎉 配置已完全修复，可以立即部署！** 