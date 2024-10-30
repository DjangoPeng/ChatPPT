# 域名和反向代理设置说明文档

本文档为域名配置、SSL 证书生成、安装及 Nginx 反向代理设置提供详细指导，以便为网站启用 HTTPS 安全访问。

---

## 1. 域名 A 记录配置

### 1.1 登录域名提供商

1. 使用您的域名服务商（如 Hexonet、阿里云、腾讯云等）提供的管理界面。
2. 找到域名管理区域，选择您要配置的域名。

### 1.2 添加 A 记录

1. 进入 DNS 管理页面。
2. 创建一条新的 **A 记录**，详细配置如下：
   - **主机记录**：`@`（表示主域名）或 `subdomain`（如果使用子域名）。
   - **记录类型**：A 记录
   - **记录值**：您的服务器公网 IP 地址（例如 `123.45.67.89`）。
   - **TTL**：选择默认值，通常为 `600` 秒。

3. **保存配置**。等待 DNS 记录的传播，通常需要几分钟，但可能最长达 24 小时。

---

## 2. 安装并配置 SSL 证书

### 2.1 安装 Certbot

Certbot 是 Let’s Encrypt 提供的免费 SSL 证书工具。首先在您的服务器上安装 Certbot 和 Nginx 插件：

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx -y
```

### 2.2 生成 SSL 证书

运行以下命令，为域名（或子域名）生成 SSL 证书。以 `example.com` 为例：

```bash
sudo certbot --nginx -d example.com
```

### 2.3 配置自动重定向到 HTTPS

Certbot 会询问您是否需要将 HTTP 重定向到 HTTPS。选择 `2` 进行自动重定向配置：

```plaintext
1: No redirect
2: Redirect - Make all requests redirect to secure HTTPS access.
```

### 2.4 验证证书安装

在浏览器中访问 `https://example.com`，查看是否显示安全锁标志，表示证书安装成功。

---

## 3. Nginx 反向代理设置

以下是使用 Nginx 反向代理的详细配置过程，确保所有 HTTP 请求自动重定向到 HTTPS，并通过 SSL 加密的 Nginx 代理将请求转发到后端服务。

### 3.1 配置 Nginx

1. 编辑或创建 Nginx 配置文件（例如 `/etc/nginx/sites-available/example.com`）：

   ```bash
   sudo nano /etc/nginx/sites-available/example.com
   ```

2. 将以下内容添加到配置文件中：

   ```nginx
   # HTTP 到 HTTPS 的重定向
   server {
       listen 80;
       server_name example.com;

       # 重定向所有 HTTP 请求到 HTTPS
       return 301 https://$host$request_uri;
   }

   # HTTPS 服务器配置
   server {
       listen 443 ssl;
       server_name example.com;

       # SSL 证书路径
       ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;    # Certbot 自动生成
       ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;  # Certbot 自动生成

       # 启用 TLS 协议
       ssl_protocols TLSv1.2 TLSv1.3;

       # 配置加密套件
       ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305";
       ssl_prefer_server_ciphers off;

       # 其他 SSL 配置
       ssl_ecdh_curve X25519:P-256:P-384:P-521;
       ssl_session_cache shared:SSL:50m;
       ssl_session_timeout 10m;

       # 上传文件大小限制
       client_max_body_size 50M;

       location / {
           proxy_pass http://127.0.0.1:7860;  # 后端服务地址，示例中使用本地 7860 端口
           proxy_http_version 1.1;

           # WebSocket 支持
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";

           # 转发客户端请求头
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **启用站点并重启 Nginx**

   创建一个符号链接启用站点配置，并重启 Nginx：

   ```bash
   sudo ln -s /etc/nginx/sites-available/example.com /etc/nginx/sites-enabled/
   sudo nginx -t  # 测试配置是否正确
   sudo systemctl restart nginx  # 重启 Nginx
   ```

### 3.2 测试反向代理

1. 通过 `https://example.com` 访问网站。
2. 验证 HTTP 请求自动重定向到 HTTPS，页面显示安全锁标志，且内容正常加载。

---

