# Olares Application Development Skill

## Trigger Conditions

**AUTOMATIC ACTIVATION - No need for user to mention "Olares":**

### Development Triggers (MANDATORY FLOW)

**Trigger Keywords:**
- Chinese: "制作" / "开发" / "创建" / "做一个" / "写一个" / "帮我做" / "帮我写" / "帮我开发" / "实现" / "编写"
- English: "build" / "create" / "make" / "develop" / "help me build" / "help me create" / "implement" / "code"

**CRITICAL BEHAVIOR - AI MUST FOLLOW THIS EXACT FLOW:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT WORKFLOW                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. User requests development                                     │
│     ↓                                                             │
│  2. AI develops the application                                   │
│     • Detect if database needed → Use PostgreSQL (injected)       │
│     • Write complete, runnable code                               │
│     • Include all necessary files                                 │
│     ↓                                                             │
│  3. AI MUST end with publish prompt (see below)                   │
│     ↓                                                             │
│  4. User confirms publish                                         │
│     ↓                                                             │
│  5. AI executes publish automatically                             │
│     • Run olares-deploy to Olares                                 │
│     • Update Nginx config                                         │
│     • Report external URL                                         │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**POST-DEVELOPMENT PROMPT (MANDATORY):**
After completing ANY development task, you MUST end your response with EXACTLY:

```
---
## ✅ 开发完成！Development Complete!

您的应用已准备就绪。Your application is ready.

**下一步 / Next Step:**

只需回复以下任意一个词，我将自动发布：
Just reply with any of these words, and I'll publish automatically:

| 命令 | Command | 效果 |
|------|---------|------|
| **发布** | **publish** | 发布到 Olares 正式环境 |

💡 回复 "发布" 或 "publish" 即可完成发布。
```

### Publish Triggers (AUTO-EXECUTE)

**Trigger Keywords (User confirms publish):**
- Publish: "发布" / "publish" / "好" / "可以" / "OK" / "yes" / "确认" / "同意" / "go" / "上线" / "打包" / "package" / "release"

**CRITICAL: When user says ANY of these after development, IMMEDIATELY execute publish to Olares. NO further confirmation needed.**

**Auto-Publish Execution:**
```bash
# 1. Detect app configuration
APP_NAME="<derived-from-code>"
IMAGE="python:3.11-slim"  # or detected from code
PORT="8080"
COMMAND="<detected-startup-command>"

# 2. Execute publish to Olares
/root/.local/bin/olares-deploy "$APP_NAME" "$IMAGE" "$PORT" "$COMMAND"

# 3. Update Nginx (MANDATORY)
python3 /root/.local/bin/olares-nginx-config

# 4. Report URL to user
echo "🌐 Your app is live at: https://xxx-3000.xxx.olares.com/$APP_NAME/"
```

### Database Triggers (AUTO-INTEGRATE)

**When to Trigger:**
- User mentions: "数据库" / "database" / "DB" / "存储数据" / "保存数据" / "save data"
- User mentions: "PostgreSQL" / "Postgres" / "MySQL" / "SQLite" / "MongoDB" / "Redis"
- User's app requires: user accounts, todos, posts, items, orders, or any persistent data
- Code contains: database connection strings, ORM setup, SQL queries

**AUTOMATIC BEHAVIOR:**
1. **Always use PostgreSQL** - injected by system or container environment
2. **NEVER** ask user which database to use - just use PostgreSQL
3. **NEVER** suggest installing a separate database
4. **NEVER** use SQLite - always use the injected PostgreSQL

**Database Auto-Detection:**
```python
# If user's app needs ANY of these, include database automatically:
NEEDS_DATABASE = [
    "user", "account", "login", "register",  # User system
    "todo", "task", "note", "item",           # CRUD apps
    "post", "article", "comment", "blog",     # Content apps
    "order", "product", "cart", "payment",    # E-commerce
    "save", "store", "persist", "remember",   # Generic storage
]
```

### Other Triggers
- User mentions "Olares", "Terminus" (legacy name), or self-hosted cloud
- Task involves creating Helm charts
- User needs to package a Docker image as an app

## Overview

Olares is a self-hosted cloud operating system. Applications are deployed as Helm charts with an additional `OlaresManifest.yaml` configuration file.

**Key Concepts:**
- **Olares Application Chart** = Standard Helm Chart + `OlaresManifest.yaml`
- **No REST API** for deployment - use Studio UI or olares-cli
- **System Services**: PostgreSQL, Redis, MongoDB, Zinc (search) are pre-installed
- **User Isolation**: Each user gets isolated app instances

**DEVELOPMENT DIRECTORY:**
- **所有应用代码都在 `/root/workspace` 目录下创建**
- 每个应用一个子目录：`/root/workspace/<app-name>/`
- 部署时自动挂载到容器的 `/app` 目录
- 代码修改后容器内立即生效（无需重新部署）

**DEPLOYMENT METHOD:**
- **Olares Publish** - Direct deployment to Olares production environment via olares-deploy command

---

## 🗄️ DATABASE USAGE GUIDE (PostgreSQL)

**CRITICAL**: When user's application needs data persistence, ALWAYS use Olares built-in PostgreSQL. NEVER suggest installing a separate database.

### Database Usage

**Always use PostgreSQL** - The database connection is automatically injected by the system or container environment.

**Why PostgreSQL:**
- ✅ Production-ready from the start
- ✅ Connection automatically injected via environment variables
- ✅ No separate database installation needed
- ✅ Full SQL feature support

### PostgreSQL Configuration

**Step 1: Configure OlaresManifest.yaml**

```yaml
# OlaresManifest.yaml
middleware:
  postgres:
    username: myapp_user
    password: {{ .Values.postgres.password }}
    databases:
      - name: myapp_db
        distributed: false
```

**Step 2: Configure Deployment Environment Variables**

```yaml
# templates/deployment.yaml
env:
  # Individual variables
  - name: PG_HOST
    value: "{{ .Values.postgres.host }}"
  - name: PG_PORT
    value: "{{ .Values.postgres.port }}"
  - name: PG_USER
    value: "{{ .Values.postgres.username }}"
  - name: PG_PASSWORD
    value: "{{ .Values.postgres.password }}"
  - name: PG_DATABASE
    value: "{{ .Values.postgres.databases.myapp_db }}"
  
  # Full connection string (recommended)
  - name: DATABASE_URL
    value: "postgresql://{{ .Values.postgres.username }}:{{ .Values.postgres.password }}@{{ .Values.postgres.host }}:{{ .Values.postgres.port }}/{{ .Values.postgres.databases.myapp_db }}"
```

**Step 3: Application Code (PostgreSQL Version)**

```python
# app.py - Production version with PostgreSQL
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, request

app = Flask(__name__)

# Get database URL from environment (injected by Olares)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def init_db():
    """Initialize database schema"""
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            completed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

# Initialize on startup
init_db()

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM todos ORDER BY created_at DESC')
    todos = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO todos (title) VALUES (%s) RETURNING id', (data['title'],))
    todo_id = cur.fetchone()['id']
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': todo_id, 'title': data['title'], 'completed': False}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

**Requirements.txt for PostgreSQL:**
```
flask
psycopg2-binary
```

### Database Initialization Patterns

**Pattern 1: Auto-create on Startup (Recommended for Simple Apps)**
```python
# In app.py - run init_db() at module load
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS ...')
    conn.commit()
    cur.close()
    conn.close()

