# ✅ Nginx Reverse Proxy Configuration Complete

## 🎯 Architecture Overview

```
External Request
  ↓
https://{hash}-3000.{username}.olares.com/{app-path}/
  ↓
Olares Ingress Controller
  ↓
OpenCode Container
  ↓
Nginx (listening on port 3000 - unified entry)
  ↓ Route based on Path
  └─ /my-app/        → my-app-svc:8080
```

**Key Design**:
- ✅ **Unified Entry**: All requests enter through port 3000
- ✅ **Path Routing**: Different applications based on URL path
- ✅ **Automatic Configuration**: Scan Kubernetes deployments, auto-generate Nginx configs

---

## 📦 Deployed Components

### 1. Nginx Configuration
- **Main config**: `/etc/nginx/nginx.conf`
- **Default server**: `/etc/nginx/conf.d/default.conf` (listening on 3000)
- **Application proxy configs**: `/etc/nginx/conf.d/dev/*.conf` (auto-generated)

### 2. Automation Tools
- **Configuration generator**: `/root/.local/bin/olares-nginx-config`

---

## 🚀 Usage

### Auto-Generate All Application Proxy Configurations
```bash
python3 /root/.local/bin/olares-nginx-config
```

Example output:
```
Olares Nginx Configuration Generator
============================================================

1. Scanning deployed applications...
   Found 1 application:
     - my-app (port 8080)

2. Generating Nginx configurations...
✓ Generated config: /etc/nginx/conf.d/dev/my-app.conf

3. Applying configuration...
✓ Nginx configuration test passed
✓ Nginx reloaded successfully

✅ Configuration complete!
```

### Check Nginx Status
```bash
python3 /root/.local/bin/olares-nginx-config status
```

### Manually Reload Nginx
```bash
nginx -s reload
```

### View Generated Configuration
```bash
cat /etc/nginx/conf.d/dev/express-demo.conf
```

---

## 🌐 Accessing Applications

### Access by Application Name
```
http://localhost:3000/my-app/
```

### Access by Port Number
```
http://localhost:3000/8080/  → my-app
```

### External Access (via Olares Ingress)
```
https://{hash}-3000.{username}.olares.com/my-app/
```

---

## 📝 Configuration Examples

### Generated Nginx Configuration Structure
```nginx
# /etc/nginx/conf.d/dev/my-app.conf

# Access by application name
location /my-app/ {
    proxy_pass http://my-app-svc.{namespace}.svc.cluster.local:8080/;
    proxy_http_version 1.1;
    
    # Standard proxy headers
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket support (important for code-server, etc.)
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    
    # Timeout settings (support for long connections)
    proxy_connect_timeout 60s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
    
    # Disable buffering (support for real-time responses)
    proxy_buffering off;
    proxy_request_buffering off;
}

# Access by port number
location /8080/ {
    proxy_pass http://my-app-svc.{namespace}.svc.cluster.local:8080/;
    # ... same config
}
```

---

## 🔧 Integration into Deployment Workflow

### Method 1: Manual Integration
Run after deploying each new application:
```bash
python3 /root/.local/bin/olares-nginx-config
```

### Method 2: Automatic Integration
Modify the `/root/.local/bin/olares-deploy` script to automatically run the configuration generator after successful deployment.

Add to end of script:
```bash
# Auto-update Nginx configuration
if [ -f /root/.local/bin/olares-nginx-config ]; then
    echo ""
    echo "Updating Nginx reverse proxy configuration..."
    python3 /root/.local/bin/olares-nginx-config > /dev/null 2>&1 || true
fi
```

---

## ✅ Verification Tests

### 1. Test Health Check
```bash
curl http://localhost:3000/health
# Expected output: healthy
```

### 2. Test Application Proxy
```bash
# Test application
curl http://localhost:3000/my-app/
# Expected output: <h1>My App</h1>

# Or by port
curl http://localhost:3000/8080/
# Expected output: same as above
```

### 3. Check Nginx Processes
```bash
ps aux | grep nginx
# Expected: see master and multiple worker processes
```

### 4. Check Listening Ports
```bash
ss -tlnp | grep :3000
# Expected: Nginx listening on port 3000
```

---

## 🐛 Troubleshooting

### Nginx Not Started
```bash
# Check configuration
nginx -t

# Start Nginx
nginx

# View error log
tail -f /tmp/nginx-error.log
```

### Application Proxy 502 Error
1. Check if application Pod is running:
   ```bash
   /tmp/kubectl get pods -n {namespace} -l app=my-app
   ```

2. Check if Service exists:
   ```bash
   /tmp/kubectl get svc -n {namespace}
   ```

3. Test Service connectivity:
   ```bash
   curl http://my-app-svc.{namespace}.svc.cluster.local:8080
   ```

### Configuration Not Applied
```bash
# Regenerate and reload
python3 /root/.local/bin/olares-nginx-config

# Or manually reload
nginx -s reload
```

---

## 📊 Port Allocation

| Port | Service | Description |
|------|---------|-------------|
| 3000 | Nginx | **Unified Entry** - All external requests through here |
| 5000 | code-server | VS Code IDE interface |
| 8000 | OpenCode AI | AI-assisted programming service |
| Others | Application Pods | Accessed through Kubernetes Service |

---

## 🎉 Completion Status

✅ Nginx started and listening on port 3000  
✅ Auto-configuration generator deployed  
✅ Proxy configurations generated for all deployed applications  
✅ WebSocket support (important for code-server, etc.)  
✅ Long connection and real-time response support  
✅ Internal testing passed  

### To Be Verified
⏳ External access testing (needs browser testing via Olares URL)

---

## 📚 Related Documentation

- Deployment script: `/root/.local/bin/olares-deploy`
- Configuration generator: `/root/.local/bin/olares-nginx-config`
- Nginx main config: `/etc/nginx/nginx.conf`
- Olares development skill: `/root/.config/opencode/skills/olares-dev.md`
