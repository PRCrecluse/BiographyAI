"""
传记下载API
"""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse, parse_qs

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """下载传记文件"""
        try:
            # 解析URL参数
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            task_id = query_params.get('task_id', [None])[0]
            
            if not task_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "缺少任务ID参数"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                return
            
            # 模拟传记内容
            if task_id == "test-id":
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="biography_{task_id}.html"')
                self.end_headers()
                
                html_content = f"""
                <!DOCTYPE html>
                <html lang="zh-CN">
                <head>
                    <meta charset="UTF-8">
                    <title>个人传记 - {task_id}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #333; }}
                        .content {{ line-height: 1.6; }}
                    </style>
                </head>
                <body>
                    <h1>个人传记</h1>
                    <div class="content">
                        <p>这是一个示例传记内容。系统正在处理您的请求...</p>
                        <p>任务ID: {task_id}</p>
                        <p>生成时间: 刚刚</p>
                    </div>
                </body>
                </html>
                """
                
                self.wfile.write(html_content.encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "传记文件不存在或任务未完成"}
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": f"下载失败: {str(e)}"}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 