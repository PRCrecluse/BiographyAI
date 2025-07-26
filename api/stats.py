"""
统计信息API
"""
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """获取统计信息"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 模拟统计数据
        stats = {
            "total_users": 1234,
            "active_users_30d": 456,
            "recent_users_7d": 89,
            "total_notes": 5678,
            "total_business_cards": 234,
            "total_biographies": 89,
            "successful_generations": 67,
            "avg_processing_time": "45s",
            "last_updated": datetime.now().isoformat(),
            "platform": "Vercel",
            "status": "healthy",
            "version": "2.0-optimized"
        }
        
        self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 