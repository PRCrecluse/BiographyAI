#!/bin/bash

echo "🎯 AI Profile 最终修复检查"
echo "=========================="
echo ""

# 当前目录
echo "📍 当前位置: $(pwd)"
echo ""

# 检查Xcode期望的文件路径
echo "🔍 检查Xcode期望的文件路径:"
echo ""

# 检查 entitlements 文件
if [ -f "AI_profile.entitlements" ]; then
    echo "✅ AI_profile.entitlements 在根目录 (✓)"
else
    echo "❌ AI_profile.entitlements 缺失"
fi

# 检查 Preview Content
if [ -d "Preview Content" ]; then
    echo "✅ Preview Content 在根目录 (✓)"
else
    echo "❌ Preview Content 缺失"
fi

# 检查 Swift 文件在 AI profile/AI profile/ 目录
if [ -f "AI profile/AI profile/AI_profileApp.swift" ]; then
    echo "✅ Swift 文件在 AI profile/AI profile/ (✓)"
else
    echo "❌ Swift 文件在错误位置"
fi

# 检查 Views 在 AI profile/AI profile/Views/
if [ -f "AI profile/AI profile/Views/HomeView.swift" ]; then
    echo "✅ Views 在 AI profile/AI profile/Views/ (✓)"
else
    echo "❌ Views 目录错误"
fi

# 检查 MainView 的 DragGesture 语法
if [ -f "AI profile/AI profile/Views/MainView.swift" ]; then
    if grep -q "value.translation.width" "AI profile/AI profile/Views/MainView.swift"; then
        echo "✅ MainView DragGesture 语法正确 (.width)"
    else
        echo "❌ MainView DragGesture 语法需要修复"
    fi
else
    echo "❌ MainView.swift 文件缺失"
fi

echo ""
echo "📁 完整目录结构检查:"
echo "当前目录内容:"
ls -la | grep -E "(AI_profile\.entitlements|Preview Content|AI profile)"

echo ""
echo "AI profile/AI profile/ 内容:"
if [ -d "AI profile/AI profile" ]; then
    ls -la "AI profile/AI profile/" | head -10
else
    echo "目录不存在"
fi

echo ""
echo "🧹 清理编译缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/AI_profile* 2>/dev/null
echo "✅ 缓存已清理"

echo ""
echo "🚀 状态总结:"
echo "如果所有项目都显示 ✅，那么:"
echo "1. 在 Xcode 中打开项目"
echo "2. 检查项目导航器中的文件引用"
echo "3. 删除任何红色(无效)的文件引用"
echo "4. 重新添加文件(如果需要)"
echo "5. 编译项目 (Cmd+B)"
echo ""
echo "预期结果: 编译成功，所有错误解决！" 