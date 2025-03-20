# YouTube下载器项目部署指南

这是一个基于FastAPI的YouTube视频下载器，支持Docker部署和HTTPS。

## 部署到搬瓦工并绑定域名

### 1. 准备工作

- 一个搬瓦工VPS实例，已安装Docker和Docker Compose
- 已注册的域名（例如：www.ytdlonline.org）
- 域名的SSL证书文件

### 2. 将代码上传到服务器

```bash
# 连接到服务器
ssh username@your-server-ip

# 创建项目目录
mkdir -p /root/ytdler
cd /root/ytdler

# 上传项目文件或使用Git克隆
# 方法1：使用SCP上传
# 在本地执行：
scp -r /path/to/ytdler/* username@your-server-ip:/root/ytdler/

# 方法2：使用Git
git clone https://your-git-repo-url.git /root/ytdler
```

### 3. 准备SSL证书

```bash
# 创建SSL证书目录
mkdir -p /root/ytdler/nginx/ssl

# 上传SSL证书到服务器
# 在本地执行：
scp /path/to/cert.pem username@your-server-ip:/root/ytdler/nginx/ssl/
scp /path/to/key.pem username@your-server-ip:/root/ytdler/nginx/ssl/
```

### 4. 创建数据目录

```bash
mkdir -p /root/ytdler/downloads
touch /root/ytdler/notes.json
```

### 5. 配置域名DNS解析

1. 登录域名管理平台
2. 添加A记录：`www.ytdlonline.org` 指向搬瓦工服务器IP地址

### 6. 启动Docker容器

```bash
cd /root/ytdler
docker-compose up -d --build
```

### 7. 查看日志

```bash
docker-compose logs -f
```

### 8. 更新应用

```bash
cd /root/ytdler
git pull  # 如果使用Git
docker-compose down
docker-compose up -d --build
```

## 常见问题

### 无法访问网站

- 检查搬瓦工防火墙设置，确保开放80和443端口
- 验证域名DNS是否已正确解析到服务器IP

### SSL证书问题

- 确认证书文件格式正确（PEM格式）
- 检查证书路径是否正确：`/root/ytdler/nginx/ssl/cert.pem`和`/root/ytdler/nginx/ssl/key.pem`

### 无法下载视频

- 检查Docker日志：`docker-compose logs ytdler`
- 可能需要更新yt-dlp：
  ```bash
  docker-compose exec ytdler pip install --upgrade yt-dlp
  docker-compose restart ytdler
  ```

## 安全建议

- 定期更新Docker镜像和依赖
- 设置访问限制（可以在Nginx配置中添加）
- 考虑添加基本身份验证 