init_db()  # Called once on startup
```

**Pattern 2: Migration Scripts (For Complex Apps)**
```bash
# Use Alembic for SQLAlchemy migrations
pip install alembic
alembic init migrations
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

**Pattern 3: Using SQLAlchemy ORM**
```python
# models.py - Using SQLAlchemy with PostgreSQL
import os
from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

# Get PostgreSQL connection from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = 'todos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create tables
with app.app_context():
    db.create_all()
```

### Quick Reference: Database Environment Variables

When `middleware.postgres` is configured, Olares injects these variables:

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `{{ .Values.postgres.host }}` | PostgreSQL hostname | `citus-master-svc.user-space-xxx` |
| `{{ .Values.postgres.port }}` | PostgreSQL port | `5432` |
| `{{ .Values.postgres.username }}` | Database user | `myapp_user` |
| `{{ .Values.postgres.password }}` | Auto-generated password | `xK9...abc` |
| `{{ .Values.postgres.databases.myapp_db }}` | Database name | `myapp_db_xxx` |

### Using Database Environment Variables in Application Code

After configuring environment variables in `deployment.yaml`, your application receives these values at runtime. Here's how to use them in different languages:

**Common Environment Variable Names (configure in deployment.yaml):**

| Env Variable | Helm Template Value | Runtime Example |
|--------------|---------------------|-----------------|
| `DB_HOST` | `{{ .Values.postgres.host }}` | `citus-master-svc.user-system-xxx` |
| `DB_PORT` | `{{ .Values.postgres.port }}` | `5432` |
| `DB_USER` | `{{ .Values.postgres.username }}` | `myapp_xxx_user` |
| `DB_PASSWORD` | `{{ .Values.postgres.password }}` | `XJBVYOFh7Wr...` |
| `DB_DATABASE` | `{{ .Values.postgres.databases.<name> }}` | `myapp_db_xxx` |

**Python Example (using psycopg2):**

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    """Create database connection using Olares-injected environment variables"""
    return psycopg2.connect(
        host=os.environ.get('DB_HOST'),
        port=os.environ.get('DB_PORT', '5432'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_DATABASE'),
        cursor_factory=RealDictCursor
    )

# Alternative: Build connection string
def get_database_url():
    """Build PostgreSQL connection URL from environment variables"""
    return (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}"
        f"/{os.environ['DB_DATABASE']}"
    )
```

**Python Example (using SQLAlchemy):**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Build connection URL from environment variables
DATABASE_URL = (
    f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
    f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}"
    f"/{os.environ['DB_DATABASE']}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Node.js Example (using pg):**

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: process.env.DB_HOST,
  port: parseInt(process.env.DB_PORT || '5432'),
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_DATABASE,
});

// Query example
async function getUsers() {
  const { rows } = await pool.query('SELECT * FROM users');
  return rows;
}
```

**Go Example (using pgx):**

```go
package main

import (
    "context"
    "fmt"
    "os"

    "github.com/jackc/pgx/v5/pgxpool"
)

func connectDB() (*pgxpool.Pool, error) {
    connStr := fmt.Sprintf(
        "postgres://%s:%s@%s:%s/%s",
        os.Getenv("DB_USER"),
        os.Getenv("DB_PASSWORD"),
        os.Getenv("DB_HOST"),
        os.Getenv("DB_PORT"),
        os.Getenv("DB_DATABASE"),
    )
    return pgxpool.New(context.Background(), connStr)
}
```

**Rust Example (using sqlx):**

```rust
use sqlx::postgres::PgPoolOptions;
use std::env;

async fn connect_db() -> Result<sqlx::PgPool, sqlx::Error> {
    let database_url = format!(
        "postgres://{}:{}@{}:{}/{}",
        env::var("DB_USER").expect("DB_USER required"),
        env::var("DB_PASSWORD").expect("DB_PASSWORD required"),
        env::var("DB_HOST").expect("DB_HOST required"),
        env::var("DB_PORT").unwrap_or_else(|_| "5432".to_string()),
        env::var("DB_DATABASE").expect("DB_DATABASE required"),
    );

    PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await
}
```

**Best Practices:**

1. **Always use environment variables** - Never hardcode database credentials
2. **Provide defaults for port** - `DB_PORT` is usually `5432` but be explicit
3. **Use connection pooling** - PostgreSQL has limited connections, use pools
4. **Handle connection errors gracefully** - The database may not be ready immediately on startup
5. **Verify variables exist** - Check at startup if required variables are set

**Health Check Pattern:**

```python
def check_database_health():
    """Verify database connection and environment variables"""
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_DATABASE']

    missing = [var for var in required_vars if not os.environ.get(var)]
    if missing:
        raise EnvironmentError(f"Missing database variables: {missing}")

    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Troubleshooting Database Connections

**Issue: Connection refused**
```bash
# Check if database variables are set
echo $DATABASE_URL
echo $PG_HOST

# Test connection from container
python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

**Issue: Authentication failed**
```bash
# Verify username/password match OlaresManifest.yaml
# Check that middleware.postgres is properly configured
```

**Issue: Database does not exist**
```bash
# Ensure database name in .Values.postgres.databases.<name> matches your code
# Database is auto-created when app is installed via Olares
```

### Database Isolation with PostgreSQL Schema

When developing multiple applications that share the same PostgreSQL instance, use **PostgreSQL Schema** to isolate data between applications.

**Why Schema Isolation?**

| Scenario | Database Isolation | Notes |
|----------|-------------------|-------|
| **Single App** | Use default `public` schema | Simple, no extra config needed |
| **Multiple Apps** | Schema per app | Logical isolation in shared database |

Use Schema to achieve logical isolation without needing separate databases.

**Python Example: Schema-based Isolation**

```python
import os
import psycopg2
from psycopg2.extras import RealDictCursor

class AppDatabase:
    """Database wrapper with schema isolation for multi-app environments"""

    def __init__(self, app_name: str):
        self.app_name = app_name
        self.schema = app_name.replace('-', '_')  # Schema names can't have hyphens
        self._init_schema()

    def get_connection(self):
        """Get database connection with schema set"""
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT', '5432'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_DATABASE'),
            cursor_factory=RealDictCursor,
            options=f'-c search_path={self.schema}'  # Auto-use this schema
        )
        return conn

    def _init_schema(self):
        """Create schema if not exists"""
        # Connect without schema first
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            port=os.environ.get('DB_PORT', '5432'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_DATABASE')
        )
        cur = conn.cursor()
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS {self.schema}')
        conn.commit()
        cur.close()
        conn.close()

# Usage: Each app uses its own schema
# App 1: Todo App
todo_db = AppDatabase('todo-app')
conn = todo_db.get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS tasks (id SERIAL PRIMARY KEY, title TEXT)')
# Creates: todo_app.tasks

# App 2: Blog App
blog_db = AppDatabase('blog-app')
conn = blog_db.get_connection()
conn.execute('CREATE TABLE IF NOT EXISTS posts (id SERIAL PRIMARY KEY, content TEXT)')
# Creates: blog_app.posts
```

