#!/usr/bin/env python3
"""
测试API端点的脚本
"""
import requests
import json
import time

# API基础URL
BASE_URL = "https://biographyai.zeabur.app"

def test_create_endpoint():
    """测试创建端点"""
    print("🧪 测试创建端点...")
    
    url = f"{BASE_URL}/api/biography/create"
    
    # 模拟iOS应用的multipart/form-data请求
    files = {
        'user_requirements': (None, '测试用户需求：生成一份个人传记'),
        'template_style': (None, 'classic'),
        'language': (None, 'zh-CN'),
        'files': ('test.jpg', b'fake_image_data', 'image/jpeg')
    }
    
    try:
        response = requests.post(url, files=files, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 创建成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return data.get('task_id')
        else:
            print(f"❌ 创建失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return None

def test_status_endpoint(task_id):
    """测试状态查询端点"""
    print(f"\n🔍 测试状态查询端点 (任务ID: {task_id})...")
    
    url = f"{BASE_URL}/api/biography/status/{task_id}"
    
    try:
        response = requests.get(url, timeout=30)
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 查询成功: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"❌ 查询失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False

def test_known_task_id():
    """测试已知的任务ID"""
    print(f"\n🎯 测试已知任务ID...")
    return test_status_endpoint("test-task-f43f7806")

def main():
    """主测试函数"""
    print("🚀 开始API端点测试...\n")
    
    # 测试已知任务ID
    test_known_task_id()
    
    # 测试创建端点
    task_id = test_create_endpoint()
    
    if task_id:
        # 等待一下，然后测试状态查询
        print("\n⏳ 等待2秒后查询任务状态...")
        time.sleep(2)
        test_status_endpoint(task_id)
    
    print("\n🏁 测试完成!")

if __name__ == "__main__":
    main()
