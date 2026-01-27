# Olares Application Development Skill

## Trigger Conditions

Use this skill when:
- User wants to deploy an application to Olares
- User mentions "Olares", "Terminus" (legacy name), or self-hosted cloud
- Task involves creating Helm charts for Olares ecosystem
- User needs to package a Docker image as an Olares app
- Database provisioning (PostgreSQL, Redis, MongoDB, etc.) on Olares is needed
- **User completes development and needs to deploy to Olares DevBox (AUTOMATIC)**
- **User asks to "deploy", "publish", or "make it accessible" after development**

## Overview

Olares is a self-hosted cloud operating system. Applications are deployed as Helm charts with an additional `OlaresManifest.yaml` configuration file.

**Key Concepts:**
- **Olares Application Chart** = Standard Helm Chart + `OlaresManifest.yaml`
- **No REST API** for deployment - use Studio UI or olares-cli
- **System Services**: PostgreSQL, Redis, MongoDB, Zinc (search) are pre-installed
- **User Isolation**: Each user gets isolated app instances

**TWO DEPLOYMENT METHODS:**
1. **DevBox Quick Deploy** (Recommended for development) - Direct kubectl deployment, automatic external access
2. **Market Package** (For publishing) - Helm chart package via Studio UI

---

## 🚀 DEVBOX QUICK DEPLOY (Automatic Deployment After Development)

**When to Use:** User completes application development in OpenCode and wants immediate deployment.

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

### Quick Deploy Script

**Location:** `/tmp/opencode-deploy-v2.sh`

**Usage:**
```bash
/tmp/opencode-deploy-v2.sh <app-name> <image> <port> [startup-command]
```

**Script ensures it exists and is executable:**
```bash
if [ ! -f /tmp/opencode-deploy-v2.sh ]; then
    echo "ERROR: Deployment script not found!"
    echo "The script should be at /tmp/opencode-deploy-v2.sh"
    exit 1
fi
chmod +x /tmp/opencode-deploy-v2.sh
```

### Automatic Deployment Workflow

**When user completes development:**

1. **Detect Application Type**
   ```python
   frameworks = {
       'flask': {'image': 'python:3.11-slim', 'port': 5000, 'detect': 'app.py with Flask'},
       'fastapi': {'image': 'python:3.11-slim', 'port': 8000, 'detect': 'main.py with FastAPI'},
       'express': {'image': 'node:20-slim', 'port': 3000, 'detect': 'package.json with express'},
       'django': {'image': 'python:3.11-slim', 'port': 8000, 'detect': 'manage.py'}
   }
   ```

2. **Generate App Name**
   ```python
   import re
   app_name = re.sub(r'[^a-z0-9-]', '-', user_provided_name.lower())
   app_name = app_name.strip('-')[:50]  # Max 50 chars
   ```

3. **Build Startup Command**
   - Flask: `pip install flask && python app.py`
   - FastAPI: `pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 8000`
   - Express: `npm install && npm start`
   - Django: `pip install django && python manage.py runserver 0.0.0.0:8000`

4. **Execute Deployment**
   ```bash
   /tmp/opencode-deploy-v2.sh "$APP_NAME" "$IMAGE" "$PORT" "$COMMAND"
   ```

5. **Extract External URL**
   ```bash
   # Get the third-level domain from deployment
   THIRD_LEVEL=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
       -o jsonpath='{.metadata.annotations.applications\.app\.bytetrade\.io/default-thirdlevel-domains}' \
       | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['thirdLevelDomain'])")
   
   # Get user's Olares domain from namespace or config
   DOMAIN="onetest02.olares.com"  # Extract from environment
   
   EXTERNAL_URL="https://${THIRD_LEVEL}.${DOMAIN}"
   ```

6. **Report to User**
   ```
   ✅ Deployment successful!
   
   Your application is now live:
   🌐 External URL: https://xxxxx-5000.onetest02.olares.com
   
   Internal URL (cluster only):
   http://app-name-svc.namespace.svc.cluster.local:5000
   
   View logs: /tmp/opencode-manage.sh logs app-name
   Manage: /tmp/opencode-manage.sh info app-name
   ```

### External Access Configuration

**Olares URL Format:**
```
https://{random-hash}-{port}.{username}.olares.com

Example:
https://dd176ae5-5000.onetest02.olares.com
         ↑          ↑      ↑
    random hash  port   username
```

