#!/usr/bin/env python3
"""
快速路由测试脚本 - 验证API端点是否正确路由
"""
import urllib.request
import json
import sys

def test_status_api():
    """测试状态API是否返回JSON而不是HTML"""
    url = "https://biographyai.zeabur.app/api/biography/status/test-task-aa5da9b3"
    
    try:
        # 创建请求，明确指定Accept头
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('User-Agent', 'iOS-Biography-App/1.0')
        
        # 发送请求
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            status_code = response.getcode()
            content_type = response.getheader('Content-Type', '')
            
            print(f"🌐 URL: {url}")
            print(f"📊 状态码: {status_code}")
            print(f"📄 Content-Type: {content_type}")
            print(f"📝 响应长度: {len(content)} 字符")
            
            # 检查是否是HTML响应
            if content.strip().startswith('<!DOCTYPE html>'):
                print("❌ 错误：收到HTML响应而不是JSON")
                print("🔍 HTML内容预览:")
                print(content[:200] + "...")
                return False
            
            # 尝试解析JSON
            try:
                data = json.loads(content)
                print("✅ 成功：收到有效的JSON响应")
                print("📋 JSON内容:")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                return True
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                print("📄 原始响应:")
                print(content)
                return False
                
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_create_api():
    """测试创建API"""
    print("\n" + "="*50)
    print("🧪 测试创建API...")
    
    url = "https://biographyai.zeabur.app/api/biography/create"
    
    # 模拟multipart/form-data请求
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    data = f"""------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="user_requirements"\r
\r
测试传记生成需求\r
------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="template_style"\r
\r
classic\r
------WebKitFormBoundary7MA4YWxkTrZu0gW\r
Content-Disposition: form-data; name="language"\r
\r
zh-CN\r
------WebKitFormBoundary7MA4YWxkTrZu0gW--\r
""".encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        req.add_header('Accept', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            status_code = response.getcode()
            
            print(f"📊 状态码: {status_code}")
            print(f"📝 响应: {content}")
            
            if status_code == 200:
                try:
                    data = json.loads(content)
                    print("✅ 创建API工作正常")
                    return data.get('task_id')
                except:
                    print("❌ 创建API返回非JSON响应")
                    return None
            else:
                print("❌ 创建API返回错误状态码")
                return None
                
    except Exception as e:
        print(f"❌ 创建API请求失败: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始API路由测试...")
    print("="*50)
    
    # 测试状态API
    print("🔍 测试状态查询API...")
    status_ok = test_status_api()
    
    # 测试创建API
    task_id = test_create_api()
    
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"状态API: {'✅ 正常' if status_ok else '❌ 异常'}")
    print(f"创建API: {'✅ 正常' if task_id else '❌ 异常'}")
    
    if not status_ok:
        print("\n🔧 建议修复步骤:")
        print("1. 检查Vercel路由配置是否已部署")
        print("2. 确认 /api/biography/status/(.*) 路由规则")
        print("3. 验证status.py文件是否正确部署")
        
    return status_ok and task_id is not None

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
