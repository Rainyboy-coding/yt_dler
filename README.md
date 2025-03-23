# YouTube 下载器项目部署指南

这是一个基于 FastAPI 的 YouTube 视频下载器，支持直接部署到 VPS 并配置 HTTPS。

## 部署到搬瓦工并绑定域名

### 1. 准备工作

- 一个搬瓦工 VPS 实例，已安装 Python 3.8+和 Nginx
- 已注册的域名（例如：www.ytdlonline.org）
- 域名的 SSL 证书文件

### 2. 将代码上传到服务器

```bash
# 连接到服务器
ssh username@your-server-ip

# 创建项目目录
mkdir -p /var/www/ytdler
cd /var/www/ytdler

# 上传项目文件或使用Git克隆
# 方法1：使用SCP上传
# 在本地执行：
scp -r /path/to/ytdler/* username@your-server-ip:/var/www/ytdler/

# 方法2：使用Git
git clone https://your-git-repo-url.git /var/www/ytdler
```

### 3. 安装依赖

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装必要的系统依赖
sudo apt install python3 python3-pip python3-venv nginx ffmpeg -y

# 创建并激活虚拟环境
cd /var/www/ytdler
python3 -m venv venv
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 4. 准备 SSL 证书

```bash
# 创建SSL证书目录
sudo mkdir -p /etc/nginx/ssl

# 上传SSL证书到服务器
# 在本地执行：
scp /path/to/cert.pem username@your-server-ip:/etc/nginx/ssl/
scp /path/to/key.pem username@your-server-ip:/etc/nginx/ssl/
```

### 5. 配置 Nginx

```bash
# 创建Nginx配置文件
sudo nano /etc/nginx/sites-available/ytdler

# 添加以下内容：
# server {
#     listen 80;
#     server_name www.ytdlonline.org;
#
#     # 重定向到HTTPS
#     return 301 https://$host$request_uri;
# }
#
# server {
#     listen 443 ssl;
#     server_name www.ytdlonline.org;
#
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#
#     location /static {
#         alias /var/www/ytdler/static/;
#     }
#
#     location / {
#         proxy_pass http://127.0.0.1:8000;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
# }

# 启用配置文件
sudo ln -s /etc/nginx/sites-available/ytdler /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 6. 创建数据目录

```bash
mkdir -p /var/www/ytdler/downloads
touch /var/www/ytdler/notes.json
echo "{}" > /var/www/ytdler/notes.json
sudo chown -R www-data:www-data /var/www/ytdler/downloads
sudo chown www-data:www-data /var/www/ytdler/notes.json
```

### 7. 配置系统服务

```bash
# 创建系统服务文件
sudo nano /etc/systemd/system/ytdler.service

# 添加以下内容：
# [Unit]
# Description=YouTube Downloader Application
# After=network.target
#
# [Service]
# User=www-data
# WorkingDirectory=/var/www/ytdler
# ExecStart=/var/www/ytdler/venv/bin/python main.py
# Restart=always
#
# [Install]
# WantedBy=multi-user.target

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable ytdler
sudo systemctl start ytdler
```

### 8. 配置域名 DNS 解析

1. 登录域名管理平台
2. 添加 A 记录：`www.ytdlonline.org` 指向搬瓦工服务器 IP 地址

### 9. 配置防火墙

```bash
sudo ufw allow 80
sudo ufw allow 443
```

### 10. 查看服务状态

```bash
sudo systemctl status ytdler
sudo journalctl -u ytdler -f
```

### 11. 更新应用

```bash
cd /var/www/ytdler
git pull  # 如果使用Git
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ytdler
```

## 常见问题

### 无法访问网站

- 检查搬瓦工防火墙设置，确保开放 80 和 443 端口
- 验证域名 DNS 是否已正确解析到服务器 IP
- 检查 Nginx 配置：`sudo nginx -t`

### SSL 证书问题

- 确认证书文件格式正确（PEM 格式）
- 检查证书路径是否正确：`/etc/nginx/ssl/cert.pem`和`/etc/nginx/ssl/key.pem`

### 无法下载视频

- 检查服务日志：`sudo journalctl -u ytdler -f`
- 可能需要更新 yt-dlp：
  ```bash
  source /var/www/ytdler/venv/bin/activate
  pip install --upgrade yt-dlp
  sudo systemctl restart ytdler
  ```

### 权限问题

- 确保应用目录权限正确：`sudo chown -R www-data:www-data /var/www/ytdler`
- 确保日志和下载目录可写：`sudo chmod -R 755 /var/www/ytdler/downloads`

## 安全建议

- 定期更新系统和依赖
- 设置访问限制（可以在 Nginx 配置中添加）
- 考虑添加基本身份验证