**Required Annotations** (automatically added by script):
```yaml
annotations:
  meta.helm.sh/release-name: app-name
  meta.helm.sh/release-namespace: namespace
  applications.app.bytetrade.io/entrances: '[{"name":"app-name","host":"app-name-svc","port":5000,"title":"app-name","authLevel":"private","openMethod":"default"}]'
  applications.app.bytetrade.io/default-thirdlevel-domains: '[{"appName":"app-name","entranceName":"app-name","thirdLevelDomain":"random-hash-port"}]'
  applications.app.bytetrade.io/icon: https://app.cdn.olares.com/appstore/default/defaulticon.webp
  applications.app.bytetrade.io/title: app-name
```

### Management Commands

**Location:** `/tmp/opencode-manage.sh`

```bash
# List all deployed apps
/tmp/opencode-manage.sh list

# Show app details and URL
/tmp/opencode-manage.sh info <app-name>

# View logs
/tmp/opencode-manage.sh logs <app-name>
/tmp/opencode-manage.sh logs <app-name> -f  # Follow

# Test connectivity
/tmp/opencode-manage.sh test <app-name>

# Delete app
/tmp/opencode-manage.sh delete <app-name>
```

### Display All External URLs

**Location:** `/tmp/opencode-urls.sh`

```bash
# Show all deployed apps with external URLs
/tmp/opencode-urls.sh
```

Output:
```
═══════════════════════════════════════════════
  OpenCode 部署的应用 - 外部访问地址
═══════════════════════════════════════════════

▶ flask-app
  状态: ✅ Running (1/1)
  端口: 5000
  外部访问: https://dd176ae5-5000.onetest02.olares.com
  集群内部: http://flask-app-svc.namespace.svc.cluster.local:5000

▶ express-api
  状态: ✅ Running (1/1)
  端口: 3000
  外部访问: https://c113fc1b-3000.onetest02.olares.com
  集群内部: http://express-api-svc.namespace.svc.cluster.local:3000
```

### Network Architecture

**New Architecture (Unified Entry + Nginx Reverse Proxy):**
```
User Browser
    ↓ HTTPS
https://b0c54349-3000.onetest02.olares.com/{app-name}/
    ↓ DNS Resolution
Olares Ingress Controller (TLS termination)
    ↓ HTTP
OpenCode Container (port 3000 - unified entry)
    ↓
Nginx Reverse Proxy (listening on 3000)
    ↓ Path-based routing
    ├─ /express-demo/ → express-demo-svc:3000
    ├─ /flask-app/    → flask-app-svc:5000
    ├─ /test-app/     → test-app-svc:8000
    └─ /opencode/     → localhost:4096 (OpenCode Server mode)
    ↓
Service: app-name-svc (ClusterIP)
    ↓ TCP
Pod: app-name-xxx (10.233.x.x:port)
    ↓
Application (0.0.0.0:port)
```

**Key Points:**
- **Unified Entry**: All external requests come through port 3000 (OpenCode default)
- **Path Routing**: Different URL paths map to different services
- **Automatic Configuration**: Nginx configs auto-generated for each deployment
- **Fixed OpenCode Mapping**: Port 4096 always mapped for OpenCode Server mode

**Legacy Architecture (Direct Service Access - Deprecated):**
```
User Browser
    ↓ HTTPS
https://xxxxx-5000.onetest02.olares.com
    ↓ DNS Resolution
Olares Ingress Controller
    ↓ HTTP (internal)
Service: app-name-svc (ClusterIP:5000)
    ↓ TCP
Pod: app-name-xxx (10.233.x.x:5000)
    ↓
Application (0.0.0.0:5000)
```

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
Olares Nginx 配置生成器
============================================================

1. 扫描已部署的应用...
  找到 3 个应用:
    - express-demo (端口 3000)
    - flask-app (端口 5000)
    - test-app (端口 8000)

2. 生成 Nginx 配置...
✓ 生成配置: /etc/nginx/conf.d/dev/express-demo.conf
✓ 生成配置: /etc/nginx/conf.d/dev/flask-app.conf
✓ 生成配置: /etc/nginx/conf.d/dev/test-app.conf
✓ 生成固定配置: /etc/nginx/conf.d/dev/opencode-server.conf (port 4096)

3. 应用配置...
✓ Nginx 配置测试通过
✓ Nginx 重载成功

✅ 配置完成！
```

#### External Access URLs

After Nginx configuration, applications are accessible via:

**Pattern 1: Application Name Path**
```
https://{hash}-3000.{domain}/{app-name}/

