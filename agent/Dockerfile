# 使用Python 3.11官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p uploads output static

# 暴露端口（Zeabur通常使用8080）
EXPOSE 8080
EXPOSE 8000

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8080

# 启动命令（确保错误输出到stdout）
CMD ["python", "-u", "main.py"]
