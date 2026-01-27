# ✅ Nginx 反向代理配置完成

## 🎯 架构说明

```
外部请求
  ↓
https://{hash}-3000.onetest02.olares.com/{app-path}/
  ↓
Olares Ingress Controller
  ↓
OpenCode Container
  ↓
Nginx (监听 3000 端口 - 统一入口)
  ↓ 根据 Path 路由
  ├─ /express-demo/  → express-demo-svc:3000
  ├─ /test-app/      → test-web-app-svc:8000
  └─ /api/           → test-python-api-svc:9000
```

**关键设计**：
- ✅ **统一入口**：所有请求通过 3000 端口进入
- ✅ **Path 路由**：根据 URL 路径区分不同应用
- ✅ **自动配置**：扫描 Kubernetes 部署，自动生成 Nginx 配置

---

## 📦 已部署组件

### 1. Nginx 配置
- **主配置**：`/etc/nginx/nginx.conf`
- **默认服务器**：`/etc/nginx/conf.d/default.conf`（监听 3000）
- **应用代理配置**：`/etc/nginx/conf.d/dev/*.conf`（自动生成）

### 2. 自动化工具
- **配置生成器**：`/root/.local/bin/olares-nginx-config`

---

## 🚀 使用方法

### 自动生成所有应用的代理配置
```bash
python3 /root/.local/bin/olares-nginx-config
```

输出示例：
```
Olares Nginx 配置生成器
============================================================

1. 扫描已部署的应用...
  找到 4 个应用:
    - express-demo (端口 3000)
    - flask-hello (端口 5000)
    - test-python-api (端口 9000)
    - test-web-app (端口 8000)

2. 生成 Nginx 配置...
✓ 生成配置: /etc/nginx/conf.d/dev/express-demo.conf
✓ 生成配置: /etc/nginx/conf.d/dev/flask-hello.conf
✓ 生成配置: /etc/nginx/conf.d/dev/test-python-api.conf
✓ 生成配置: /etc/nginx/conf.d/dev/test-web-app.conf

3. 应用配置...
✓ Nginx 配置测试通过
✓ Nginx 重载成功

✅ 配置完成！
```

### 查看 Nginx 状态
```bash
python3 /root/.local/bin/olares-nginx-config status
```

### 手动重载 Nginx
```bash
nginx -s reload
```

### 查看生成的配置
```bash
cat /etc/nginx/conf.d/dev/express-demo.conf
```

---

## 🌐 访问应用

### 通过应用名称访问
```
http://localhost:3000/express-demo/
http://localhost:3000/test-app/
http://localhost:3000/api-service/
```

### 通过端口号访问
```
http://localhost:3000/3000/  → express-demo
http://localhost:3000/8000/  → test-web-app
http://localhost:3000/9000/  → test-python-api
```

### 外部访问（通过 Olares Ingress）
```
https://{hash}-3000.onetest02.olares.com/express-demo/
https://{hash}-3000.onetest02.olares.com/test-app/
```

---

## 📝 配置示例

### 生成的 Nginx 配置结构
```nginx
# /etc/nginx/conf.d/dev/express-demo.conf

# 通过应用名访问
location /express-demo/ {
    proxy_pass http://express-demo-svc.opencode-dev-onetest02.svc.cluster.local:3000/;
    proxy_http_version 1.1;
    
    # 标准代理头
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket 支持（对 code-server 等应用很重要）
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    
    # 超时设置（支持长连接）
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # 禁用缓冲（支持实时响应）
    proxy_buffering off;
    proxy_request_buffering off;
}

# 通过端口号访问
location /3000/ {
    proxy_pass http://express-demo-svc.opencode-dev-onetest02.svc.cluster.local:3000/;
    # ... 相同配置
}
```

---

## 🔧 集成到部署流程

### 方式 1：手动集成
每次部署新应用后运行：
```bash
python3 /root/.local/bin/olares-nginx-config
```

### 方式 2：自动集成
修改 `/root/.local/bin/olares-deploy` 脚本，在部署成功后自动运行配置生成器。

添加到脚本末尾：
```bash
# 自动更新 Nginx 配置
if [ -f /root/.local/bin/olares-nginx-config ]; then
    echo ""
    log_step "更新 Nginx 反向代理配置..."
    python3 /root/.local/bin/olares-nginx-config > /dev/null 2>&1 || true
fi
```

---

## ✅ 验证测试

### 1. 测试健康检查
```bash
curl http://localhost:3000/health
# 预期输出: healthy
```

### 2. 测试应用代理
```bash
# Express 应用
curl http://localhost:3000/express-demo/
# 预期输出: <h1>Express Demo</h1>

# Python 应用
curl http://localhost:3000/8000/
# 预期输出: HTML directory listing or app response
```

### 3. 检查 Nginx 进程
```bash
ps aux | grep nginx
# 预期: 看到 master 和多个 worker 进程
```

### 4. 检查监听端口
```bash
ss -tlnp | grep :3000
# 预期: Nginx 监听在 3000 端口
```

---

## 🐛 故障排查

### Nginx 未启动
```bash
# 检查配置
nginx -t

# 启动 Nginx
nginx

# 查看错误日志
tail -f /tmp/nginx-error.log
```

### 应用代理 502 错误
1. 检查应用 Pod 是否运行：
   ```bash
   /tmp/kubectl get pods -n opencode-dev-onetest02 -l app=express-demo
   ```

2. 检查 Service 是否存在：
   ```bash
   /tmp/kubectl get svc -n opencode-dev-onetest02
   ```

3. 测试 Service 连接：
   ```bash
   curl http://express-demo-svc.opencode-dev-onetest02.svc.cluster.local:3000
   ```

### 配置未生效
```bash
# 重新生成并重载
python3 /root/.local/bin/olares-nginx-config

# 或手动重载
nginx -s reload
```

---

## 📊 端口分配

| 端口 | 服务 | 说明 |
|------|------|------|
| 3000 | Nginx | **统一入口** - 所有外部请求通过这里 |
| 5000 | code-server | VS Code IDE 界面 |
| 8000 | OpenCode AI | AI 辅助编程服务 |
| 其他 | 应用 Pods | 通过 Kubernetes Service 访问 |

---

## 🎉 完成状态

✅ Nginx 已启动并监听 3000 端口  
✅ 自动配置生成器已部署  
✅ 为所有已部署应用生成了代理配置  
✅ 支持 WebSocket（对 code-server 等重要）  
✅ 支持长连接和实时响应  
✅ 内部测试通过  

### 待验证
⏳ 外部访问测试（需要通过浏览器访问 Olares URL）

---

## 📚 相关文档

- 部署脚本：`/root/.local/bin/olares-deploy`
- 配置生成器：`/root/.local/bin/olares-nginx-config`
- Nginx 主配置：`/etc/nginx/nginx.conf`
- Olares 开发技能：`/root/.config/opencode/skills/olares-dev.md`
