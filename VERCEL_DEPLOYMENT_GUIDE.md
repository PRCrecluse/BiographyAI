# Vercel 部署指南 📚

## 🚀 一键部署步骤

### 1. 准备GitHub仓库
✅ **已完成** - 代码已推送到: https://github.com/PRCrecluse/Biography-AI1.0-.git

### 2. 在Vercel中导入项目

1. **登录Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 使用GitHub账户登录

2. **导入项目**
   - 点击 "New Project"
   - 选择 "Import Git Repository"
   - 搜索并选择 `Biography-AI1.0-`

3. **项目配置**
   - Framework Preset: `Other`
   - Root Directory: `./` (保持默认)
   - Build Command: 留空
   - Output Directory: 留空
   - Install Command: 留空

### 3. 配置环境变量

在Vercel项目设置中添加以下环境变量：

```bash
# 必需的环境变量
OPENAI_API_KEY=sk-your-openai-api-key-here
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key-here

# 可选的环境变量
DOUBAO_API_KEY=your-doubao-api-key-here
```

**配置步骤：**
1. 进入项目 Settings
2. 选择 Environment Variables
3. 添加上述变量
4. 点击 Save

### 4. 部署配置文件

项目已包含以下Vercel配置文件：

- `vercel.json` - 路由和函数配置
- `requirements.txt` - Python依赖（Vercel优化版本）
- `runtime.txt` - Python版本规范

### 5. 部署

1. **首次部署**
   - 配置完环境变量后，Vercel会自动触发部署
   - 部署时间约2-3分钟

2. **部署成功后的API端点**
   ```
   https://your-project.vercel.app/api/health          # 健康检查
   https://your-project.vercel.app/api/stats           # 系统统计
   https://your-project.vercel.app/api/biography/create # 创建传记
   https://your-project.vercel.app/api/biography/status/{id} # 查询状态
   https://your-project.vercel.app/api/biography/download/{id} # 下载传记
   ```

## 🔧 技术配置详情

### Python版本
- 使用 Python 3.9.18 (在 `runtime.txt` 中指定)

### 依赖优化
- 使用轻量级依赖包 (`requirements.txt`)
- 移除了大型库如 `reportlab`, `opencv-python` 等
- 优化包大小以符合Vercel限制

### 函数配置
- 传记创建: 最大执行时间 300秒
- 其他API: 10-30秒执行时间
- 支持文件上传和处理

### 存储配置
- 上传文件: Vercel临时存储
- 输出文件: 通过API直接返回
- 持久化数据: Supabase数据库

## 🐛 常见问题解决

### 1. 部署失败
**问题**: 依赖安装失败
**解决**: 
- 检查 `requirements.txt` 是否正确
- 确保使用Vercel兼容的包版本

### 2. API调用失败
**问题**: 环境变量未配置
**解决**:
- 确认所有必需的环境变量已添加
- 重新部署以应用新的环境变量

### 3. 函数超时
**问题**: 传记生成超时
**解决**:
- 已将创建函数超时设置为300秒
- 如需更长时间，考虑异步处理

### 4. 文件上传问题
**问题**: 图片上传失败
**解决**:
- 确保图片大小 < 10MB
- 支持格式: JPG, PNG, WEBP

## 📱 移动端兼容性

项目API完全兼容iOS Swift应用：
- 支持multipart/form-data上传
- 返回标准JSON格式
- 支持CORS跨域请求

## 🔄 持续部署

每次推送到main分支时，Vercel会自动重新部署：

```bash
# 更新代码
git add .
git commit -m "Update features"
git push origin main
```

## 🌟 性能优化建议

1. **使用CDN缓存静态资源**
2. **启用Vercel Analytics监控**
3. **配置自定义域名**
4. **启用HTTPS（自动）**

---

**部署完成后，您的Biography AI系统就可以在全球范围内使用了！** 🎉 