**Node.js Example: Schema-based Isolation**

```javascript
const { Pool } = require('pg');

class AppDatabase {
  constructor(appName) {
    this.schema = appName.replace(/-/g, '_');
    this.pool = new Pool({
      host: process.env.DB_HOST,
      port: parseInt(process.env.DB_PORT || '5432'),
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_DATABASE,
    });
  }

  async init() {
    await this.pool.query(`CREATE SCHEMA IF NOT EXISTS ${this.schema}`);
    await this.pool.query(`SET search_path TO ${this.schema}`);
  }

  async query(sql, params) {
    // Ensure schema is set for each query
    const client = await this.pool.connect();
    try {
      await client.query(`SET search_path TO ${this.schema}`);
      return await client.query(sql, params);
    } finally {
      client.release();
    }
  }
}

// Usage
const todoDb = new AppDatabase('todo-app');
await todoDb.init();
await todoDb.query('CREATE TABLE IF NOT EXISTS tasks (id SERIAL, title TEXT)');
```

**SQLAlchemy Example: Schema-based Isolation**

```python
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

def create_app_engine(app_name: str):
    """Create SQLAlchemy engine with schema isolation"""
    schema = app_name.replace('-', '_')

    database_url = (
        f"postgresql://{os.environ['DB_USER']}:{os.environ['DB_PASSWORD']}"
        f"@{os.environ['DB_HOST']}:{os.environ.get('DB_PORT', '5432')}"
        f"/{os.environ['DB_DATABASE']}"
    )

    engine = create_engine(
        database_url,
        connect_args={'options': f'-c search_path={schema}'},
        pool_pre_ping=True
    )

    # Create schema if not exists
    with engine.connect() as conn:
        conn.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        conn.commit()

    return engine, schema

# Usage with ORM
engine, schema = create_app_engine('my-app')
Base = declarative_base()
Base.metadata.schema = schema  # All tables use this schema

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

Base.metadata.create_all(engine)  # Creates: my_app.users
```

**Best Practices for Schema Isolation:**

1. **Naming Convention**: Use app name as schema name (replace hyphens with underscores)
2. **Initialize Early**: Create schema at app startup before any table operations
3. **Set search_path**: Always set `search_path` to ensure queries target correct schema
4. **Flexibility**: Schema code works with default `public` schema if not set

**Schema vs Separate Databases:**

| Aspect | Schema Isolation | Separate Databases |
|--------|-----------------|-------------------|
| Setup | Code-level, automatic | Requires new middleware config |
| Performance | Shared resources | Isolated resources |
| Backup | Single backup includes all | Per-database backup |
| Use Case | Multiple apps sharing DB | Single app per database |

---

## 🚀 OLARES PUBLISH (Automatic Deployment After Development)

**When to Use:** User completes application development and wants to publish to Olares production environment.

### Prerequisites Check

Before deploying, verify:
```bash
# Check kubectl is available
which /tmp/kubectl || echo "Need to install kubectl"

# Check current namespace
cat /var/run/secrets/kubernetes.io/serviceaccount/namespace

# Check RBAC permissions
/tmp/kubectl auth can-i create deployments -n $(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)
```

### Publish Tools

**Available Tools:**
- `/root/.local/bin/olares-deploy` - Deploy applications to Kubernetes
- `/root/.local/bin/olares-manage` - Manage deployed applications
- `/root/.local/bin/olares-urls` - Display all application URLs
- `/root/.local/bin/olares-nginx-config` - Update Nginx reverse proxy configuration

### Deployment Script

**Location:** `/root/.local/bin/olares-deploy`

**Usage:**
```bash
/root/.local/bin/olares-deploy <app-name> <image> <port> [startup-command]
```

**Example:**
```bash
# Deploy Python web app
olares-deploy my-app python:3.11-slim 8080 "pip install flask && python app.py"
```

### Automatic Deployment Workflow

**When user completes development:**

1. **Detect Application Type**
   ```python
   # Example: Python web application
   app_config = {
       'image': 'python:3.11-slim',
       'port': 8080,
       'detect': 'app.py or main.py'
   }
   ```

2. **Generate App Name**
   ```python
   import re
   app_name = re.sub(r'[^a-z0-9-]', '-', user_provided_name.lower())
   app_name = app_name.strip('-')[:50]  # Max 50 chars
   ```

3. **Build Startup Command**
   - Example: `pip install flask && python app.py`
   - Or: `pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 8080`

4. **Execute Deployment**
   ```bash
   /root/.local/bin/olares-deploy "$APP_NAME" "$IMAGE" "$PORT" "$COMMAND"
   ```

5. **Update Nginx Reverse Proxy (MANDATORY)**
   ```bash
   python3 /root/.local/bin/olares-nginx-config
   ```

6. **Extract Access URL**
   ```bash
   # Get the third-level domain from deployment
   THIRD_LEVEL=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
       -o jsonpath='{.metadata.annotations.applications\.app\.bytetrade\.io/default-thirdlevel-domains}' \
       | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['thirdLevelDomain'])")

   # Get user's Olares domain from namespace or config
   DOMAIN="{username}.olares.com"  # Extract from environment

   ACCESS_URL="https://${THIRD_LEVEL}.${DOMAIN}/${APP_NAME}/"
   ```

7. **Report to User**
   ```
   ✅ Deployment successful!

   🌐 访问地址: https://{app-id}-3000.{username}.olares.com/app-name/

   📁 代码目录: /root/workspace/app-name

   Manage your app:
   • View logs: olares-manage logs app-name
   • Check status: olares-manage info app-name
   ```

### External Access Configuration

**Olares URL Format:**
```
https://{appid}-{port}.{username}.olares.com/{path}

Example:
https://{app-id}-3000.{username}.olares.com/my-app/
         ↑          ↑      ↑            ↑
      app id     port   username    app path
```

**Required Annotations** (automatically added by script):
```yaml
annotations:
  meta.helm.sh/release-name: app-name
  meta.helm.sh/release-namespace: namespace
  applications.app.bytetrade.io/entrances: '[{"name":"app-name","host":"app-name-svc","port":8080,"title":"app-name","authLevel":"private","openMethod":"default"}]'
  applications.app.bytetrade.io/default-thirdlevel-domains: '[{"appName":"app-name","entranceName":"app-name","thirdLevelDomain":"random-hash-port"}]'
  applications.app.bytetrade.io/icon: https://app.cdn.olares.com/appstore/default/defaulticon.webp
  applications.app.bytetrade.io/title: app-name
```

### Management Commands

**Location:** `/root/.local/bin/olares-manage`

```bash
# List all deployed apps
olares-manage list

# Show app details and URL
olares-manage info <app-name>

# View logs
olares-manage logs <app-name>
olares-manage logs <app-name> -f  # Follow

# Test connectivity
olares-manage test <app-name>

# Delete app
olares-manage delete <app-name>
```

### Display All App URLs

