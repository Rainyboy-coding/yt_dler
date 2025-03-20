FROM python:3.9-slim

WORKDIR /app

# 安装ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY requirements.txt .
COPY main.py .
COPY /templates ./templates
COPY /static ./static

# 创建下载目录
RUN mkdir -p downloads

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 