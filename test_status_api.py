#!/usr/bin/env python3
"""
本地测试状态API修复
验证路由和task_id提取逻辑
"""

import sys
import os
from urllib.parse import parse_qs

# 模拟Vercel路由传递的查询参数
def test_task_id_extraction(path):
    """测试task_id提取逻辑"""
    print(f"🧪 测试路径: {path}")
    
    # 从URL参数中获取task_id（Vercel路由会将路径参数转换为查询参数）
    query_params = parse_qs(path.split('?')[1]) if '?' in path else {}
    task_id = query_params.get('task_id', [None])[0]
    
    # 如果URL中没有task_id参数，尝试从路径中提取（兼容性处理）
    if not task_id:
        # 例如从 /api/biography/status/123456 提取 123456
        path_parts = path.strip('/').split('/')
        if len(path_parts) >= 1:
            task_id = path_parts[-1]
            # 移除查询参数（如果有的话）
            if '?' in task_id:
                task_id = task_id.split('?')[0]
            # 检查是否是有效的任务ID格式（避免提取到其他路径组件）
            if len(task_id) < 3 or task_id == 'status' or task_id == '':
                task_id = None
    
    print(f"✅ 提取的task_id: {task_id}")
    return task_id

def main():
    """测试不同的URL格式"""
    print("🔧 测试状态API路由修复\n")
    
    # 测试用例
    test_cases = [
        # Vercel路由传递的格式（修复后）
        "/api/biography/status.py?task_id=test-task-aa5da9b3",
        "/api/biography/status.py?task_id=test-task-f43f7806",
        
        # 原始路径格式（兼容性）
        "/api/biography/status/test-task-aa5da9b3",
        "/api/biography/status/test-task-f43f7806",
        
        # 边界情况
        "/api/biography/status/",
        "/api/biography/status",
        "/?task_id=test-task-aa5da9b3",
    ]
    
    for test_path in test_cases:
        task_id = test_task_id_extraction(test_path)
        if task_id:
            print(f"✅ 成功提取: {task_id}")
        else:
            print(f"❌ 提取失败")
        print("-" * 50)
    
    # 测试任务数据
    print("\n📊 测试任务数据:")
    tasks = {
        "test-task-aa5da9b3": {
            "status": "completed",
            "progress": 100,
            "message": "传记生成完成",
            "created_at": "2025-07-25T12:03:00",
            "image_count": 1,
            "language": "zh-CN",
            "result": {
                "content": "# 我的人生故事\n\n## 2021年的回忆\n\n在2021年的某个平凡的日子里，我正在洗澡...",
                "title": "我的个人传记 - 简单生活的美好"
            }
        }
    }
    
    test_id = "test-task-aa5da9b3"
    if test_id in tasks:
        print(f"✅ 找到任务: {test_id}")
        print(f"   状态: {tasks[test_id]['status']}")
        print(f"   进度: {tasks[test_id]['progress']}%")
        print(f"   消息: {tasks[test_id]['message']}")
    else:
        print(f"❌ 任务不存在: {test_id}")

if __name__ == "__main__":
    main()
