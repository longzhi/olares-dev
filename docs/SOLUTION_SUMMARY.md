# 🎉 Olares 应用外部访问解决方案 - 完成

## 问题回顾

**原始问题**：
- 应用部署后，内部可访问（集群内 curl 成功）
- 外部浏览器访问返回 HTTP 421 错误
- 所有外部 URL 都重定向到同一个固定页面

**根本原因**：
OpenCode 容器需要一个**反向代理机制**来将外部请求（通过 3000 端口进入）转发到不同的 Kubernetes Service。

---

## ✅ 实施的解决方案

### 架构设计

```
外部浏览器
  ↓ HTTPS
https://b0c54349-3000.onetest02.olares.com/{app-path}/
  ↓
Olares Ingress Controller (TLS termination)
  ↓ HTTP
OpenCode Container (opencode-dev pod)
  ↓
Nginx 反向代理 (监听 3000 端口)
  ↓ 根据 Path 路由到不同的 Service
  ├─ /express-demo/  → express-demo-svc:3000
  ├─ /test-app/      → test-web-app-svc:8000  
  └─ /api/           → test-python-api-svc:9000
  ↓
Kubernetes Service (ClusterIP, load balancing)
  ↓
Application Pod
```

### 核心原理

**统一入口 + Path 路由**：
1. OpenCode 默认开放 3000 端口作为统一入口
2. 所有外部请求通过 3000 端口进入 OpenCode 容器
3. Nginx 监听 3000 端口，根据 URL Path 分发请求
4. 不同的 Path 映射到不同的内部 Kubernetes Service
5. Service 将请求转发到对应的 Pod

---

## 🛠️ 实施步骤

### 1. 修复 Nginx 配置
- 修改日志路径为 `/tmp/nginx-*.log`（容器环境兼容）
- 更改运行用户为 `root`
- 配置 Nginx 监听 **3000 端口**（而不是 8080）

**文件**：`/etc/nginx/nginx.conf`, `/etc/nginx/conf.d/default.conf`

### 2. 创建自动配置生成器
创建 Python 脚本自动化配置管理：

**文件**：`/root/.local/bin/olares-nginx-config`

**功能**：
- 自动扫描所有已部署的应用（通过 kubectl）
- 为每个应用生成 Nginx 反向代理配置
- 两种路由规则：
  - 应用名：`/app-name/` → Service
  - 端口号：`/port/` → Service
- 自动重载 Nginx（graceful reload，零停机）

### 3. 启动 Nginx
```bash
python3 /root/.local/bin/olares-nginx-config
```

结果：
- ✅ Nginx 成功启动
- ✅ 监听 3000 端口（替换原有占用的服务）
- ✅ 为 4 个应用生成了代理配置

### 4. 验证内部访问
```bash
$ curl http://localhost:3000/express-demo/
<h1>Express Demo</h1><p>onetest02.olares.com</p>

$ curl http://localhost:3000/health
healthy
```

✅ **内部测试成功！**

---

## 🌐 外部访问 URL

### OpenCode 统一入口
```
https://b0c54349-3000.onetest02.olares.com
```

### 应用访问路径

#### 通过应用名访问（推荐）
```
https://b0c54349-3000.onetest02.olares.com/express-demo/
https://b0c54349-3000.onetest02.olares.com/test-app/
https://b0c54349-3000.onetest02.olares.com/api/
```

#### 通过端口号访问
```
https://b0c54349-3000.onetest02.olares.com/3000/  → express-demo
https://b0c54349-3000.onetest02.olares.com/8000/  → test-web-app
https://b0c54349-3000.onetest02.olares.com/9000/  → api service
```

#### 健康检查
```
https://b0c54349-3000.onetest02.olares.com/health
```

---

## 📦 已部署的文件和工具

### 配置文件
- `/etc/nginx/nginx.conf` - Nginx 主配置
- `/etc/nginx/conf.d/default.conf` - 监听 3000 端口的默认服务器
- `/etc/nginx/conf.d/dev/*.conf` - 自动生成的应用代理配置

### 自动化工具
- `/root/.local/bin/olares-nginx-config` - 配置生成器（Python）
- `/root/.local/bin/olares-deploy` - 应用部署脚本
- `/root/.local/bin/olares-manage` - 应用管理工具
- `/root/.local/bin/olares-urls` - URL 查看工具

### 文档
- `/root/NGINX_PROXY_COMPLETE.md` - 详细使用文档
- `/root/NGINX_PROXY_STATUS.md` - 实施过程记录
- `/root/SOLUTION_SUMMARY.md` - 本文档

---

## 🚀 使用流程

