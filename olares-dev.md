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
- **User wants to submit application to Olares Market**
- **User needs to package and publish an Olares application**

## Overview

Olares is a self-hosted cloud operating system. Applications are deployed as Helm charts with an additional `OlaresManifest.yaml` configuration file.

**Key Concepts:**
- **Olares Application Chart** = Standard Helm Chart + `OlaresManifest.yaml`
- **No REST API** for deployment - use Studio UI or olares-cli
- **System Services**: PostgreSQL, Redis, MongoDB, Zinc (search) are pre-installed
- **User Isolation**: Each user gets isolated app instances

**THREE DEPLOYMENT METHODS:**
1. **DevBox Quick Deploy** (Development) - Direct kubectl deployment with automatic external access
2. **Market Package** (Publishing) - Helm chart package for Olares Market submission
3. **GitHub Submission** (Public Distribution) - Submit to official Olares Market repository

---

## 🚀 DEVBOX QUICK DEPLOY (Automatic Deployment After Development)

**When to Use:** User completes application development in OpenCode and wants immediate deployment for testing.

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

### Quick Deploy Tools

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

**Examples:**
```bash
# Deploy Flask app
olares-deploy flask-app python:3.11-slim 5000 "pip install flask && python app.py"

# Deploy Express.js app
olares-deploy express-demo node:20-slim 3000 "npm install && npm start"

# Deploy FastAPI app
olares-deploy api-server python:3.11-slim 8000 "pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0"
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
   /root/.local/bin/olares-deploy "$APP_NAME" "$IMAGE" "$PORT" "$COMMAND"
   ```

5. **Update Nginx Reverse Proxy (MANDATORY)**
   ```bash
   python3 /root/.local/bin/olares-nginx-config
   ```

6. **Extract External URL**
   ```bash
   # Get the third-level domain from deployment
   THIRD_LEVEL=$(kubectl get deployment "$APP_NAME" -n "$NAMESPACE" \
       -o jsonpath='{.metadata.annotations.applications\.app\.bytetrade\.io/default-thirdlevel-domains}' \
       | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['thirdLevelDomain'])")
   
   # Get user's Olares domain from namespace or config
   DOMAIN="{username}.olares.com"  # Extract from environment
   
   EXTERNAL_URL="https://${THIRD_LEVEL}.${DOMAIN}"
   ```

7. **Report to User**
   ```
   ✅ Deployment successful!
   
   Your application is now live:
   🌐 External URL: https://{app-id}-3000.{username}.olares.com/app-name/
   
   Alternative access:
   • By port: https://{app-id}-3000.{username}.olares.com/5000/
   • Internal: http://app-name-svc.namespace.svc.cluster.local:5000
   
   Manage your app:
   • View logs: olares-manage logs app-name
   • Check status: olares-manage info app-name
   • List all apps: olares-urls
   ```

### External Access Configuration

**Olares URL Format:**
```
https://{appid}-{port}.{username}.olares.com/{path}

Example:
https://{app-id}-3000.{username}.olares.com/flask-app/
         ↑          ↑      ↑            ↑
      app id     port   username    app path
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

### Display All External URLs

**Location:** `/root/.local/bin/olares-urls`

```bash
# Show all deployed apps with external URLs
olares-urls
```

**Output:**
```
═══════════════════════════════════════════════
  OpenCode Deployed Applications
═══════════════════════════════════════════════

▶ flask-app
  Status: ✅ Running (1/1)
  Port: 5000
  External: https://{app-id}-3000.{username}.olares.com/flask-app/
  Internal: http://flask-app-svc.namespace.svc.cluster.local:5000

▶ express-api
  Status: ✅ Running (1/1)
  Port: 3000
  External: https://{app-id}-3000.{username}.olares.com/express-api/
  Internal: http://express-api-svc.namespace.svc.cluster.local:3000
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
    ├─ /express-demo/ → express-demo-svc:3000
    ├─ /flask-app/    → flask-app-svc:5000
    └─ /test-app/     → test-app-svc:8000
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
   Found 3 applications:
     - express-demo (port 3000)
     - flask-app (port 5000)
     - test-app (port 8000)