**Location:** `/root/.local/bin/olares-urls`

```bash
# Show all deployed apps with URLs
olares-urls
```

**Output:**
```
═══════════════════════════════════════════════
  OpenCode Deployed Applications
═══════════════════════════════════════════════

▶ my-app
  Status: ✅ Running (1/1)
  Port: 8080
  访问地址: https://{app-id}-3000.{username}.olares.com/my-app/
  代码目录: /root/workspace/my-app
```

### Network Architecture

**Current Architecture (Unified Entry + Nginx Reverse Proxy):**
```
User Browser
    ↓ HTTPS
https://{app-id}-3000.{username}.olares.com/{app-name}/
    ↓ DNS Resolution
Olares Ingress Controller (TLS termination)
    ↓ HTTP
OpenCode Container (port 3000 - unified entry)
    ↓
Nginx Reverse Proxy (listening on 3000)
    ↓ Path-based routing
    ├─ / → localhost:4096 (OpenCode Server mode)
    └─ /my-app/       → my-app-svc:8080
    ↓
Service: app-name-svc (ClusterIP)
    ↓ TCP
Pod: app-name-xxx (10.233.x.x:port)
    ↓
Application (0.0.0.0:port)
```

**Key Points:**
- **Unified Entry**: All external requests come through port 3000 (OpenCode container)
- **Path Routing**: Different URL paths map to different services
- **Automatic Configuration**: Nginx configs auto-generated for each deployment
- **Fixed OpenCode Mapping**: Root path (/) always mapped to localhost:4096 for OpenCode Server

### Nginx Reverse Proxy Configuration

**IMPORTANT**: After each deployment, the Nginx reverse proxy MUST be updated to route external traffic.

#### Automatic Configuration Tool

**Location:** `/root/.local/bin/olares-nginx-config`

**Purpose:**
- Automatically scans all deployed applications
- Generates Nginx reverse proxy configurations
- Updates routing rules for external access
- Includes fixed mapping for OpenCode Server mode (port 4096)

**Usage:**
```bash
# After deploying any application, run:
python3 /root/.local/bin/olares-nginx-config
```

**Output:**
```
Olares Nginx Configuration Generator
============================================================

1. Scanning deployed applications...
   Found 1 application:
     - my-app (port 8080)

2. Generating Nginx configurations...
✓ Generated config: /etc/nginx/conf.d/dev/my-app.conf
✓ Generated fixed config: /etc/nginx/conf.d/dev/opencode-server.conf (port 4096)

3. Applying configuration...
✓ Nginx configuration test passed
✓ Nginx reloaded successfully

✅ Configuration complete!
```

#### Access URLs

After Nginx configuration, applications are accessible via:

**Pattern 1: Application Name Path (Recommended)**
```
https://{hash}-3000.{domain}/{app-name}/

Example:
https://{app-id}-3000.{username}.olares.com/my-app/
```

**Pattern 2: Port Number Path**
```
https://{hash}-3000.{domain}/{port}/

Example:
https://{app-id}-3000.{username}.olares.com/8080/  → my-app
```

**Fixed: OpenCode Server Mode**
```
https://{hash}-3000.{domain}/  → localhost:4096

Example:
https://{app-id}-3000.{username}.olares.com/
```

#### Nginx Configuration Details

**Generated Config Structure:**
```nginx
# /etc/nginx/conf.d/dev/my-app.conf

# Route by application name
location /my-app/ {
    proxy_pass http://my-app-svc.namespace.svc.cluster.local:8080/;
    proxy_http_version 1.1;
    
    # Standard headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support (critical for real-time apps)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    
    # Timeouts for long-lived connections
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # Disable buffering for real-time responses
    proxy_buffering off;
    proxy_request_buffering off;
}

# Route by port number
location /8080/ {
    proxy_pass http://my-app-svc.namespace.svc.cluster.local:8080/;
    # ... same config as above
}
```

**Fixed OpenCode Server Config:**
```nginx
# /etc/nginx/conf.d/dev/opencode-server.conf

# OpenCode Server mode (always on port 4096)
# Fallback: All other paths go to OpenCode Server (must be last)
location / {
    proxy_pass http://localhost:4096;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Critical for OpenCode Server WebSocket connections
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    
    # Long timeout for persistent connections (1 hour)
    proxy_connect_timeout 60s;
    proxy_send_timeout 3600s;
    proxy_read_timeout 3600s;
    
    proxy_buffering off;
    proxy_request_buffering off;
}
```

#### Complete Deployment Workflow

**Standard Process:**
```bash
# Step 1: Deploy application
/root/.local/bin/olares-deploy my-app python:3.11-slim 8080 "python app.py"

# Step 2: Update Nginx reverse proxy (MANDATORY)
python3 /root/.local/bin/olares-nginx-config

# Step 3: Access application
# https://{app-id}-3000.{username}.olares.com/my-app/
```

**Automated Integration:**

The deployment script at `/root/.local/bin/olares-deploy` can automatically trigger Nginx configuration update:

```bash
# Add at the end of olares-deploy script
if [ -f /root/.local/bin/olares-nginx-config ]; then
    echo ""
    echo "Updating Nginx reverse proxy configuration..."
    python3 /root/.local/bin/olares-nginx-config > /dev/null 2>&1 || true
    echo "✓ Nginx configuration updated"
fi
```

#### Nginx Management Commands

```bash
# Check Nginx status
python3 /root/.local/bin/olares-nginx-config status

# Manually reload Nginx
nginx -s reload

# Test Nginx configuration
nginx -t

# View Nginx logs
tail -f /tmp/nginx-error.log
tail -f /tmp/nginx-access.log

# View generated configs
ls -la /etc/nginx/conf.d/dev/
cat /etc/nginx/conf.d/dev/my-app.conf
```

#### Troubleshooting Nginx Proxy

**Issue: 502 Bad Gateway**
```bash
# Check if application Pod is running
/tmp/kubectl get pods -n namespace -l app=my-app

# Check if Service exists
/tmp/kubectl get svc -n namespace my-app-svc

# Test Service connectivity from within container
curl http://my-app-svc.namespace.svc.cluster.local:port
```

**Issue: 404 Not Found**
```bash
# Check if Nginx config exists
ls /etc/nginx/conf.d/dev/my-app.conf

# Regenerate Nginx configuration
python3 /root/.local/bin/olares-nginx-config

# Check Nginx error log
tail -f /tmp/nginx-error.log
```

**Issue: Nginx not running**
```bash
# Check Nginx process
ps aux | grep nginx

# Start Nginx
nginx

# Reload Nginx
nginx -s reload
```

**Issue: App route shows OpenCode instead of application**

**Symptom:** Accessing `https://xxx.olares.com/my-app/` shows OpenCode UI instead of the deployed application.

**Root Cause:** `olares-nginx-config` generates config files in `/etc/nginx/conf.d/dev/` subdirectory, but `nginx.conf` only includes `/etc/nginx/conf.d/*.conf` (not subdirectories). The app route configs are never loaded.

