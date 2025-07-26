#!/bin/bash

echo "🚀 开始部署到Vercel..."

# 检查Vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ 未安装Vercel CLI"
    echo "请运行: npm i -g vercel"
    exit 1
fi

# 检查环境变量
if [ -z "$DOUBAO_API_KEY" ]; then
    echo "⚠️  建议设置DOUBAO_API_KEY环境变量"
    echo "或在Vercel项目设置中配置"
fi

# 预部署检查
echo "🔍 预部署检查..."

# 检查关键文件
required_files=("requirements.txt" "vercel.json" "api/biography/create_optimized.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少关键文件: $file"
        exit 1
    fi
done

# 检查.gitignore
if ! grep -q "output/" .gitignore 2>/dev/null; then
    echo "⚠️  .gitignore可能未正确配置"
fi

echo "✅ 预检查通过"

# 部署
echo "🚀 开始部署..."
vercel --prod

echo "🎉 部署完成！"
echo "📝 部署后测试："
echo "  1. 访问 /api/health 检查健康状态"
echo "  2. 访问 /api/biography/create 测试核心功能"
echo "  3. 检查Vercel函数日志"