2. Generating Nginx configurations...
✓ Generated config: /etc/nginx/conf.d/dev/express-demo.conf
✓ Generated config: /etc/nginx/conf.d/dev/flask-app.conf
✓ Generated config: /etc/nginx/conf.d/dev/test-app.conf
✓ Generated fixed config: /etc/nginx/conf.d/dev/opencode-server.conf (port 4096)

3. Applying configuration...
✓ Nginx configuration test passed
✓ Nginx reloaded successfully

✅ Configuration complete!
```

#### External Access URLs

After Nginx configuration, applications are accessible via:

**Pattern 1: Application Name Path (Recommended)**
```
https://{hash}-3000.{domain}/{app-name}/

Examples:
https://{app-id}-3000.{username}.olares.com/express-demo/
https://{app-id}-3000.{username}.olares.com/flask-app/
https://{app-id}-3000.{username}.olares.com/test-app/
```

**Pattern 2: Port Number Path**
```
https://{hash}-3000.{domain}/{port}/

Examples:
https://{app-id}-3000.{username}.olares.com/3000/  → express-demo
https://{app-id}-3000.{username}.olares.com/5000/  → flask-app
https://{app-id}-3000.{username}.olares.com/8000/  → test-app
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
location /port/ {
    proxy_pass http://app-name-svc.namespace.svc.cluster.local:port/;
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
olares-deploy my-app python:3.11-slim 5000 "python app.py"

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

### Example: Complete Automated Flow

**User says:** "I built a Flask todo app, deploy it"

**AI Response:**
```
I'll deploy your Flask app to Olares right away!

Detecting configuration...
✓ Framework: Flask
✓ Image: python:3.11-slim
✓ Port: 5000
✓ App name: flask-todo-app

Deploying to Olares...
[Executing: olares-deploy flask-todo-app python:3.11-slim 5000 "pip install flask && python app.py"]

✅ Deployment successful!

Updating Nginx reverse proxy...
[Executing: python3 /root/.local/bin/olares-nginx-config]
✓ Nginx configuration updated
✓ Generated reverse proxy config for flask-todo-app

Your Flask todo app is now live at:
🌐 https://{app-id}-3000.{username}.olares.com/flask-todo-app/

Alternative access methods:
• By port: https://{app-id}-3000.{username}.olares.com/5000/
• Internal: http://flask-todo-app-svc.namespace.svc.cluster.local:5000

The app is running in an isolated Pod with:
- CPU: 100m-500m
- Memory: 128Mi-512Mi
- Auto-scaling: Ready (if needed)

Access through unified entry point (port 3000) with path-based routing.

You can view logs with:
olares-manage logs flask-todo-app

Or manage it via:
olares-manage info flask-todo-app
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

## 🚀 GITHUB SUBMISSION (Olares Market Publishing)

To publish your application to the official Olares Market, you must submit it through GitHub.

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

### Quick Development Test (DevBox)

```bash
# 1. Develop application locally or in OpenCode
# 2. Deploy for testing
olares-deploy myapp python:3.11-slim 5000 "python app.py"

# 3. Update Nginx
python3 /root/.local/bin/olares-nginx-config

# 4. Test at: https://xxx-3000.domain.com/myapp/
# 5. View logs: olares-manage logs myapp
```

### Package for Studio Upload

```bash
# 1. Create chart structure
mkdir -p myapp/templates

# 2. Create Chart.yaml, OlaresManifest.yaml, deployment.yaml, service.yaml

# 3. Package
helm package myapp/

# 4. Upload via Studio UI → Custom → Upload → myapp-0.1.0.tgz
```

### Publish to Market

```bash
# 1. Fork https://github.com/beclab/apps
git clone https://github.com/YOUR_USERNAME/apps.git

# 2. Add your chart
cp -r myapp/ apps/

# 3. Create owners file
echo "your-github-username" > apps/myapp/owners

# 4. Commit and push
git add apps/myapp/
git commit -m "Add myapp application"
git push origin main

# 5. Create PR with title: [NEW][myapp][0.1.0]My Application

# 6. Mark "Ready for review" when ready

# 7. Wait for GitBot validation and auto-merge
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

# DevBox deployment
olares-deploy myapp python:3.11-slim 5000 "python app.py"

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
