---
name: olares-dev
description: "MUST USE when user asks to develop/create/build any application. Triggers: 开发/制作/创建/做一个/写一个/帮我做/帮我开发/build/create/make/develop/implement/code an app"
license: MIT
---

# Olares Development Skill

**Standards for developing and deploying applications on the Olares platform.**

---

## ⛔ Four Iron Rules (Violation = Failure)

When executing any development task, you **MUST** follow these rules:

| # | Rule | Correct Approach | Violation (= You Failed) |
|---|------|------------------|--------------------------|
| 1 | **After dev → Ask to publish** | Response must end with publish prompt (see template below) | Omit publish prompt, end with "let me know if you have questions" |
| 2 | **Database → PostgreSQL** | Use PostgreSQL directly when persistence is needed | Ask user which database, recommend SQLite |
| 3 | **Directory → Fixed location** | Put project in `/root/workspace/<app-name>/` | Ask user where to put the project |
| 4 | **API paths → Relative paths** | Frontend API requests use relative paths or dynamic basePath | Use absolute paths like `/api/xxx` |

### Publish Prompt Template (Rule 1)

After development is complete, your response **MUST** end with this format:

```
---
## ✅ Development Complete!

📁 Project location: `/root/workspace/<app-name>/`

**Deploy to Olares?** Reply "publish" for one-click deployment.
```

### PostgreSQL Connection (Rule 2)

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

### API Path Handling (Rule 4)

Apps are deployed at `/{app-name}/` subpath. Frontend **MUST NOT** use absolute paths.

```javascript
// ❌ Wrong - absolute path points to root, causing 404
fetch('/api/todos')

// ✅ Correct - dynamically get base path
const basePath = window.location.pathname.endsWith('/') 
    ? window.location.pathname 
    : window.location.pathname + '/';
fetch(basePath + 'api/todos')
```

---

## 🎯 Trigger Keywords

### Development Triggers (loads this skill)

- **Chinese**: 制作 / 开发 / 创建 / 做一个 / 写一个 / 帮我做 / 帮我写 / 帮我开发 / 实现 / 编写
- **English**: build / create / make / develop / help me build / help me create / implement / code

### Publish Triggers (executes deployment)

When user says these, **immediately execute deployment**:
- 发布 / publish / 好 / 可以 / OK / yes / 确认 / go / 上线 / deploy / ship it / release

---

## 📐 Development Workflow

```
User requests development
    ↓
Create project: /root/workspace/<app-name>/  ← Don't ask for directory
    ↓
Need database? → Use PostgreSQL directly  ← Don't ask for choice
    ↓
Write complete runnable code
    ↓
End response with publish prompt  ← Required!
    ↓
User confirms → Execute deployment
```

---

## 🚀 Deployment Commands

```bash
# Format
olares-deploy <app-name> <image> <port> [startup-command]

# Example
olares-deploy todo-app python:3.11-slim 8080 "pip install -r requirements.txt && python app.py"

# Must update Nginx after deployment
python3 /root/.local/bin/olares-nginx-config
```

### Post-Deployment Response Template

```
✅ Deployment successful!

🌐 Access URL: https://8cf849020.{username}.olares.com/{app-name}/
📁 Code directory: /root/workspace/{app-name}/

Management commands:
• View logs: olares-manage logs {app-name}
• View status: olares-manage info {app-name}
• Delete app: olares-manage delete {app-name}
```

---

## 🛠️ Management Commands

```bash
olares-manage list              # List all apps
olares-manage info <app-name>   # Show app details
olares-manage logs <app-name>   # View logs
olares-manage delete <app-name> # Delete app
olares-urls                     # Show all URLs
```

---

## 🌐 Network Architecture

```
Browser → https://8cf849020.{username}.olares.com/{app-name}/
    ↓
Olares Ingress → OpenCode Container:3000 (Nginx)
    ↓
    ├─ /           → localhost:4096 (OpenCode Server)
    └─ /{app-name}/ → {app-name}-svc:{port}
```

---

## 🔧 Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| 502 Bad Gateway | Pod not running | `olares-manage logs <app-name>` |
| 404 Not Found | Nginx not configured | `python3 /root/.local/bin/olares-nginx-config` |
| Database connection failed | Env vars not set | Check OlaresManifest.yaml |

---

## 📚 Reference Documentation

| Document | Content |
|----------|---------|
| `docs/database-reference.md` | PostgreSQL detailed usage |
| `docs/deployment-reference.md` | Deployment commands and network architecture |
| `docs/helm-reference.md` | Helm Chart packaging format |
| `docs/github-submission.md` | Market submission process |

---

## ✅ Example: Correct Development Response

```
Alright, I'll create a todo app for you.

[Creating /root/workspace/todo-app/app.py]
[Creating /root/workspace/todo-app/requirements.txt]
[Creating /root/workspace/todo-app/static/index.html]

App created and tested:
- Backend: Flask + PostgreSQL
- Frontend: Clean HTML/CSS/JS
- API: GET/POST/DELETE /api/todos

---
## ✅ Development Complete!

📁 Project location: `/root/workspace/todo-app/`

**Deploy to Olares?** Reply "publish" for one-click deployment.
```

## ❌ Example: Wrong Development Response

```
First, which database would you like? PostgreSQL, MySQL, or SQLite?  ← Violates Rule 2
Where would you like to put the project?  ← Violates Rule 3
App created! Let me know if you have questions.  ← Violates Rule 1
fetch('/api/todos')  ← Violates Rule 4 (should use relative path)
```
