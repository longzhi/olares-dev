# Olares Development Skill

🚀 Complete Olares development and deployment skill for [OpenCode AI](https://opencode.com), including automated tools and Nginx reverse proxy system.

OpenCode skill for developing and deploying applications to [Olares](https://olares.com) - a self-hosted cloud operating system.

## 📦 Contents

- `olares-dev.md` - **Enhanced** skill file with DevBox Quick Deploy + Nginx reverse proxy
- `templates/` - Boilerplate templates for quick chart creation
- `tools/` - **NEW** Automated deployment and management tools
- `docs/` - **NEW** Complete documentation and guides

## 🎯 What's New

### Automated DevBox Deployment System
- ✅ Direct `kubectl` deployment (no Helm charts needed for dev)
- ✅ Automatic Nginx reverse proxy configuration
- ✅ Unified entry point (port 3000) with path-based routing
- ✅ OpenCode Server external access support
- ✅ Zero-downtime configuration updates

### Network Architecture
```
External Browser
  ↓ HTTPS
https://{hash}-3000.{domain}/{path}
  ↓
Olares Ingress → OpenCode Container (port 3000)
  ↓
Nginx Reverse Proxy (path routing)
  ↓
  ├─ /                    → localhost:4096 (OpenCode Server)
  ├─ /my-app/            → my-app-svc:port
  └─ /health             → Nginx health check
```

## 🚀 Quick Start

### 1. Install Tools

```bash
# Install to system
mkdir -p ~/.local/bin ~/.local/lib
cp tools/olares-* ~/.local/bin/
cp tools/olares_deployer.py ~/.local/lib/
chmod +x ~/.local/bin/olares-*

# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Skill

```bash
# Install to OpenCode
cp olares-dev.md ~/.config/opencode/skills/
```

### 3. Deploy Your First App

```bash
# 1. Deploy application
olares-deploy my-app python:3.11-slim 5000 "python app.py"

# 2. Update Nginx config (REQUIRED)
python3 ~/.local/bin/olares-nginx-config

# 3. Access at:
# https://{hash}-3000.{domain}/my-app/
```

## 📋 Standard Deployment Flow

```bash
# Step 1: Deploy
olares-deploy app-name image:tag port "startup-command"

# Step 2: Update Nginx (Mandatory!)
python3 olares-nginx-config

# Step 3: Access
https://{hash}-3000.{domain}/app-name/
```

## 🛠️ Available Tools

### Deployment
- `olares-deploy` - Deploy apps to Kubernetes
- `olares-nginx-config` - Generate/update Nginx reverse proxy configs
- `olares_deployer.py` - Python API for programmatic deployment

### Management
- `olares-manage` - Manage deployed apps (list, info, logs, delete)
- `olares-urls` - Show all deployed app URLs
- `olares-init` - Initialize environment (install kubectl, verify RBAC)

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `olares-dev.md` | Complete OpenCode skill definition |
| `docs/FINAL_SOLUTION.md` | Complete architecture and solution guide |
| `docs/NGINX_PROXY_COMPLETE.md` | Nginx configuration detailed guide |
| `docs/SOLUTION_SUMMARY.md` | Problem and solution summary |

## 🌐 Access Patterns

### OpenCode Server
```
https://{hash}-3000.{domain}/
```
Root path for OpenCode Server (port 4096).

### Deployed Applications
```
# By app name
https://{hash}-3000.{domain}/my-app/

# By port number
https://{hash}-3000.{domain}/5000/

# Health check
https://{hash}-3000.{domain}/health
```

## 📖 Usage in OpenCode

### Traditional (Helm Charts)

For production apps intended for Olares Market:

```bash
# Use templates
cp templates/* my-app/
# Edit Chart.yaml, OlaresManifest.yaml, etc.
# Package and deploy via Studio UI
```

### DevBox Quick Deploy (Recommended for Development)

For rapid development and testing:

```bash
# Just run deploy command
olares-deploy my-app python:3.11-slim 5000 "python app.py"
python3 olares-nginx-config

# App is live immediately!
```

## 🎨 Example: Hello World

```bash
# Create app
echo '<h1>Hello World</h1>' > index.html

# Deploy
olares-deploy hello-world python:3.11-slim 8000 "python -m http.server 8000"

# Update Nginx
python3 olares-nginx-config

# Access
https://{hash}-3000.{domain}/hello-world/
```

## ✨ Key Features

### Traditional Helm Deployment
1. **Application Packaging** - Helm chart structure + OlaresManifest.yaml
2. **Database Provisioning** - PostgreSQL, Redis, MongoDB integration
3. **Permission Configuration** - App data, user data, system APIs
4. **Deployment Workflow** - Studio UI steps, Playwright automation
5. **Troubleshooting** - Common issues and solutions

### NEW: DevBox Quick Deploy
1. **One-Command Deployment** - No Helm charts needed
2. **Automatic Nginx Proxy** - Unified entry with path routing
3. **OpenCode Server Support** - External access to development tools
4. **Zero Downtime** - Graceful Nginx reloads
5. **Auto Framework Detection** - Flask, FastAPI, Express, Django

## 🔑 Key Concepts

- **Unified Entry Point**: All requests through port 3000
- **Path-Based Routing**: Different apps on different URL paths
- **OpenCode Server**: Root path (`/`) for development environment
- **Automatic Configuration**: One command to update all proxy rules
- **No Port Conflicts**: Unlimited apps without port exhaustion

**Traditional Concepts**:
- **No REST API**: Olares deployment is through Studio UI (automate with Playwright)
- **System Services**: PostgreSQL/Redis/MongoDB are pre-installed, just declare in manifest
- **User Isolation**: Each user gets isolated app instances

## 🐛 Troubleshooting

### App not accessible externally
```bash
# Did you update Nginx?
python3 olares-nginx-config

# Check Nginx status
python3 olares-nginx-config status
```

### 502 Bad Gateway
```bash
# Check if pod is running
kubectl get pods -n namespace -l app=app-name

# View logs
kubectl logs -n namespace -l app=app-name
```

### Configuration issues
```bash
# View generated config
cat /etc/nginx/conf.d/dev/app-name.conf

# Test Nginx config
nginx -t

# Reload Nginx
nginx -s reload
```

## 📞 Support

- **GitHub Issues**: https://github.com/longzhi/olares-skill/issues
- **Olares Documentation**: https://docs.olares.com/developer/develop/
- **Official App Repository**: https://github.com/beclab/apps

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a Pull Request

## 📄 License

MIT License

---

**🎉 Happy Developing on Olares!**
