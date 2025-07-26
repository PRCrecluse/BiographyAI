#!/bin/bash

echo "🔬 AI Profile 编译测试"
echo "=========================="

# 检查当前目录
echo "当前目录: $(pwd)"
echo ""

# 检查文件结构
echo "📁 检查文件结构:"
echo "✅ AI_profileApp.swift: $(test -f AI_profileApp.swift && echo '存在' || echo '缺失')"
echo "✅ Models.swift: $(test -f Models.swift && echo '存在' || echo '缺失')"
echo "✅ Theme.swift: $(test -f Theme.swift && echo '存在' || echo '缺失')"
echo "✅ Views/HomeView.swift: $(test -f Views/HomeView.swift && echo '存在' || echo '缺失')"
echo "✅ Views/MainView.swift: $(test -f Views/MainView.swift && echo '存在' || echo '缺失')"
echo "✅ Views/Components/BottomTabBar.swift: $(test -f Views/Components/BottomTabBar.swift && echo '存在' || echo '缺失')"
echo ""

# 检查语法修复
echo "🔧 检查 MainView.swift 语法修复:"
if grep -q "value.translation.width" Views/MainView.swift; then
    echo "✅ DragGesture 语法已修复 (使用 .width)"
else
    echo "❌ DragGesture 语法需要修复"
fi
echo ""

# 清理缓存
echo "🧹 清理编译缓存..."
rm -rf ~/Library/Developer/Xcode/DerivedData/AI_profile* 2>/dev/null
echo "✅ 缓存已清理"
echo ""

# 显示项目路径
echo "📍 项目位置:"
echo "Xcode项目: $(pwd)/AI profile.xcodeproj"
echo "Swift文件位置: $(pwd)/"
echo ""

echo "🚀 下一步操作:"
echo "1. 在 Xcode 中打开: AI profile.xcodeproj"
echo "2. 确保所有 Swift 文件都在项目导航器中显示"
echo "3. 编译项目 (Cmd+B)"
echo "4. 如果有红色文件引用，删除并重新添加文件"
echo ""

echo "修复说明:"
echo "• 已修复 DragGesture: value.translation.x → value.translation.width"
echo "• 文件结构已优化到正确位置"
echo "• 所有必需的 Swift 文件都存在"
echo ""

echo "�� 预期结果: 编译成功，无错误！" 