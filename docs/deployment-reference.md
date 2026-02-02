# 部署参考文档

> 这是详细参考文档。核心流程见主 SKILL.md

## 部署工具

| 工具 | 路径 | 用途 |
|------|------|------|
| `olares-deploy` | `/root/.local/bin/olares-deploy` | 部署应用 |
| `olares-manage` | `/root/.local/bin/olares-manage` | 管理应用 |
| `olares-urls` | `/root/.local/bin/olares-urls` | 显示所有 URL |
| `olares-nginx-config` | `/root/.local/bin/olares-nginx-config` | 更新 Nginx 配置 |

## olares-deploy 用法

```bash
olares-deploy <app-name> <image> <port> [startup-command]

# 示例
olares-deploy todo-app python:3.11-slim 8080 "pip install flask && python app.py"
olares-deploy my-api node:20-slim 3000 "npm install && npm start"
```

## olares-manage 用法

```bash
# 列出所有应用
olares-manage list

# 查看应用详情
olares-manage info <app-name>

# 查看日志
olares-manage logs <app-name>
olares-manage logs <app-name> -f  # 实时跟踪

# 测试连接
olares-manage test <app-name>

# 删除应用
olares-manage delete <app-name>
```

## 网络架构

```
用户浏览器
    ↓ HTTPS
https://8cf849020.{username}.olares.com/{app-name}/
    ↓
Olares Ingress → OpenCode Container:3000
    ↓
Nginx 反向代理
    ↓
    ├─ /           → localhost:4096 (OpenCode Server)
    ├─ /todo-app/  → todo-app-svc:8080
    └─ /my-api/    → my-api-svc:3000
```

## URL 格式

```
https://{appid}.{username}.olares.com/{app-path}/

示例：
https://8cf849020.onetest02.olares.com/todo-app/
```

AppID 计算规则：
- `md5("mymas")[:8]` = `8cf84902`
- 第一个入口 (index 0) → `8cf849020`

## Nginx 配置

部署后必须更新 Nginx：

```bash
python3 /root/.local/bin/olares-nginx-config
```

生成的配置文件位于 `/etc/nginx/conf.d/dev/`

## 完整部署流程

```bash
# 1. 部署应用
olares-deploy my-app python:3.11-slim 8080 "python app.py"

# 2. 更新 Nginx（必须）
python3 /root/.local/bin/olares-nginx-config

# 3. 访问应用
# https://8cf849020.{username}.olares.com/my-app/
```

## 前端 API 路径配置

部署路径带前缀时，前端必须配置 baseURL：

```javascript
// src/api.js
const api = axios.create({
  baseURL: '/my-app/api',  // 包含部署路径前缀
});
```

```javascript
// vite.config.js
export default defineConfig({
  base: '/my-app/',
});
```

## 故障排查

### 502 Bad Gateway
```bash
# 检查 Pod 是否运行
kubectl get pods -n $NAMESPACE -l app=my-app

# 检查 Service
kubectl get svc -n $NAMESPACE my-app-svc
```

### 404 Not Found
```bash
# 检查 Nginx 配置是否存在
ls /etc/nginx/conf.d/dev/my-app.conf

# 重新生成配置
python3 /root/.local/bin/olares-nginx-config
```

### 应用无法外部访问
```bash
# 检查入口端口配置（应为 3000）
kubectl get deployment -n $NAMESPACE -o jsonpath='{.metadata.annotations}'
```

## ConfigMap 部署代码

由于 hostPath 无法跨节点访问，使用 ConfigMap 存储代码：

```bash
# 创建 ConfigMap
kubectl create configmap myapp-code -n $NAMESPACE \
  --from-file=app.py=/root/workspace/myapp/app.py \
  --from-file=index.html=/root/workspace/myapp/static/index.html
```

在 deployment 中挂载：

```yaml
spec:
  containers:
  - name: myapp
    volumeMounts:
    - name: code
      mountPath: /code
    command: ["/bin/sh", "-c"]
    args:
      - |
        cp /code/* /app/
        cd /app && python app.py
  volumes:
  - name: code
    configMap:
      name: myapp-code
```