**Diagnosis:**
```bash
# Check if config file exists
ls /etc/nginx/conf.d/dev/my-app.conf  # File exists but not loaded

# Check what nginx.conf includes
grep "include" /etc/nginx/nginx.conf
# Shows: include /etc/nginx/conf.d/*.conf;  (no subdirectory)

# Check default.conf - only has OpenCode route
cat /etc/nginx/conf.d/default.conf
# Shows: location / { proxy_pass http://localhost:4096; }
```

**Solution:** Add an `include` directive in `/etc/nginx/conf.d/default.conf` to load configs from the `dev/` subdirectory:

```nginx
server {
    listen 3000;
    server_name _;
    
    # Include all app routes (MUST be before location /)
    include /etc/nginx/conf.d/dev/*.conf;
    
    # OpenCode Server default route (fallback)
    location / {
        proxy_pass http://localhost:4096;
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

Then reload nginx:
```bash
kill -HUP $(pgrep -f "nginx: master" | head -1)
```

**Why this solution:**
- One-time fix: only need to modify `default.conf` once
- Each app config stays in its own file (`/etc/nginx/conf.d/dev/app-name.conf`)
- `olares-nginx-config` script works without modification
- New app deployments work automatically after `nginx -s reload`

#### Health Check Endpoint

Nginx includes a health check endpoint for monitoring:

```bash
# Test health endpoint
curl http://localhost:3000/health
# Expected: healthy

# External access
https://{app-id}-3000.{username}.olares.com/health
```

### Deployment Isolation

Each deployed app gets:
- **Independent Deployment** (process isolation)
- **Independent Service** (network isolation)
- **Independent Resource Quota** (CPU/Memory limits)
- **Unique External Domain** (DNS isolation)

### Error Handling

**If deployment fails:**
```bash
# Check Pod status
/tmp/kubectl get pods -n namespace -l app=app-name

# Check Pod logs
/tmp/kubectl logs -n namespace -l app=app-name

# Check events
/tmp/kubectl get events -n namespace --sort-by=.lastTimestamp | tail -20

# Describe deployment
/tmp/kubectl describe deployment app-name -n namespace
```

**Common Issues:**
| Error | Cause | Solution |
|-------|-------|----------|
| `Forbidden: cannot create deployments` | No RBAC | Request admin to apply RBAC config |
| `ImagePullBackOff` | Image not found | Check image name and registry |
| `CrashLoopBackOff` | App crashes on start | Check logs for errors |
| `admission webhook denied` | Missing annotations | Use deployment script with proper annotations |
| App accessible internally but not externally | Default entrance port is 4096, not 3000 | Patch deployment to use port 3000 (see below) |
| `No such file or directory` in Pod | hostPath volume can't access OpenCode files | Use ConfigMap for code deployment |

### ⚠️ CRITICAL: First-Time Setup Requirements

Before deploying applications, ensure these configurations are in place:

#### 1. RBAC Permissions

The ServiceAccount needs permissions to create deployments and services:

```bash
# Check current permissions
/tmp/kubectl auth can-i create deployments -n $(cat /var/run/secrets/kubernetes.io/serviceaccount/namespace)

# If "no", request admin to apply RBAC:
cat << 'EOF' | /tmp/kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: devbox-deployer
  namespace: <YOUR_NAMESPACE>
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["services", "configmaps"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: devbox-deployer-binding
  namespace: <YOUR_NAMESPACE>
subjects:
  - kind: ServiceAccount
    name: default
    namespace: <YOUR_NAMESPACE>
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: devbox-deployer
EOF
```

#### 2. Entrance Port Configuration (CRITICAL!)

**Problem:** OpenCode's default entrance is port 4096 (OpenCode Server). External traffic goes directly to port 4096, bypassing Nginx on port 3000. This causes deployed apps to be inaccessible externally even though internal routing works.

**Solution:** Change the default entrance port from 4096 to 3000:

```bash
# Get OpenCode deployment name (usually "mymas" or similar)
DEPLOY_NAME=$(/tmp/kubectl get deployment -n $NAMESPACE -l app=mymas -o jsonpath='{.items[0].metadata.name}')

# Check current entrance configuration
/tmp/kubectl get deployment $DEPLOY_NAME -n $NAMESPACE -o jsonpath='{.metadata.annotations.applications\.app\.bytetrade\.io/entrances}'

# Patch to use port 3000 as default entrance
/tmp/kubectl patch deployment $DEPLOY_NAME -n $NAMESPACE --type='json' -p='[
  {"op": "replace", "path": "/metadata/annotations/applications.app.bytetrade.io~1entrances", "value": "[{\"name\":\"mymas\",\"host\":\"mymas-svc\",\"port\":3000,\"title\":\"OpenCode\",\"authLevel\":\"private\",\"openMethod\":\"default\"}]"}
]'
```

**Traffic Flow After Fix:**
```
External Browser
    ↓ HTTPS
https://xxx.username.olares.com/
    ↓
Olares Ingress → Port 3000 (Nginx)
    ↓ Path-based routing
    ├─ /todo-app/  → todo-app-svc:8080
    └─ /           → localhost:4096 (OpenCode Server)
```

#### 3. Code Deployment Method

**Problem:** hostPath volumes mount from the **worker node's** filesystem, not from the OpenCode container. Since code exists only in OpenCode container, Pods on other nodes can't access it.

**Solution:** Use ConfigMap to store application code:

```bash
# Create ConfigMap with code files
/tmp/kubectl create configmap myapp-code -n $NAMESPACE \
  --from-file=app.py=/root/workspace/myapp/app.py \
  --from-file=index.html=/root/workspace/myapp/static/index.html

# In deployment, mount ConfigMap and copy to working directory:
# See deployment template below
```

**Deployment with ConfigMap:**
```yaml
spec:
  containers:
  - name: myapp
    image: python:3.11-slim
    command: ["/bin/sh", "-c"]
    args:
      - |
        mkdir -p /app/static
        cp /code/app.py /app/app.py
        cp /code/index.html /app/static/index.html
        cd /app
        pip install flask
        python app.py
    volumeMounts:
    - name: code
      mountPath: /code
  volumes:
  - name: code
    configMap:
      name: myapp-code
```

### Example: Complete Automated Flow

**User says:** "I built a todo app, deploy it"

**AI Response:**
```
I'll deploy your app to Olares right away!

Detecting configuration...
✓ Image: python:3.11-slim
✓ Port: 8080
✓ App name: todo-app

Deploying to Olares...
[Executing: olares-deploy todo-app python:3.11-slim 8080 "pip install flask && python app.py"]

✅ Deployment successful!

Updating Nginx reverse proxy...
[Executing: python3 /root/.local/bin/olares-nginx-config]
✓ Nginx configuration updated
✓ Generated reverse proxy config for todo-app

Your todo app is now live!

🌐 访问地址: https://{app-id}-3000.{username}.olares.com/todo-app/
📁 代码目录: /root/workspace/todo-app

