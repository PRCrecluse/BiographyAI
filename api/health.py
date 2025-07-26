"""
健康检查API - 优化版本
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """健康检查 - 快速响应"""
        try:
            # 立即设置响应
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # 简单快速的响应
            response = {
                "status": "healthy",
                "message": "Agent API运行正常",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0-fixed",
                "environment": "vercel-serverless",
                "endpoints": {
                    "health": "/api/health",
                    "create": "/api/biography/create", 
                    "status": "/api/biography/status/{task_id}",
                    "download": "/api/biography/download/{task_id}"
                },
                "connection_test": "success"
            }
            
            # 写入响应并立即刷新
            response_text = json.dumps(response, ensure_ascii=False, indent=2)
            self.wfile.write(response_text.encode('utf-8'))
            self.wfile.flush()
            
        except Exception as e:
            # 错误处理
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                "status": "error",
                "message": f"健康检查失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers() 
    
    def do_POST(self):
        """允许POST请求也返回健康状态"""
        self.do_GET() 