Examples:
https://b0c54349-3000.onetest02.olares.com/express-demo/
https://b0c54349-3000.onetest02.olares.com/flask-app/
https://b0c54349-3000.onetest02.olares.com/test-app/
```

**Pattern 2: Port Number Path**
```
https://{hash}-3000.{domain}/{port}/

Examples:
https://b0c54349-3000.onetest02.olares.com/3000/  → express-demo
https://b0c54349-3000.onetest02.olares.com/5000/  → flask-app
https://b0c54349-3000.onetest02.olares.com/8000/  → test-app
```

**Fixed: OpenCode Server Mode**
```
https://{hash}-3000.{domain}/opencode/  → localhost:4096

Example:
https://b0c54349-3000.onetest02.olares.com/opencode/
```

#### Nginx Configuration Details

**Generated Config Structure:**
```nginx
# /etc/nginx/conf.d/dev/app-name.conf

# Route by application name
location /app-name/ {
    proxy_pass http://app-name-svc.namespace.svc.cluster.local:port/;
    proxy_http_version 1.1;
    
    # Standard headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support (critical for code-server, etc.)
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
location /port/ {
    proxy_pass http://app-name-svc.namespace.svc.cluster.local:port/;
    # ... same config as above
}
```

**Fixed OpenCode Server Config:**
```nginx
# /etc/nginx/conf.d/dev/opencode-server.conf

# OpenCode Server mode (always on port 4096)
location /opencode/ {
    proxy_pass http://localhost:4096/;
    proxy_http_version 1.1;
    
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Critical for OpenCode Server WebSocket connections
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    
    # Long timeout for persistent connections
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
/root/.local/bin/olares-deploy my-app python:3.11-slim 5000 "python app.py"

# Step 2: Update Nginx reverse proxy (MANDATORY)
python3 /root/.local/bin/olares-nginx-config

# Step 3: Access application
# https://b0c54349-3000.onetest02.olares.com/my-app/
```

**Automated Integration:**

The deployment script at `/root/.local/bin/olares-deploy` can be modified to automatically trigger Nginx configuration update:

```bash
# Add at the end of olares-deploy script
if [ -f /root/.local/bin/olares-nginx-config ]; then
    echo ""
    log_step "更新 Nginx 反向代理配置..."
    python3 /root/.local/bin/olares-nginx-config > /dev/null 2>&1 || true
    echo "✓ Nginx 配置已更新"
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

#### Health Check Endpoint

Nginx includes a health check endpoint for monitoring:

```bash
# Test health endpoint
curl http://localhost:3000/health
# Expected: healthy

# External access
https://b0c54349-3000.onetest02.olares.com/health
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
| `admission webhook denied` | Missing annotations | Use v2 script with proper annotations |

### Example: Complete Automated Flow (UPDATED)

**User says:** "I built a Flask todo app, deploy it"

**AI Response (Updated with Nginx Reverse Proxy):**
```
I'll deploy your Flask app to Olares right away!

Detecting configuration...
✓ Framework: Flask
✓ Image: python:3.11-slim
✓ Port: 5000
✓ App name: flask-todo-app

Deploying to Olares...
[Executing: /root/.local/bin/olares-deploy flask-todo-app python:3.11-slim 5000 "pip install flask && python app.py"]

✅ Deployment successful!

Updating Nginx reverse proxy...
[Executing: python3 /root/.local/bin/olares-nginx-config]
✓ Nginx 配置已更新
✓ 为 flask-todo-app 生成反向代理配置

Your Flask todo app is now live at:
🌐 https://b0c54349-3000.onetest02.olares.com/flask-todo-app/

Alternative access methods:
• By port: https://b0c54349-3000.onetest02.olares.com/5000/
• Internal: http://flask-todo-app-svc.namespace.svc.cluster.local:5000

The app is running in an isolated Pod with:
- CPU: 100m-500m
- Memory: 128Mi-512Mi
- Auto-scaling: Ready (if needed)

Access through unified entry point (port 3000) with path-based routing.

You can view logs with:
/root/.local/bin/olares-manage logs flask-todo-app

Or manage it via:
/root/.local/bin/olares-manage info flask-todo-app
```

**Key Changes from Legacy Flow:**
1. ✅ Uses unified entry point (port 3000) instead of individual ports
2. ✅ Automatically updates Nginx reverse proxy after deployment
3. ✅ Provides path-based URL: `/{app-name}/` instead of separate domain
4. ✅ Includes fixed OpenCode Server mapping on port 4096

**Legacy vs New:**
| Aspect | Legacy | New (Current) |
|--------|--------|---------------|
| Access URL | `https://{hash}-5000.domain` | `https://{hash}-3000.domain/flask-todo-app/` |
| Entry Point | Multiple ports (3000, 5000, 8000...) | Single port (3000) |
| Routing | Direct service access | Nginx reverse proxy (path-based) |
| Configuration | Manual for each port | Automatic Nginx config generation |
| OpenCode Server | Not configured | Fixed mapping at `/opencode/` → port 4096 |

---

## 📦 MARKET PACKAGE DEPLOYMENT (For Publishing)

For apps intended for Olares Market or formal distribution, use the traditional Helm chart method below.

---

## Application Package Structure

```
myapp/
├── Chart.yaml              # Helm chart metadata
├── OlaresManifest.yaml     # Olares-specific configuration (REQUIRED)
├── templates/
│   ├── deployment.yaml     # Kubernetes deployment
│   └── service.yaml        # Kubernetes service (if needed)
├── values.yaml             # Default values (optional)
└── README.md               # Documentation (optional)
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

## Development Workflow

### Method A: Quick Deploy (Existing Docker Image)

If you already have a containerized application:

1. **Create chart structure:**
   ```bash
   mkdir -p myapp/templates
   ```

2. **Create Chart.yaml, OlaresManifest.yaml, deployment.yaml, service.yaml**
   (use templates above)

3. **Package:**
   ```bash
   # Using Helm
   helm package myapp/
   
   # Or using olares-cli (if available)
   olares-cli olares package myapp/
   ```

4. **Deploy via Studio UI:**
   - Open Olares Desktop → DevBox → Studio
   - Click "Upload" → Select .tgz file
   - Click "Install"

### Method B: Full Development (DevBox)

For developing within Olares environment:

1. **Create Dev Container:**
   - DevBox → Containers → Create
   - Select base image (e.g., `node:20`, `python:3.11`)
   - Configure resources (CPU, Memory, Storage)

2. **Develop in Container:**
   - Access via code-server (VS Code in browser)
   - Develop and test your application

3. **Create Chart:**
   - Follow Method A for packaging

4. **Test Installation:**
   - Studio → Upload → Install
   - Check logs: DevBox → Containers → Logs

---

## Deployment Process (Studio UI)

Since Olares has no REST API, deployment must go through UI:

### Manual Steps:

1. **Access Studio:**
   ```
   https://desktop.<your-olares-domain>/studio
   ```

2. **Upload Package:**
   - Click "Custom" tab
   - Click "Upload" button
   - Select your `.tgz` chart package

3. **Configure (if options defined):**
   - Fill any user-configurable options

4. **Install:**
   - Click "Install"
   - Wait for deployment to complete

5. **Verify:**
   - Check app appears in Olares desktop
   - Check container logs in DevBox if issues occur

### Automation with Playwright:

For automated deployment, use Playwright to interact with Studio UI:

```typescript
// Example: Automated deployment script
async function deployToOlares(chartPath: string) {
  const page = await browser.newPage();
  await page.goto('https://desktop.your-olares.com/studio');
  
  // Navigate to Custom tab
  await page.click('text=Custom');
  
  // Upload chart
  const fileInput = await page.locator('input[type="file"]');
  await fileInput.setInputFiles(chartPath);
  
  // Wait for upload and click Install
  await page.click('button:has-text("Install")');
  
  // Wait for completion
  await page.waitForSelector('text=Installed', { timeout: 60000 });
}
```

---

## Publishing to Market (Optional)

To publish your app to the official Olares Market:

1. **Fork repository:** https://github.com/beclab/apps

2. **Add your chart:**
   ```
   apps/
   └── myapp/
       ├── Chart.yaml
       ├── OlaresManifest.yaml
       └── templates/
   ```

3. **Submit PR** with:
   - Clear description
   - Screenshots (if UI app)
   - Testing evidence

4. **Review Process:**
   - Automated validation
   - Manual review by Olares team
   - Merge and publish to Market

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

1. Check container logs in DevBox → Containers
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

# Using olares-cli (if installed)
olares-cli olares package myapp/
olares-cli olares lint myapp/
```

---

## Examples Repository

Reference implementations: https://github.com/beclab/apps

Recommended apps to study:
- `affine` - Complex app with multiple services
- `wordpress` - Database-backed web app
- `n8n` - Automation platform with Redis
