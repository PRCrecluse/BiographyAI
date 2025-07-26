#!/usr/bin/env python3
"""
简单的API连通性测试
测试生产环境API是否正常响应
"""

import urllib.request
import json
import ssl
from urllib.error import URLError, HTTPError

def test_api_endpoint(url, description):
    """测试单个API端点"""
    print(f"🧪 测试 {description}: {url}")
    
    try:
        # 创建SSL上下文，忽略证书验证（仅用于测试）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 发送GET请求
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Biography-AI-Test/1.0')
        
        with urllib.request.urlopen(request, context=ssl_context, timeout=10) as response:
            status_code = response.getcode()
            content_type = response.getheader('Content-Type', '')
            content = response.read().decode('utf-8')
            
            print(f"✅ 状态码: {status_code}")
            print(f"📄 Content-Type: {content_type}")
            
            if 'application/json' in content_type:
                try:
                    json_data = json.loads(content)
                    print(f"📋 JSON响应: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
                except json.JSONDecodeError:
                    print(f"⚠️ JSON解析失败，原始内容: {content[:200]}...")
            else:
                print(f"📄 响应内容: {content[:200]}...")
            
            return True
            
    except HTTPError as e:
        print(f"❌ HTTP错误: {e.code} - {e.reason}")
        return False
    except URLError as e:
        print(f"❌ URL错误: {e.reason}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API连通性测试...\n")
    
    # 测试端点列表
    test_endpoints = [
        ("https://biographyai.zeabur.app/api/health", "健康检查"),
        ("https://biographyai.zeabur.app/api/stats", "统计信息"),
        ("https://biographyai.zeabur.app/", "首页"),
    ]
    
    results = []
    for url, description in test_endpoints:
        success = test_api_endpoint(url, description)
        results.append((description, success))
        print("-" * 50)
    
    # 总结测试结果
    print("\n📊 测试结果总结:")
    success_count = 0
    for description, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {description}: {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 总体结果: {success_count}/{len(results)} 个端点正常")
    
    if success_count == len(results):
        print("🎉 所有API端点都正常工作！")
    elif success_count > 0:
        print("⚠️ 部分API端点工作正常，需要检查失败的端点")
    else:
        print("💥 所有API端点都无法访问，可能是网络或部署问题")

if __name__ == "__main__":
    main()
