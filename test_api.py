#!/usr/bin/env python3
"""
测试传记创建API
"""
import requests
import json

def test_api():
    """测试API端点"""
    
    # 测试GET请求
    print("测试GET请求...")
    try:
        response = requests.get("https://biographyai.zeabur.app/api/biography/create")
        print(f"GET状态码: {response.status_code}")
        print(f"GET响应: {response.text}")
    except Exception as e:
        print(f"GET错误: {e}")
    
    # 测试POST请求
    print("\n测试POST请求...")
    try:
        data = {
            'user_requirements': '测试传记创建',
            'language': 'zh-CN',
            'template_style': 'classic'
        }
        
        response = requests.post(
            "https://biographyai.zeabur.app/api/biography/create",
            data=data
        )
        print(f"POST状态码: {response.status_code}")
        print(f"POST响应: {response.text}")
    except Exception as e:
        print(f"POST错误: {e}")

if __name__ == "__main__":
    test_api()