### 部署新应用后更新代理
```bash
# 1. 部署应用
/root/.local/bin/olares-deploy my-app python:3.11-slim 5000 "python app.py"

# 2. 自动生成 Nginx 配置
python3 /root/.local/bin/olares-nginx-config

# 3. 访问应用
https://b0c54349-3000.onetest02.olares.com/my-app/
```

### 查看所有应用的 URL
```bash
/root/.local/bin/olares-urls
```

### 检查 Nginx 状态
```bash
python3 /root/.local/bin/olares-nginx-config status
```

---

## 🎯 关键技术点

### 1. 为什么是 3000 端口？
- OpenCode 容器安装时默认开放 3000 端口
- Olares Ingress Controller 已配置将外部请求路由到 `{hash}-3000.domain`
- 所有外部流量统一从 3000 端口进入
- 无需修改 OpenCode 部署的 `studio-expose-ports` 注解
- 避免了 Pod 重启的风险

### 2. Path 路由 vs 端口路由
**之前的错误理解**：每个应用需要独立的端口（3000, 5000, 8000, 9000）

**正确的架构**：统一入口 + Path 区分
- 所有请求 → 3000 端口
- 通过 URL Path 区分应用
- Nginx 根据 Path 转发到不同的 Kubernetes Service

### 3. Kubernetes Service Discovery
Nginx 使用 Kubernetes 内部 DNS：
```nginx
proxy_pass http://app-name-svc.namespace.svc.cluster.local:port/;
```

优点：
- 无需硬编码 IP 地址
- 自动负载均衡
- 高可用性（Service 会自动更新 Endpoints）

### 4. WebSocket 支持
配置中包含 WebSocket 支持：
```nginx
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $http_connection;
```

重要性：
- code-server 需要 WebSocket
- 实时应用（聊天、通知）需要 WebSocket
- 长连接支持

---

## 📊 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| Nginx | ✅ 运行中 | 监听 3000 端口，24 个 worker 进程 |
| 配置生成器 | ✅ 已部署 | 自动扫描并生成配置 |
| 代理配置 | ✅ 已生成 | 4 个应用的配置文件 |
| 内部访问 | ✅ 测试通过 | curl localhost:3000 工作正常 |
| 外部访问 | ⏳ 待验证 | 需要通过浏览器测试 |

---

## ✅ 验证清单

请在浏览器中测试以下 URL：

- [ ] https://b0c54349-3000.onetest02.olares.com/health
  - 预期：显示 "healthy"
  
- [ ] https://b0c54349-3000.onetest02.olares.com/express-demo/
  - 预期：显示 Express Demo 页面
  
- [ ] https://b0c54349-3000.onetest02.olares.com/test-app/
  - 预期：显示应用内容或目录列表
  
- [ ] https://b0c54349-3000.onetest02.olares.com/3000/
  - 预期：与 /express-demo/ 相同的内容

---

## 🎓 经验总结

### 成功的关键
1. **理解 Olares 的网络架构** - 统一入口而非多端口
2. **利用现有基础设施** - 使用已开放的 3000 端口
3. **自动化配置管理** - Python 脚本动态生成配置
4. **零停机部署** - Nginx graceful reload

### 技术亮点
- Kubernetes Service Discovery（无需硬编码 IP）
- 动态配置生成（适应应用变化）
- WebSocket 支持（兼容更多应用场景）
- 健康检查端点（便于监控）

### 避免的陷阱
- ❌ 尝试为每个应用开放独立端口
- ❌ 修改 studio-expose-ports 导致 Pod 重启
- ❌ 硬编码 Service IP 地址
- ❌ 忽略 WebSocket 支持

---

## 📞 需要帮助？

### 故障排查
参考：`/root/NGINX_PROXY_COMPLETE.md` 的故障排查章节

### 重新生成配置
```bash
python3 /root/.local/bin/olares-nginx-config
```

### 查看 Nginx 日志
```bash
tail -f /tmp/nginx-error.log
tail -f /tmp/nginx-access.log
```

### 检查应用状态
```bash
/tmp/kubectl get pods -n opencode-dev-onetest02
/tmp/kubectl get svc -n opencode-dev-onetest02
```

---

## 🎉 结论

通过在 OpenCode 容器内配置 Nginx 反向代理，我们成功实现了：

✅ **统一入口** - 所有应用通过 3000 端口访问  
✅ **Path 路由** - 灵活的 URL 路径映射  
✅ **自动化** - 一键生成和更新配置  
✅ **零停机** - 无需重启 OpenCode Pod  
✅ **可扩展** - 轻松添加新应用  

**外部访问 URL**：
```
https://b0c54349-3000.onetest02.olares.com/{app-name}/
```

**下一步**：在浏览器中测试验证外部访问！
