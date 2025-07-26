#!/usr/bin/env python3
"""
个人传记Agent - Zeabur部署入口文件
"""
import sys
import os
import traceback

print("🔧 Python启动调试信息:")
print(f"📍 Python版本: {sys.version}")
print(f"📁 当前工作目录: {os.getcwd()}")
print(f"📦 Python路径: {sys.path[:3]}...")  # 只显示前3个路径
print(f"📋 环境变量PORT: {os.environ.get('PORT', '未设置')}")

try:
    print("📥 导入uvicorn...")
    import uvicorn
    print("✅ uvicorn导入成功")
    
    print("📥 导入dashboard_server...")
    from dashboard_server import app
    print("✅ dashboard_server导入成功")
    
    print("🚀 启动个人传记Agent - Zeabur部署版本...")
    
    # Zeabur会自动设置PORT环境变量
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🌐 监听端口: {port}")
    print(f"🔗 访问地址: http://0.0.0.0:{port}")
    print("📊 启动FastAPI服务器...")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print(f"🔍 详细错误: {traceback.format_exc()}")
    sys.exit(1)
except Exception as e:
    print(f"❌ 启动失败: {e}")
    print(f"🔍 详细错误: {traceback.format_exc()}")
    sys.exit(1)
