#!/bin/bash

# 传记状态查询API修复部署脚本
# 作者：AI Assistant
# 版本：1.0.0

set -e  # 遇到错误立即退出

echo "🚀 开始部署状态查询API修复..."

# 检查是否安装了 vercel CLI
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI 未安装"
    echo "📦 正在安装 Vercel CLI..."
    npm install -g vercel
    echo "✅ Vercel CLI 安装完成"
fi

# 检查是否登录
echo "🔐 检查 Vercel 登录状态..."
if ! vercel whoami &> /dev/null; then
    echo "🔑 请登录 Vercel..."
    vercel login
fi

# 检查修复文件
echo "📁 检查修复文件..."
if [[ ! -f "api/biography/status.py" ]]; then
    echo "❌ 缺少修复文件: api/biography/status.py"
    exit 1
fi

echo "✅ 修复文件检查完成"

# 确认部署
echo ""
echo "⚠️ 重要提醒："
echo "此脚本将部署以下修复："
echo "1. 修复 status.py 使用 BaseHTTPRequestHandler 类"
echo "2. 确保 vercel.json 路由配置正确"
echo ""

read -p "是否继续部署？(y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "❌ 部署已取消"
    exit 0
fi

# 部署
echo "🚀 开始部署修复..."
vercel --prod

echo "🎉 修复部署完成！"
echo "📝 部署后测试："
echo "  1. 访问 /api/biography/status/test-id 测试状态API"
echo "  2. 检查Vercel函数日志"
echo ""
echo "如果问题仍然存在，请检查："
echo "1. Vercel日志中的详细错误信息"
echo "2. 确保 status.py 文件格式正确"
echo "3. 确保 vercel.json 配置正确" 