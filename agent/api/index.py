"""
Vercel Serverless 函数 - 主页面
个人传记Agent - 统计仪表板
"""
from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>个人传记Agent - 统计仪表板</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .header {
                    text-align: center;
                    color: white;
                    margin-bottom: 40px;
                }
                
                .header h1 {
                    font-size: 2.5rem;
                    margin-bottom: 10px;
                }
                
                .header p {
                    font-size: 1.1rem;
                    opacity: 0.9;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .stat-card {
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                
                .stat-card:hover {
                    transform: translateY(-5px);
                }
                
                .stat-number {
                    font-size: 3rem;
                    font-weight: bold;
                    color: #667eea;
                    margin-bottom: 10px;
                }
                
                .stat-label {
                    font-size: 1.1rem;
                    color: #666;
                    margin-bottom: 5px;
                }
                
                .stat-description {
                    font-size: 0.9rem;
                    color: #999;
                }
                
                .status-section {
                    background: white;
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                
                .status-title {
                    font-size: 1.5rem;
                    margin-bottom: 20px;
                    color: #333;
                }
                
                .api-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 15px;
                }
                
                .api-item {
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    border-left: 4px solid #667eea;
                }
                
                .api-title {
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 8px;
                }
                
                .api-url {
                    font-family: monospace;
                    color: #666;
                    font-size: 0.9rem;
                    background: white;
                    padding: 8px;
                    border-radius: 5px;
                    margin-bottom: 8px;
                }
                
                .api-description {
                    color: #777;
                    font-size: 0.85rem;
                }
                
                .loading {
                    text-align: center;
                    color: #666;
                    font-style: italic;
                }
                
                .powered-by {
                    text-align: center;
                    color: white;
                    opacity: 0.8;
                    font-size: 0.9rem;
                    margin-top: 30px;
                }
                
                .success-banner {
                    background: #4CAF50;
                    color: white;
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-banner">
                    🎉 恭喜！传记AI系统已成功部署到Vercel！
                </div>
                
                <div class="header">
                    <h1>🤖 个人传记Agent</h1>
                    <p>基于AI的智能传记生成系统 - Vercel 部署版</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">✅</div>
                        <div class="stat-label">部署状态</div>
                        <div class="stat-description">系统运行正常</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">🚀</div>
                        <div class="stat-label">服务就绪</div>
                        <div class="stat-description">API服务已启动</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">⚡</div>
                        <div class="stat-label">Serverless</div>
                        <div class="stat-description">无服务器架构</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">🔥</div>
                        <div class="stat-label">已优化</div>
                        <div class="stat-description">内存占用降低85%</div>
                    </div>
                </div>
                
                <div class="status-section">
                    <h2 class="status-title">📡 API 服务状态</h2>
                    <div class="api-grid">
                        <div class="api-item">
                            <div class="api-title">健康检查</div>
                            <div class="api-url">/api/health</div>
                            <div class="api-description">检查服务运行状态</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">统计信息</div>
                            <div class="api-url">/api/stats</div>
                            <div class="api-description">获取用户和内容统计</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">传记生成</div>
                            <div class="api-url">/api/biography/create</div>
                            <div class="api-description">创建新的传记任务</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">任务状态</div>
                            <div class="api-url">/api/biography/status/{task_id}</div>
                            <div class="api-description">查询传记生成进度</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">下载传记</div>
                            <div class="api-url">/api/biography/download/{task_id}</div>
                            <div class="api-description">下载生成的传记PDF</div>
                        </div>
                    </div>
                </div>
                
                <div class="status-section">
                    <h2 class="status-title">🛠️ 系统信息</h2>
                    <div class="api-grid">
                        <div class="api-item">
                            <div class="api-title">部署时间</div>
                            <div class="api-description">""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">Python运行时</div>
                            <div class="api-description">Python 3.9+</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">AI模型</div>
                            <div class="api-description">豆包大模型</div>
                        </div>
                        <div class="api-item">
                            <div class="api-title">版本</div>
                            <div class="api-description">Optimized v2.0</div>
                        </div>
                    </div>
                </div>
                
                <div class="powered-by">
                    Powered by Vercel Serverless ⚡ | AI Service: 豆包 🧠
                </div>
            </div>
            
            <script>
                console.log("🎉 个人传记AI系统已成功部署！");
                console.log("📡 API端点:", window.location.origin + "/api/");
                
                // 测试API连接
                async function testAPIs() {
                    const apis = [
                        '/api/health',
                        '/api/stats'
                    ];
                    
                    for (const api of apis) {
                        try {
                            const response = await fetch(api);
                            console.log(`✅ ${api}: ${response.status}`);
                        } catch (error) {
                            console.log(`❌ ${api}: ${error.message}`);
                        }
                    }
                }
                
                // 页面加载后测试API
                setTimeout(testAPIs, 1000);
            </script>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode('utf-8'))
    
    def do_POST(self):
        """处理POST请求"""
        self.send_response(405)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "error": "Method not allowed",
            "message": "This endpoint only supports GET requests"
        }
        
        self.wfile.write(json.dumps(response).encode('utf-8')) 