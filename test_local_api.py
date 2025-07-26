#!/usr/bin/env python3
"""
本地测试简化版API
"""
import json
from datetime import datetime

class MockRequest:
    def __init__(self, method='GET', path='/', query='', headers=None, body=b''):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers or {}
        self.body = body

def handler(request):
    """模拟Vercel handler函数"""
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    if request.method == 'POST':
        try:
            task_id = str(uuid.uuid4())
            response_data = {
                "task_id": task_id,
                "status": "submitted",
                "message": "传记生成任务已提交，请稍后查询进度",
                "created_at": datetime.now().isoformat()
            }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data, ensure_ascii=False)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({
                    "error": "创建任务失败",
                    "detail": str(e)
                }, ensure_ascii=False)
            }
    
    elif request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "message": "传记创建API已就绪",
                "endpoints": {
                    "POST /": "创建传记任务",
                    "GET /": "API状态"
                }
            }, ensure_ascii=False)
        }
    
    else:
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({
                "error": "方法不被允许"
            }, ensure_ascii=False)
        }

# 测试
if __name__ == "__main__":
    print("测试GET请求...")
    req = MockRequest('GET')
    result = handler(req)
    print(f"状态码: {result['statusCode']}")
    print(f"响应: {result['body']}")
    
    print("\n测试POST请求...")
    req = MockRequest('POST', body=b'{"test": "data"}')
    result = handler(req)
    print(f"状态码: {result['statusCode']}")
    print(f"响应: {result['body']}")
    
    print("\nAPI测试完成！")