查看日志: olares-manage logs todo-app
应用管理: olares-manage info todo-app
```

---

## 📦 MARKET PACKAGE DEPLOYMENT (For Publishing)

For apps intended for Olares Market or formal distribution, use the Helm chart packaging method.

### Application Package Structure

```
myapp/
├── Chart.yaml              # Helm chart metadata (REQUIRED)
├── OlaresManifest.yaml     # Olares-specific configuration (REQUIRED)
├── owners                  # GitHub usernames of maintainers (REQUIRED for Market)
├── templates/
│   ├── deployment.yaml     # Kubernetes deployment
│   └── service.yaml        # Kubernetes service (if needed)
├── values.yaml             # Default values (optional)
└── README.md               # Documentation (recommended)
```

---

## Chart.yaml Template

```yaml
apiVersion: v2
name: myapp                    # lowercase, alphanumeric + hyphens
version: 0.1.0                 # Chart version (SemVer)
appVersion: "1.0.0"            # Application version
description: "My application description"
keywords:
  - productivity              # For market categorization
home: https://github.com/user/myapp
icon: https://example.com/icon.png
```

**Important Notes:**
- `name` must match directory name and `metadata.name` in OlaresManifest.yaml
- `version` must match `metadata.version` in OlaresManifest.yaml
- Use semantic versioning (SemVer): MAJOR.MINOR.PATCH

---

## OlaresManifest.yaml Complete Reference

This is the **most critical file** for Olares applications.

```yaml
terminusManifest.version: '0.7.1'        # Manifest schema version
terminusManifest.type: app               # app | recommend | model | middleware

metadata:
  name: myapp                            # Must match Chart.yaml name
  title: My Application                  # Display name in Market
  description: "Application description"
  icon: https://example.com/icon.png
  version: 0.1.0                         # Must match Chart.yaml version
  categories:
    - Productivity                       # Market category
  rating: 0                              # Initial rating

# ============================================
# PERMISSION CONFIGURATION
# ============================================
permission:
  # App data storage permission (RECOMMENDED)
  appData: true
  
  # User data access (home directories)
  userData:
    - Home                               # User's home directory
    - Documents                          # Documents folder

  # System API access
  sysData:
    - dataType: secret                   # Access secrets service
      group: secret.infisical
      appName: infisical
      svc: infisical-backend
      namespace: user-space-{{ .Values.bfl.username }}
      port: 8080
      version: v2
      ops:
        - RetrieveSecret
        - CreateSecret
        - DeleteSecret

# ============================================
# SPEC - Application Components
# ============================================
spec:
  # ------------------------------
  # Full-text Search (Zinc)
  # ------------------------------
  fulltext:
    enabled: false                       # Enable Zinc search integration
  
  # ------------------------------
  # Required System Dependencies
  # ------------------------------
  requiredMemory: 128Mi                  # Minimum memory
  requiredDisk: 512Mi                    # Minimum disk
  requiredCpu: 100m                      # Minimum CPU (100m = 0.1 cores)
  
  # Memory/CPU limits (actual container limits)
  limitedMemory: 512Mi
  limitedCpu: 500m
  
  # Required GPU (optional)
  requiredGpu: 0
  
  # ------------------------------
  # Supported Architectures
  # ------------------------------
  supportArch:
    - amd64
    - arm64
  
  # ------------------------------
  # Feature Flags
  # ------------------------------
  onlyAdmin: false                       # Admin-only app
  featuredImage: featured.png            # Market featured image
  promoteImage:                          # Promotion images
    - promote1.png
    - promote2.png

# ============================================
# ENTRANCES - Web UI Access Points
# ============================================
entrances:
  - name: myapp-web                      # Unique entrance ID
    title: My App                        # Display name
    icon: https://example.com/icon.png
    host: myapp-svc                      # Service hostname (from service.yaml)
    port: 3000                           # Service port
    authLevel: private                   # private | public
    openMethod: default                  # default | iframe | window

# ============================================
# MIDDLEWARE DEPENDENCIES
# ============================================
middleware:
  # PostgreSQL Database
  postgres:
    username: myapp_user
    password: {{ .Values.postgres.password }}     # Auto-generated
    databases:
      - name: myapp_db
        distributed: false               # Use distributed (CockroachDB-like) mode
  
  # Redis Cache
  redis:
    password: {{ .Values.redis.password }}        # Auto-generated
    namespace: myapp-cache
  
  # MongoDB (if needed)
  mongodb:
    username: myapp_user
    password: {{ .Values.mongodb.password }}
    databases:
      - name: myapp_db
        script: init-mongo.js            # Optional init script in templates/

# ============================================
# OPTIONS - User Configuration UI
# ============================================
options:
  analytics:
    enabled: false                       # Analytics tracking
  
  dependencies:                          # Dependent apps
    - name: mongodb                      # Require MongoDB middleware app
      type: middleware
      version: ">=0.1.0"
    
  policies:                              # Network policies
    - uriRegex: /api/.*
      level: two_factor                  # Require 2FA for API access
      oneTime: false
      validDuration: 3600s
      entranceName: myapp-web
```

---

## Deployment Template (templates/deployment.yaml)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
  namespace: {{ .Release.Namespace }}
  labels:
    app: {{ .Release.Name }}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
        - name: {{ .Release.Name }}
          image: "your-registry/your-image:tag"
          imagePullPolicy: IfNotPresent
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          
          # --------------------------------
          # ENVIRONMENT VARIABLES
          # --------------------------------
          env:
            # App Data Directory (if permission.appData: true)
            - name: APP_DATA_DIR
              value: /app/data
            
            # PostgreSQL (if middleware.postgres defined)
            - name: PG_HOST
              value: {{ .Values.postgres.host }}
            - name: PG_PORT
              value: "{{ .Values.postgres.port }}"
            - name: PG_USER
              value: {{ .Values.postgres.username }}
            - name: PG_PASSWORD
              value: {{ .Values.postgres.password }}
            - name: PG_DATABASE
              value: {{ .Values.postgres.databases.myapp_db }}
            # Full connection string
            - name: DATABASE_URL
              value: "postgresql://{{ .Values.postgres.username }}:{{ .Values.postgres.password }}@{{ .Values.postgres.host }}:{{ .Values.postgres.port }}/{{ .Values.postgres.databases.myapp_db }}"
            
            # Redis (if middleware.redis defined)
            - name: REDIS_HOST
              value: {{ .Values.redis.host }}
            - name: REDIS_PORT
              value: "{{ .Values.redis.port }}"
            - name: REDIS_PASSWORD
              value: {{ .Values.redis.password }}
            
            # MongoDB (if middleware.mongodb defined)
            - name: MONGO_URI
              value: "mongodb://{{ .Values.mongodb.username }}:{{ .Values.mongodb.password }}@{{ .Values.mongodb.host }}:{{ .Values.mongodb.port }}/{{ .Values.mongodb.databases.myapp_db }}"
            
            # Olares System Variables
            - name: OLARES_USER
              value: {{ .Values.bfl.username }}
            - name: POD_NAMESPACE
              valueFrom:
                fieldRef:
                  fieldPath: metadata.namespace
          
          # --------------------------------
          # VOLUME MOUNTS
          # --------------------------------
          volumeMounts:
            # App data volume (persistent storage)
            - name: app-data
              mountPath: /app/data
            
            # User home directory (if permission.userData includes Home)
            - name: user-home
              mountPath: /home/user
      
      volumes:
        - name: app-data
          hostPath:
            type: DirectoryOrCreate
            path: {{ .Values.userspace.appData }}/{{ .Release.Name }}
        
        - name: user-home
          hostPath:
            type: Directory
            path: {{ .Values.userspace.Home }}
          
      # --------------------------------
      # RESOURCE LIMITS
      # --------------------------------
      resources:
        requests:
          cpu: 100m
          memory: 128Mi
        limits:
          cpu: 500m
          memory: 512Mi
```

