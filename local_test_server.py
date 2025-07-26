#!/usr/bin/env python3
"""
本地测试服务器 - 用于测试API功能
"""
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class LocalTestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"🔍 GET请求: {path}")
        
        if path == '/api/health':
            self.handle_health_check()
        elif path == '/api/test':
            self.handle_test_endpoint()
        elif path.startswith('/api/biography/status/'):
            task_id = path.split('/')[-1]
            self.handle_status_check(task_id)
        else:
            self.send_404()
    
    def do_POST(self):
        """处理POST请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        print(f"🔍 POST请求: {path}")
        
        if path == '/api/biography/create':
            self.handle_create_biography()
        else:
            self.send_404()
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    
    def handle_health_check(self):
        """健康检查端点"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                "status": "healthy",
                "message": "本地测试服务器运行正常",
                "timestamp": datetime.now().isoformat(),
                "version": "local-test-1.0",
                "environment": "local-development"
            }
            
            response_json = json.dumps(response, ensure_ascii=False, indent=2)
            self.wfile.write(response_json.encode('utf-8'))
            print("✅ 健康检查响应已发送")
            
        except Exception as e:
            print(f"❌ 健康检查错误: {e}")
            self.send_error_response(str(e))
    
    def handle_test_endpoint(self):
        """测试端点"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                "message": "测试端点正常工作",
                "status": "ok",
                "timestamp": datetime.now().isoformat()
            }
            
            response_json = json.dumps(response, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            print("✅ 测试端点响应已发送")
            
        except Exception as e:
            print(f"❌ 测试端点错误: {e}")
            self.send_error_response(str(e))
    
    def handle_create_biography(self):
        """传记创建端点"""
        try:
            # 读取请求体
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            print(f"📝 接收到创建传记请求，数据长度: {content_length}")
            
            # 模拟成功响应
            task_id = f"local-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            response = {
                "task_id": task_id,
                "status": "submitted",
                "message": "传记生成任务已提交（本地测试模式）"
            }
            
            response_json = json.dumps(response, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            print(f"✅ 传记创建响应已发送，任务ID: {task_id}")
            
        except Exception as e:
            print(f"❌ 传记创建错误: {e}")
            self.send_error_response(str(e))
    
    def handle_status_check(self, task_id):
        """状态检查端点"""
        try:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            # 模拟状态响应
            response = {
                "task_id": task_id,
                "status": "completed",
                "progress": 100,
                "message": "传记生成完成（本地测试模式）",
                "result": {
                    "content": "这是一个本地测试生成的传记内容示例...",
                    "title": "测试传记"
                }
            }
            
            response_json = json.dumps(response, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            print(f"✅ 状态检查响应已发送，任务ID: {task_id}")
            
        except Exception as e:
            print(f"❌ 状态检查错误: {e}")
            self.send_error_response(str(e))
    
    def send_404(self):
        """发送404响应"""
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {"error": "端点未找到", "path": self.path}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, error_message):
        """发送错误响应"""
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        
        response = {"error": error_message}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

def main():
    """启动本地测试服务器"""
    port = 8000
    server_address = ('', port)
    
    print(f"🚀 启动本地测试服务器...")
    print(f"📍 服务器地址: http://localhost:{port}")
    print(f"🔗 健康检查: http://localhost:{port}/api/health")
    print(f"🔗 测试端点: http://localhost:{port}/api/test")
    print(f"🔗 创建传记: http://localhost:{port}/api/biography/create")
    print(f"🔗 状态查询: http://localhost:{port}/api/biography/status/{{task_id}}")
    print(f"⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    try:
        httpd = HTTPServer(server_address, LocalTestHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        httpd.server_close()

if __name__ == '__main__':
    main()
