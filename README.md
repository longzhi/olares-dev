# Olares Development Skill

OpenCode skill for developing and deploying applications to [Olares](https://olares.com) - a self-hosted cloud operating system.

## Contents

- `olares-dev.md` - Main skill file with complete Olares development reference
- `templates/` - Boilerplate templates for quick chart creation

## Usage

### In OpenCode

Add this skill to your OpenCode configuration:

```bash
# Global installation
cp olares-dev.md ~/.config/opencode/skills/

# Or project-specific
cp olares-dev.md .opencode/skills/
```

### Templates

The `templates/` directory contains fillable templates:

| File | Purpose |
|------|---------|
| `Chart.yaml` | Helm chart metadata |
| `OlaresManifest.yaml` | Olares-specific configuration |
| `deployment.yaml` | Kubernetes deployment template |
| `service.yaml` | Kubernetes service template |

Replace `{{ PLACEHOLDER }}` values with your actual configuration.

## What This Skill Covers

1. **Application Packaging** - Helm chart structure + OlaresManifest.yaml
2. **Database Provisioning** - PostgreSQL, Redis, MongoDB integration
3. **Permission Configuration** - App data, user data, system APIs
4. **Deployment Workflow** - Studio UI steps, Playwright automation
5. **Troubleshooting** - Common issues and solutions

## Key Concepts

- **No REST API**: Olares deployment is through Studio UI (automate with Playwright)
- **System Services**: PostgreSQL/Redis/MongoDB are pre-installed, just declare in manifest
- **User Isolation**: Each user gets isolated app instances

## References

- [Olares Documentation](https://docs.olares.com/developer/develop/)
- [Official App Repository](https://github.com/beclab/apps)
- [OlaresManifest Spec](https://docs.olares.com/developer/develop/package/manifest/)
