# Olares Application Development Skill

## Trigger Conditions

Use this skill when:
- User wants to deploy an application to Olares
- User mentions "Olares", "Terminus" (legacy name), or self-hosted cloud
- Task involves creating Helm charts for Olares ecosystem
- User needs to package a Docker image as an Olares app
- Database provisioning (PostgreSQL, Redis, MongoDB, etc.) on Olares is needed

## Overview

Olares is a self-hosted cloud operating system. Applications are deployed as Helm charts with an additional `OlaresManifest.yaml` configuration file.

**Key Concepts:**
- **Olares Application Chart** = Standard Helm Chart + `OlaresManifest.yaml`
- **No REST API** for deployment - use Studio UI or olares-cli
- **System Services**: PostgreSQL, Redis, MongoDB, Zinc (search) are pre-installed
- **User Isolation**: Each user gets isolated app instances

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