## 4. 定期更新和维护

Let’s Encrypt 证书有效期为 90 天，Certbot 会自动创建续订任务。您可以手动测试自动续订：

```bash
sudo certbot renew --dry-run
```

---

## 示例测试和故障排除

- **SSL 测试**：访问 [SSL Labs](https://www.ssllabs.com/ssltest/)，输入您的域名进行 SSL 配置检查。
- **日志查看**：在 `/var/log/nginx/error.log` 中查找 Nginx 错误日志，帮助诊断 SSL、代理和连接问题。

---

### 注意事项
1. 确保您的域名 DNS 设置已正确生效，访问域名时指向服务器 IP。
2. 定期检查和维护 Nginx 与 Certbot 版本，以确保安全性和兼容性。

--- 

以上步骤完成后，您的域名将通过 Nginx 反向代理为后端服务提供 HTTPS 安全访问。


## 补充：Nginx 配置详细说明

以下是 Nginx 配置模板，将特定项替换为通用变量，并包含详细注释说明：

```nginx
# 配置 HTTP 到 HTTPS 重定向
server {
    listen 80;
    server_name example.com;  # 将此替换为您的域名，例如 example.com

    # 将所有 HTTP 请求重定向到 HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name example.com;  # 将此替换为您的域名

    # 配置 SSL 证书路径（替换为您的证书路径）
    ssl_certificate /path/to/ssl/fullchain.pem;    # 例如 /etc/letsencrypt/live/example.com/fullchain.pem
    ssl_certificate_key /path/to/ssl/privkey.pem;  # 例如 /etc/letsencrypt/live/example.com/privkey.pem

    # 允许的 TLS 协议版本
    ssl_protocols TLSv1.2 TLSv1.3;

    # 兼容 TLS 1.3 的加密套件
    ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305";
    ssl_prefer_server_ciphers off;

    # 其他 SSL 配置
    ssl_ecdh_curve X25519:P-256:P-384:P-521;
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 10m;

    # 设置最大上传文件大小限制
    client_max_body_size 50M;

    # 代理到后端服务（例如 Gradio 的 HTTP 服务）
    location / {
        proxy_pass http://127.0.0.1:7860;  # 将流量转发到本地运行在端口 7860 的 HTTP 服务
        proxy_http_version 1.1;

        # WebSocket 支持
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 转发客户端请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 配置项注释说明

- **server_name**：设置服务器名称，通常为域名。将 `example.com` 替换为您自己的域名。
- **ssl_certificate** 和 **ssl_certificate_key**：SSL 证书文件路径，指向 HTTPS 所需的证书和私钥文件。替换为实际证书路径。
- **ssl_protocols**：允许的 TLS 协议版本。这里设置为只允许较新的 TLS 1.2 和 TLS 1.3。
- **ssl_ciphers**：定义了服务器支持的加密套件，确保符合 TLS 1.3 要求并与常用浏览器兼容。
- **ssl_prefer_server_ciphers**：设置为 `off`，让客户端选择其首选的加密套件。
- **ssl_ecdh_curve**：定义服务器支持的椭圆曲线，用于 ECDH 密钥交换。
- **client_max_body_size**：设置上传文件的大小限制，确保上传较大文件时不被拒绝。
- **proxy_pass**：指向后端服务的 URL，在本例中是本地运行在 `127.0.0.1:7860` 的服务（如 Gradio）。
- **proxy_set_header**：设置必要的请求头以支持 WebSocket 和客户端 IP 转发。

### 示例

假设域名为 `myapp.example.com`，证书路径位于 `/etc/letsencrypt/live/myapp.example.com/`，则配置为：

```nginx
server {
    listen 80;
    server_name myapp.example.com;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name myapp.example.com;

    ssl_certificate /etc/letsencrypt/live/myapp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/myapp.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers "ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305";
    ssl_prefer_server_ciphers off;

    ssl_ecdh_curve X25519:P-256:P-384:P-521;
    ssl_session_cache shared:SSL:50m;
    ssl_session_timeout 10m;

    client_max_body_size 50M;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```