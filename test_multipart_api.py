#!/usr/bin/env python3
"""
测试传记创建API的multipart请求处理
模拟iOS应用发送的multipart/form-data请求
"""

import requests
import json
from io import BytesIO
from PIL import Image

def create_test_image():
    """创建测试图片"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_biography_create_api():
    """测试传记创建API"""
    print("🧪 开始测试传记创建API...")
    
    # API端点
    url = "http://localhost:8000/api/biography/create"
    
    # 准备测试数据
    test_data = {
        'user_requirements': '我是一个软件工程师，喜欢编程和旅行。请帮我生成一份专业的传记。',
        'language': 'zh-CN',
        'template_style': 'professional'
    }
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 准备multipart文件
    files = {
        'user_requirements': (None, test_data['user_requirements']),
        'language': (None, test_data['language']),
        'template_style': (None, test_data['template_style']),
        'image_0': ('test_image.jpg', test_image, 'image/jpeg'),
    }
    
    try:
        print(f"📡 发送请求到: {url}")
        print(f"📋 请求数据: {test_data}")
        
        # 发送请求
        response = requests.post(url, files=files, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ 成功响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 测试任务状态查询
                if 'task_id' in result:
                    task_id = result['task_id']
                    print(f"\n🔍 测试任务状态查询: {task_id}")
                    status_url = f"http://localhost:8000/api/biography/status/{task_id}"
                    status_response = requests.get(status_url)
                    
                    if status_response.status_code == 200:
                        status_result = status_response.json()
                        print(f"✅ 状态查询成功: {json.dumps(status_result, ensure_ascii=False, indent=2)}")
                    else:
                        print(f"❌ 状态查询失败: {status_response.status_code} - {status_response.text}")
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"📄 原始响应: {response.text}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"📄 错误响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求异常: {e}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def test_production_api():
    """测试生产环境API"""
    print("\n🌐 测试生产环境API...")
    
    # 生产API端点
    url = "https://biographyai.zeabur.app/api/biography/create"
    
    # 准备测试数据
    test_data = {
        'user_requirements': '测试用户需求：我是一个产品经理，专注于AI产品开发。',
        'language': 'zh-CN',
        'template_style': 'modern'
    }
    
    # 创建测试图片
    test_image = create_test_image()
    
    # 准备multipart文件
    files = {
        'user_requirements': (None, test_data['user_requirements']),
        'language': (None, test_data['language']),
        'template_style': (None, test_data['template_style']),
        'image_0': ('test_image.jpg', test_image, 'image/jpeg'),
    }
    
    try:
        print(f"📡 发送请求到: {url}")
        response = requests.post(url, files=files, timeout=30)
        
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ 生产环境成功: {json.dumps(result, ensure_ascii=False, indent=2)}")
            except json.JSONDecodeError:
                print(f"❌ 生产环境返回非JSON: {response.text[:200]}...")
        else:
            print(f"❌ 生产环境失败: {response.status_code} - {response.text[:200]}...")
            
    except Exception as e:
        print(f"❌ 生产环境测试异常: {e}")

if __name__ == "__main__":
    # 测试本地API（如果运行）
    test_biography_create_api()
    
    # 测试生产环境API
    test_production_api()
    
    print("\n🏁 测试完成")
