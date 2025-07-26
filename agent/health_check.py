#!/usr/bin/env python3
"""
简单的健康检查脚本 - 用于验证Zeabur环境
"""
import sys
import os

def main():
    print("🔍 环境健康检查开始...")
    print(f"📍 Python版本: {sys.version}")
    print(f"📁 当前目录: {os.getcwd()}")
    print(f"📋 PORT环境变量: {os.environ.get('PORT', '未设置')}")
    
    # 检查关键文件
    files_to_check = ['dashboard_server.py', 'requirements.txt', 'main.py']
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 不存在")
    
    # 检查关键依赖
    try:
        import fastapi
        print(f"✅ FastAPI版本: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI未安装")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn版本: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn未安装")
    
    try:
        import requests
        print(f"✅ Requests版本: {requests.__version__}")
    except ImportError:
        print("❌ Requests未安装")
    
    print("🏁 健康检查完成")

if __name__ == "__main__":
    main()
