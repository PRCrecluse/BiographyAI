"""
Vercel Serverless 函数 - 传记创建
"""
import json
import uuid
from datetime import datetime

def handler(request):
    """Vercel Serverless 函数处理器"""
    
    # 设置CORS头
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS, GET',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    }
    
    # 处理OPTIONS预检请求
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # 处理POST请求
    if request.method == 'POST':
        try:
            task_id = str(uuid.uuid4())
            response_data = {
                "task_id": task_id,
                "status": "submitted",
                "message": "传记生成任务已提交",
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
    
    # 处理GET请求
    elif request.method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                "message": "传记创建API已就绪",
                "version": "1.0.0"
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