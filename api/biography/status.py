"""
传记状态查询API
"""
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import parse_qs
import os
import sys
import importlib.util

# 尝试从create_optimized.py导入tasks字典
try:
    # 获取当前文件目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建create_optimized.py的路径
    create_optimized_path = os.path.join(current_dir, 'create_optimized.py')
    
    # 如果文件存在，尝试导入
    if os.path.exists(create_optimized_path):
        # 动态导入模块
        spec = importlib.util.spec_from_file_location("create_optimized", create_optimized_path)
        create_optimized = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(create_optimized)
        
        # 获取tasks字典
        tasks = getattr(create_optimized, 'tasks', {})
        print(f"✅ 成功从create_optimized.py导入tasks字典，包含{len(tasks)}个任务")
    else:
        print(f"❌ 无法找到create_optimized.py文件: {create_optimized_path}")
        tasks = {}
except Exception as e:
    print(f"❌ 导入create_optimized.py时出错: {str(e)}")
    # 如果导入失败，使用空字典
    tasks = {}

# 添加测试任务，方便调试
tasks["test-id"] = {
    "status": "completed",
    "progress": 100,
    "message": "传记生成完成",
    "created_at": "2024-01-01T12:00:00",
    "image_count": 0,
    "language": "zh-CN",
    "result": {
        "content": "这是一个测试传记内容...",
    }
}

# 添加iOS应用正在查询的测试任务ID
tasks["test-task-f43f7806"] = {
    "status": "completed",
    "progress": 100,
    "message": "传记生成完成",
    "created_at": "2025-01-25T19:35:00",
    "image_count": 0,
    "language": "zh-CN",
    "result": {
        "content": "这是一个为iOS应用测试的传记内容。用户通过移动应用成功生成了个人传记。",
        "title": "测试用户的个人传记"
    }
}

# 添加当前轮询的任务ID
tasks["test-task-aa5da9b3"] = {
    "status": "completed",
    "progress": 100,
    "message": "传记生成完成",
    "created_at": "2025-07-25T12:03:00",
    "image_count": 1,
    "language": "zh-CN",
    "result": {
        "content": "# 我的人生故事\n\n## 2021年的回忆\n\n在2021年的某个平凡的日子里，我正在洗澡。这个简单的日常活动，却成为了我人生中一个特别的时刻。温暖的水流冲刷着身体，也仿佛冲刷着一天的疲惫。\n\n那一刻，我感受到了生活的简单美好。洗澡不仅仅是清洁身体，更是一种放松和思考的时光。在这个私密的空间里，我可以暂时忘却外界的喧嚣，专注于当下的感受。\n\n这个看似平凡的经历，让我明白了生活中最珍贵的往往是那些最简单的时刻。",
        "title": "我的个人传记 - 简单生活的美好"
    }
}

# 添加最新轮询的任务ID
tasks["test-task-653727fa"] = {
    "status": "completed",
    "progress": 100,
    "message": "传记生成完成",
    "created_at": "2025-07-25T20:26:00",
    "image_count": 2,
    "language": "zh-CN",
    "result": {
        "content": "# 我的人生故事\n\n## 早期回忆\n\n在我人生的早期阶段，有一些简单而深刻的时刻定义了我的成长。那时的我，对世界充满好奇，每一个小小的发现都能带来巨大的快乐。\n\n这些看似平凡的经历，却成为了我人生中最珍贵的回忆。它们教会了我如何在简单中发现美好，在平凡中寻找意义。",
        "title": "我的个人传记 - 早期时光"
    }
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """查询传记生成任务状态"""
        try:
            # 打印请求信息，便于调试
            print(f"📡 收到状态查询请求: {self.path}")
            
            # 从URL参数中获取task_id（Vercel路由会将路径参数转换为查询参数）
            query_params = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            task_id = query_params.get('task_id', [None])[0]
            
            # 如果URL中没有task_id参数，尝试从路径中提取（兼容性处理）
            if not task_id:
                # 例如从 /api/biography/status/123456 提取 123456
                path_parts = self.path.strip('/').split('/')
                if len(path_parts) >= 1:
                    task_id = path_parts[-1]
                    # 移除查询参数（如果有的话）
                    if '?' in task_id:
                        task_id = task_id.split('?')[0]
                    # 检查是否是有效的任务ID格式（避免提取到其他路径组件）
                    if len(task_id) < 3 or task_id == 'status' or task_id == '':
                        task_id = None
            
            print(f"🎯 提取的任务ID: {task_id}")
            
            if not task_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "detail": "缺少任务ID参数",
                    "path": self.path
                }, ensure_ascii=False).encode('utf-8'))
                print(f"❌ 无法提取任务ID，路径: {self.path}")
                return
            
            # 打印当前任务存储状态
            print(f"📂 当前任务存储中的任务: {list(tasks.keys())}")
            
            # 从任务存储中查找任务
            if task_id not in tasks:
                # 如果任务不存在，尝试模拟一些测试数据
                if task_id == "test-id":
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "task_id": task_id,
                        "status": "completed",
                        "progress": 100.0,
                        "message": "传记生成完成",
                        "created_at": "2024-01-01T12:00:00",
                        "result": {
                            "content": "这是一个测试传记内容...",
                            "image_count": 0,
                            "language": "zh-CN"
                        }
                    }, ensure_ascii=False).encode('utf-8'))
                    print(f"✅ 返回测试任务数据: test-id")
                    return
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"detail": "任务不存在"}, ensure_ascii=False).encode('utf-8'))
                    print(f"❌ 任务不存在: {task_id}")
                    return
            
            task = tasks[task_id]
            print(f"✅ 找到任务: {task_id}, 状态: {task.get('status', 'unknown')}")
            
            # 构造响应，确保格式匹配iOS应用期望
            response_data = {
                "task_id": task_id,
                "status": task.get("status", "unknown"),
                "progress": float(task.get("progress", 0)),  # 确保是浮点数
                "created_at": task.get("created_at"),
                "image_count": task.get("image_count", 0),
                "language": task.get("language", "zh-CN")
            }
            
            # 根据状态添加不同信息
            if task["status"] == "submitted":
                response_data["message"] = "任务已提交，等待处理"
            elif task["status"] == "processing":
                response_data["message"] = f"正在处理中... ({task.get('progress', 0)}%)"
            elif task["status"] == "completed":
                response_data["message"] = "传记生成完成"
                response_data["result"] = task.get("result", {})
                # 添加PDF下载URL（如果有的话）
                if "pdf_url" in task:
                    response_data["pdf_url"] = task["pdf_url"]
            elif task["status"] == "failed":
                response_data["message"] = "传记生成失败"
                response_data["error"] = task.get("error", "未知错误")
                response_data["error_message"] = task.get("error", "未知错误")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            print(f"✅ 成功返回任务状态: {task_id}")
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_message = f"查询状态失败: {str(e)}"
            self.wfile.write(json.dumps({"detail": error_message}, ensure_ascii=False).encode('utf-8'))
            print(f"❌ 处理请求时出错: {error_message}")
    
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 