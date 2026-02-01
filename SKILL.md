---
name: olares-dev
description: "MUST USE when user asks to develop/create/build any application. Triggers: 开发/制作/创建/做一个/写一个/帮我做/帮我开发/build/create/make/develop/implement/code an app"
license: MIT
---

# Olares Development Skill

**在 Olares 平台上开发和部署应用的规范。**

---

## ⛔ 三条铁律（违反即失败）

在执行任何开发任务时，你 **必须** 遵守以下规则：

| # | 规则 | 正确做法 | 违规行为（= 你失败了） |
|---|------|----------|----------------------|
| 1 | **开发完 → 问发布** | 回复必须以发布提示结尾（见下方模板） | 省略发布提示、用"有问题告诉我"结尾 |
| 2 | **数据库 → PostgreSQL** | 需要持久化时直接用 PostgreSQL | 问用户选什么数据库、推荐 SQLite |
| 3 | **目录 → 固定位置** | 项目放 `/root/workspace/<app-name>/` | 问用户想放哪个目录 |

### 发布提示模板（规则1）

开发完成后，你的回复 **必须** 以这个格式结尾：

```
---
## ✅ 开发完成！

📁 项目位置：`/root/workspace/<app-name>/`

**发布到 Olares？** 回复 "publish" 一键部署。
```

### PostgreSQL 连接方式（规则2）

```python
import os
conn = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT', '5432'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD'),
    database=os.environ.get('DB_DATABASE')
)
```

---

## 🎯 触发词

### 开发触发词（加载此 skill）

- **中文**：制作 / 开发 / 创建 / 做一个 / 写一个 / 帮我做 / 帮我写 / 帮我开发 / 实现 / 编写
- **English**: build / create / make / develop / help me build / help me create / implement / code

### 发布触发词（执行部署）

用户说以下词时，**立即执行部署**：
- 发布 / publish / 好 / 可以 / OK / yes / 确认 / go / 上线 / deploy / ship it / release

---

## 📐 开发工作流

```
用户请求开发
    ↓
创建项目: /root/workspace/<app-name>/  ← 不要问目录
    ↓
需要数据库？→ 直接用 PostgreSQL  ← 不要问选择
    ↓
编写完整可运行的代码
    ↓
回复以发布提示结尾  ← 必须！
    ↓
用户确认 → 执行部署
```

---

## 🚀 部署命令

```bash
# 格式
olares-deploy <app-name> <image> <port> [startup-command]

# 示例
olares-deploy todo-app python:3.11-slim 8080 "pip install -r requirements.txt && python app.py"

# 部署后必须更新 Nginx
python3 /root/.local/bin/olares-nginx-config
```

### 部署后回复模板

```
✅ 部署成功！

🌐 访问地址：https://8cf849020.{username}.olares.com/{app-name}/
📁 代码目录：/root/workspace/{app-name}/

管理命令：
• 查看日志：olares-manage logs {app-name}
• 查看状态：olares-manage info {app-name}
• 删除应用：olares-manage delete {app-name}
```

---

## 🛠️ 管理命令

```bash
olares-manage list              # 列出所有应用
olares-manage info <app-name>   # 查看应用详情
olares-manage logs <app-name>   # 查看日志
olares-manage delete <app-name> # 删除应用
olares-urls                     # 显示所有 URL
```

---

## 🌐 网络架构

```
用户浏览器 → https://8cf849020.{username}.olares.com/{app-name}/
    ↓
Olares Ingress → OpenCode Container:3000 (Nginx)
    ↓
    ├─ /           → localhost:4096 (OpenCode Server)
    └─ /{app-name}/ → {app-name}-svc:{port}
```

---

## 🔧 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 502 Bad Gateway | Pod 未运行 | `olares-manage logs <app-name>` |
| 404 Not Found | Nginx 未配置 | `python3 /root/.local/bin/olares-nginx-config` |
| 数据库连接失败 | 环境变量未设置 | 检查 OlaresManifest.yaml |

---

## 📚 参考文档

| 文档 | 内容 |
|------|------|
| `docs/database-reference.md` | PostgreSQL 详细用法 |
| `docs/deployment-reference.md` | 部署命令和网络架构 |
| `docs/helm-reference.md` | Helm Chart 打包格式 |
| `docs/github-submission.md` | Market 提交流程 |

---

## ✅ 示例：正确的开发回复

```
好的，我来帮你创建一个待办事项应用。

[创建 /root/workspace/todo-app/app.py]
[创建 /root/workspace/todo-app/requirements.txt]
[创建 /root/workspace/todo-app/static/index.html]

应用已创建并测试通过：
- 后端：Flask + PostgreSQL
- 前端：简洁的 HTML/CSS/JS
- API：GET/POST/DELETE /api/todos

---
## ✅ 开发完成！

📁 项目位置：`/root/workspace/todo-app/`

**发布到 Olares？** 回复 "publish" 一键部署。
```

## ❌ 示例：错误的开发回复

```
首先，你想用什么数据库？PostgreSQL、MySQL 还是 SQLite？  ← 违反规则2
你想把项目放在哪个目录？  ← 违反规则3
应用已创建完成！有问题随时告诉我。  ← 违反规则1
```