---

## Service Template (templates/service.yaml)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-svc        # Match entrances.host in OlaresManifest
  namespace: {{ .Release.Namespace }}
spec:
  type: ClusterIP
  selector:
    app: {{ .Release.Name }}
  ports:
    - name: http
      port: 3000                        # Match entrances.port
      targetPort: 3000
      protocol: TCP
```

---

## System-Injected Helm Variables

Olares automatically injects these variables (accessible via `.Values.*`):

### User Context
| Variable | Description | Example |
|----------|-------------|---------|
| `.Values.bfl.username` | Current user's name | `john` |
| `.Values.userspace.Home` | User home path | `/terminus/userdata/Home/john` |
| `.Values.userspace.appData` | App data root | `/terminus/userdata/AppData` |
| `.Values.userspace.appCache` | App cache root | `/terminus/userdata/AppCache` |

### PostgreSQL (when `middleware.postgres` defined)
| Variable | Description |
|----------|-------------|
| `.Values.postgres.host` | PostgreSQL host |
| `.Values.postgres.port` | PostgreSQL port (usually 5432) |
| `.Values.postgres.username` | Database username |
| `.Values.postgres.password` | Auto-generated password |
| `.Values.postgres.databases.<dbname>` | Database name |

### Redis (when `middleware.redis` defined)
| Variable | Description |
|----------|-------------|
| `.Values.redis.host` | Redis host |
| `.Values.redis.port` | Redis port (usually 6379) |
| `.Values.redis.password` | Auto-generated password |

### MongoDB (when `middleware.mongodb` defined)
| Variable | Description |
|----------|-------------|
| `.Values.mongodb.host` | MongoDB host |
| `.Values.mongodb.port` | MongoDB port (usually 27017) |
| `.Values.mongodb.username` | Database username |
| `.Values.mongodb.password` | Auto-generated password |
| `.Values.mongodb.databases.<dbname>` | Database name |

---

## 📚 ADVANCED: GitHub Market Submission (Optional Reference)

> **Note:** This section is for advanced users who want to publish their applications to the public Olares Market. The primary publishing method is via `olares-deploy` command (see "OLARES PUBLISH" section above).

To publish your application to the official public Olares Market, you can optionally submit it through GitHub.

### Prerequisites

Before submission:
1. ✅ Application tested thoroughly on your Olares
2. ✅ Complete Helm chart created (Chart.yaml + OlaresManifest.yaml + templates)
3. ✅ GitHub account with username
4. ✅ Application assets prepared (icon, screenshots, etc.)
5. ✅ Documentation written (README.md)

### Submission Process Overview

```
1. Fork official repository
   ↓
2. Add your application chart
   ↓
3. Create Pull Request with proper format
   ↓
4. GitBot automatic validation
   ↓
5. Review and merge
   ↓
6. Application live on Olares Market
```

### Step 1: Fork Official Repository

**Repository:** https://github.com/beclab/apps

```bash
# Fork via GitHub UI, then clone your fork
git clone https://github.com/YOUR_USERNAME/apps.git
cd apps
```

### Step 2: Prepare Application Chart

**Directory Structure:**
```
apps/
└── myapp/                              # Your application folder
    ├── Chart.yaml                      # REQUIRED
    ├── OlaresManifest.yaml            # REQUIRED
    ├── owners                          # REQUIRED (GitHub usernames)
    ├── README.md                       # Recommended
    ├── templates/
    │   ├── deployment.yaml
    │   └── service.yaml
    └── values.yaml                     # Optional
```

**Create `owners` file:**
```bash
# Add your GitHub username (one per line)
echo "your-github-username" > myapp/owners
```

**Example `owners` file:**
```
longzhi
another-contributor
```

### Step 3: Prepare Application Assets

**Asset Requirements:**

| Asset Type | Format | Size Limit | Dimensions | Required |
|-----------|--------|------------|------------|----------|
| Icon | PNG/WEBP | ≤512 KB | 256x256 px | ✅ YES |
| Screenshots | JPEG/PNG/WEBP | ≤8 MB each | 1440x900 px | ⚠️ Recommended (2-8) |
| Featured Image | JPEG/PNG/WEBP | ≤8 MB | 1440x900 px | Optional |

**Add assets to OlaresManifest.yaml:**
```yaml
metadata:
  icon: https://example.com/icon.webp

spec:
  promoteImage:
    - https://example.com/screenshot1.png
    - https://example.com/screenshot2.png
  featuredImage: https://example.com/featured.webp
```

### Step 4: Create Pull Request

**PR Title Format (CRITICAL):**
```
[PR_TYPE][FolderName][version]Title Content

Examples:
[NEW][myapp][0.1.0]My awesome application
[UPDATE][myapp][0.2.0]Fixed bugs and improved performance
[SUSPEND][myapp][0.1.0]Temporarily suspend distribution
[REMOVE][myapp][0.1.0]Remove application from market
```

**PR Types:**
| Type | Description | Use Case |
|------|-------------|----------|
| `NEW` | Submit new application | First-time submission |
| `UPDATE` | Update existing application | Bug fixes, new features, version upgrade |
| `SUSPEND` | Temporarily disable distribution | Need to pause downloads |
| `REMOVE` | Permanently remove application | Complete removal from market |

**PR Title Rules:**
- ✅ Must contain exactly ONE PR type, folder name, and version
- ✅ PR type must be one of: NEW, UPDATE, SUSPEND, REMOVE
- ✅ Folder name must match your chart directory name
- ✅ Version must match Chart.yaml and OlaresManifest.yaml
- ❌ Do NOT modify PR title after GitBot labels it

**Create Draft PR:**
```bash
# Commit your changes
git add myapp/
git commit -m "Add myapp application"
git push origin main

