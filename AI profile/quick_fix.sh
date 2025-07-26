#!/bin/bash

echo "🔧 AI Profile 项目快速修复脚本"
echo "================================"

# 清理编译缓存
echo "1. 清理 Xcode 编译缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/AI_profile* 2>/dev/null
echo "✅ 编译缓存已清理"

# 检查文件结构
echo ""
echo "2. 检查项目文件结构..."
if [ -f "AI_profileApp.swift" ]; then
    echo "✅ AI_profileApp.swift 存在"
else
    echo "❌ AI_profileApp.swift 缺失"
fi

if [ -f "Models.swift" ]; then
    echo "✅ Models.swift 存在"
else
    echo "❌ Models.swift 缺失"
fi

if [ -f "Theme.swift" ]; then
    echo "✅ Theme.swift 存在"
else
    echo "❌ Theme.swift 缺失"
fi

if [ -d "Views" ]; then
    echo "✅ Views 目录存在"
    echo "   Views 目录内容："
    ls Views/
else
    echo "❌ Views 目录缺失"
fi

if [ -d "Services" ]; then
    echo "✅ Services 目录存在"
else
    echo "❌ Services 目录缺失"
fi

echo ""
echo "3. 当前目录结构："
echo "$(pwd)"
ls -la

echo ""
echo "🚀 下一步操作："
echo "1. 在 Xcode 中打开 AI profile.xcodeproj"
echo "2. 按照 XCODE_FIX_GUIDE.md 中的步骤重新添加文件"
echo "3. 清理并重新编译项目"

echo ""
echo "修复完成！请查看 XCODE_FIX_GUIDE.md 了解详细步骤。" 