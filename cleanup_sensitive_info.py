#!/usr/bin/env python3
"""
Biography AI - 敏感信息清理脚本
用于清理项目中的API密钥、数据库凭据等敏感信息
"""

import os
import re
import glob

def clean_file(filepath, replacements):
    """清理单个文件中的敏感信息"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 执行替换
        for pattern, replacement in replacements.items():
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已清理: {filepath}")
            return True
        else:
            print(f"⏭️  无需清理: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ 清理失败 {filepath}: {e}")
        return False

def main():
    """主函数"""
    print("🔒 开始清理Biography AI项目中的敏感信息...")
    
    # 定义需要清理的敏感信息模式
    replacements = {
        # Supabase URL
        r'https://htrxrclxinpmbtignjoj\.supabase\.co': 'https://your-project-id.supabase.co',
        
        # Supabase Anon Key (JWT token)
        r'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh0cnhyY2x4aW5wbWJ0aWduam9qIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4MjI3MjQsImV4cCI6MjA2NDM5ODcyNH0\.25i0glZgXhlREptIxij06Hw0_tXkSj__30HcA-y3Q6s': 'your-supabase-anon-key-here',
        
        # API密钥占位符
        r'""': '""',
        r"''": "''",
        
        # 其他可能的敏感信息
        r'sk-[a-zA-Z0-9]{48}': 'your-openai-api-key-here',  # OpenAI API密钥格式
        r'Bearer [a-zA-Z0-9_-]{100,}': 'Bearer your-api-key-here',  # Bearer token
    }
    
    # 定义需要清理的文件类型
    file_patterns = [
        '**/*.py',
        '**/*.swift', 
        '**/*.js',
        '**/*.json',
        '**/*.md',
        '**/*.txt'
    ]
    
    cleaned_files = 0
    total_files = 0
    
    # 遍历所有文件
    for pattern in file_patterns:
        for filepath in glob.glob(pattern, recursive=True):
            # 跳过一些不需要清理的目录
            if any(skip in filepath for skip in ['.git/', '__pycache__/', '.DS_Store', 'node_modules/']):
                continue
                
            total_files += 1
            if clean_file(filepath, replacements):
                cleaned_files += 1
    
    print(f"\n📊 清理完成:")
    print(f"   总文件数: {total_files}")
    print(f"   已清理文件: {cleaned_files}")
    print(f"   未变更文件: {total_files - cleaned_files}")
    
    # 创建安全检查报告
    print(f"\n🔍 安全检查建议:")
    print(f"   1. 检查 .env.example 文件是否包含所有必要的环境变量")
    print(f"   2. 确保 .gitignore 文件包含所有敏感文件类型")
    print(f"   3. 在新仓库中设置环境变量")
    print(f"   4. 删除任何包含实际密钥的本地 .env 文件")

if __name__ == "__main__":
    main()