# Create Draft PR via GitHub UI:
# 1. Go to https://github.com/beclab/apps
# 2. Click "Pull Requests" → "New Pull Request"
# 3. Select your fork and branch
# 4. Click "Create Draft Pull Request"
# 5. Fill in PR title following the format above
```

### Step 5: PR Validation and Review

**GitBot Automatic Checks:**

GitBot will automatically validate:
- ✅ PR title format is correct
- ✅ Only one PR exists for this folder
- ✅ Submitter is listed in `owners` file
- ✅ Chart.yaml and OlaresManifest.yaml versions match
- ✅ All required files present
- ✅ No `.suspend` or `.remove` files in NEW submissions

**PR Status Labels:**

| Label | Meaning | Action Required |
|-------|---------|-----------------|
| `PR type` | PR title is valid | Continue working |
| `waiting to submit` | Issues found, needs modification | Fix issues and push new commits |
| `waiting to merge` | All checks passed | Wait for auto-merge |
| `merged` | PR merged successfully | Application will appear in Market |
| `closed` | PR has irreparable issues | Create new PR after fixing |

**During Draft Phase:**
- ✅ You can continuously commit and push changes
- ✅ GitBot will NOT check until you mark "Ready for review"
- ✅ Take your time to perfect your submission

**Ready for Review:**
```
1. Click "Ready for review" button
2. GitBot starts automatic validation
3. Check PR comments for any issues
4. If issues found, push fixes
5. GitBot will re-check on new commits
```

### Step 6: Update Existing Application

**Version Requirements:**
- ✅ New version MUST be greater than current version
- ✅ Use semantic versioning: MAJOR.MINOR.PATCH
- ✅ Update both Chart.yaml and OlaresManifest.yaml
- ❌ No version rollback supported

**Update PR Title Format:**
```
[UPDATE][myapp][0.2.0]Added new features and fixed bugs
```

**Update Workflow:**
```bash
# Sync your fork with upstream
git remote add upstream https://github.com/beclab/apps.git
git fetch upstream
git rebase upstream/main

# Update your application
# - Modify files in myapp/
# - Bump version in Chart.yaml and OlaresManifest.yaml
# - Update README.md with changes

git add myapp/
git commit -m "Update myapp to v0.2.0"
git push origin main

# Create UPDATE PR with proper title format
```

### Step 7: Suspend Application

To temporarily stop distribution:

**PR Title:**
```
[SUSPEND][myapp][0.1.0]Temporarily suspend for maintenance
```

**Requirements:**
- ✅ Version must MATCH current version in repository
- ✅ Add `.suspend` file to chart root directory
- ❌ Do NOT include `.remove` file

**Create `.suspend` file:**
```bash
touch myapp/.suspend
git add myapp/.suspend
git commit -m "Suspend myapp"
git push origin main
```

**After Suspension:**
- Application stops appearing in Market
- Users who already installed can continue using it
- You can lift suspension with an UPDATE PR (remove `.suspend` file)

### Step 8: Remove Application

To permanently remove from Market:

**PR Title:**
```
[REMOVE][myapp][0.1.0]Remove application permanently
```

**Requirements:**
- ✅ Empty ALL files in application directory
- ✅ Add `.remove` file to chart root directory
- ⚠️ **IRREVERSIBLE**: Cannot reuse the same name/folder

**Remove Workflow:**
```bash
# Empty all files except .remove
rm -rf myapp/*
touch myapp/.remove

git add myapp/
git commit -m "Remove myapp permanently"
git push origin main

# Create REMOVE PR
```

**After Removal:**
- Application completely removed from Market
- Users who already installed can continue using it
- You CANNOT reuse the folder name or application name

### Troubleshooting Submission

**Issue: GitBot closed my PR**
- ✅ Create a NEW PR (do NOT reopen)
- ✅ Fix issues mentioned in PR comments
- ✅ Ensure PR title format is correct

**Issue: "Not an owner" error**
- ✅ Check `owners` file includes your GitHub username
- ✅ Username must be exact match (case-sensitive)

**Issue: "Version conflict" error**
- ✅ Ensure Chart.yaml version matches OlaresManifest.yaml
- ✅ For UPDATE, version must be greater than current
- ✅ Use semantic versioning format

**Issue: "Invalid PR title" error**
- ✅ Check PR title format: `[TYPE][folder][version]Title`
- ✅ PR type must be: NEW, UPDATE, SUSPEND, or REMOVE
- ✅ Folder name must match your chart directory
- ✅ Do NOT include extra brackets or special characters

### Collaboration and Ownership

**Add Multiple Owners:**
```
# owners file
alice
bob
charlie
```

**Two Collaboration Methods:**

**Method 1: Multiple Owners (Recommended)**
- Add all collaborators to `owners` file
- Each can fork and submit PRs independently
- All share ownership and maintenance responsibility

**Method 2: Repository Collaborators**
- Add others as collaborators to your fork
- They can push to your fork's branch
- You create PR as representative
- Only main submitter needs to be in `owners` file

---

## Development Workflow Summary

### Publish to Olares

```bash
# 1. Develop application locally or in OpenCode
# 2. Publish to Olares
olares-deploy myapp python:3.11-slim 8080 "python app.py"

# 3. Update Nginx
python3 /root/.local/bin/olares-nginx-config

# 4. Access at: https://xxx-3000.domain.com/myapp/
# 5. View logs: olares-manage logs myapp
```

---

## Common Patterns

### Pattern: Web App with PostgreSQL

```yaml
# OlaresManifest.yaml
middleware:
  postgres:
    username: webapp
    password: {{ .Values.postgres.password }}
    databases:
      - name: webapp_db
        distributed: false

entrances:
  - name: webapp
    host: webapp-svc
    port: 3000
    authLevel: private
```

### Pattern: API Service (No UI)

```yaml
# OlaresManifest.yaml - No entrances defined
# Service runs as background process
entrances: []

# Or with internal-only access:
entrances:
  - name: api
    host: api-svc
    port: 8080
    authLevel: internal   # Only accessible within cluster
```

### Pattern: Sidecar with Existing App

```yaml
# OlaresManifest.yaml
options:
  dependencies:
    - name: some-app
      type: application
      version: ">=1.0.0"
```

---

## Troubleshooting

### App Not Starting

1. Check container logs via `olares-manage logs <app-name>`
2. Verify image exists and is pullable
3. Check resource limits (memory/CPU too low?)

### Database Connection Failed

1. Verify middleware section in OlaresManifest.yaml
2. Check environment variable names match your app's expectations
3. Ensure database name in `.Values.postgres.databases.<name>` matches

### Permission Denied

1. Check `permission` section in OlaresManifest.yaml
2. Verify volume mount paths match declared permissions
3. Check `authLevel` in entrances

### App Not Appearing in Desktop

1. Verify `entrances` section is correctly configured
2. Check `metadata.name` matches `Chart.yaml` name
3. Ensure icon URL is accessible

---

## Quick Reference Commands

```bash
# Package chart
helm package myapp/

# Validate chart locally
helm lint myapp/

# Template render (debug)
helm template myapp myapp/ --debug

# Olares deployment
olares-deploy myapp python:3.11-slim 8080 "python app.py"

# Update Nginx reverse proxy
python3 /root/.local/bin/olares-nginx-config

# Manage deployed apps
olares-manage list
olares-manage info myapp
olares-manage logs myapp
olares-manage delete myapp

# Display all URLs
olares-urls
```

---

## Official Resources

- **Market Repository**: https://github.com/beclab/apps
- **Documentation**: https://docs.olares.com/developer/
- **Chart Structure**: https://docs.olares.com/developer/develop/package/chart.html
- **OlaresManifest**: https://docs.olares.com/developer/develop/package/manifest.html
- **Submission Guide**: https://docs.olares.com/developer/develop/submit/

---

## Example Applications

Study these reference implementations:
- `affine` - Complex app with multiple services
- `wordpress` - Database-backed web app
- `n8n` - Automation platform with Redis

Browse all: https://github.com/beclab/apps
