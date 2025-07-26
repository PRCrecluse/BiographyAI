#!/bin/bash

# 传记AI Agent - 快速部署脚本
# 针对agent连接问题的紧急修复版本

echo "🚀 开始部署传记AI Agent到Vercel..."

# 检查是否在正确的目录
if [ ! -f "vercel.json" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 显示当前的API配置
echo "📋 当前API配置:"
echo "  ✓ health.py - 健康检查"
echo "  ✓ status.py - 任务状态查询 (已优化)"
echo "  ✓ create_optimized.py - 传记创建 (已修复)"
echo "  ✓ vercel.json - 路由配置 (已更新)"

# 检查重要文件是否存在
echo ""
echo "🔍 检查关键文件..."
files=(
    "api/health.py"
    "api/biography/status.py"
    "api/biography/create_optimized.py"
    "vercel.json"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ $file (缺失)"
    fi
done

# 部署到Vercel
echo ""
echo "🚀 开始部署到Vercel..."

# 检查是否有vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI未安装，请先安装: npm i -g vercel"
    exit 1
fi

# 执行部署
echo "📤 正在上传文件到Vercel..."
vercel --prod --yes

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 部署成功!"
    echo ""
    echo "🔗 测试连接:"
    echo "  健康检查: https://biography-ai006-51o9dru8k-prcrecluses-projects.vercel.app/api/health"
    echo "  状态查询: https://biography-ai006-51o9dru8k-prcrecluses-projects.vercel.app/api/biography/status/test-id"
    echo ""
    echo "📱 iOS应用现在应该能够连接了!"
echo ""
    echo "🔧 如果仍有问题，请检查:"
    echo "  1. iOS应用中的baseURL是否正确"
    echo "  2. 网络连接是否正常"
    echo "  3. Vercel部署日志是否有错误"
    
else
    echo "❌ 部署失败!"
    echo "请检查错误信息并重试"
    exit 1
fi

echo ""
echo "🎉 Agent连接问题修复完成!" 