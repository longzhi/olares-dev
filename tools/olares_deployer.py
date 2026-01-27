#!/usr/bin/env python3
"""
Olares Deployer - Python API for automatic deployment
Used by OpenCode to deploy applications after development
"""

import subprocess
import json
import re
import os
from typing import Dict, Optional, Tuple
from pathlib import Path


class OlaresDeployer:
    """Deploy applications to Olares DevBox with automatic external access"""
    
    def __init__(self):
        self.kubectl = "/tmp/kubectl"
        self.deploy_script = "/root/.local/bin/olares-deploy"
        self.manage_script = "/root/.local/bin/olares-manage"
        self.urls_script = "/root/.local/bin/olares-urls"
        self.namespace = self._get_namespace()
        self.domain = self._get_domain()
        
        self._ensure_environment()
    
    def _get_namespace(self) -> str:
        ns_file = "/var/run/secrets/kubernetes.io/serviceaccount/namespace"
        if os.path.exists(ns_file):
            with open(ns_file) as f:
                return f.read().strip()
        return "default"
    
    def _get_domain(self) -> str:
        username = self.namespace.split("-")[-1] if "-" in self.namespace else "unknown"
        return f"{username}.olares.com"
    
    def _ensure_environment(self):
        init_script = "/root/.local/bin/olares-init"
        if os.path.exists(init_script):
            subprocess.run([init_script], check=False, capture_output=True)
    
    def _run_command(self, cmd: list, check: bool = True) -> Tuple[int, str, str]:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        return result.returncode, result.stdout, result.stderr
    
    def _sanitize_app_name(self, name: str) -> str:
        name = name.lower()
        name = re.sub(r'[^a-z0-9-]', '-', name)
        name = name.strip('-')
        return name[:50]
    
    def detect_framework(self, project_path: str) -> Dict[str, any]:
        """Auto-detect application framework and configuration"""
        path = Path(project_path)
        
        if (path / "app.py").exists():
            with open(path / "app.py") as f:
                content = f.read()
                if "Flask" in content or "flask" in content:
                    return {
                        "framework": "flask",
                        "image": "python:3.11-slim",
                        "port": 5000,
                        "command": "pip install flask && python app.py"
                    }
        
        if (path / "main.py").exists():
            with open(path / "main.py") as f:
                content = f.read()
                if "FastAPI" in content or "fastapi" in content:
                    return {
                        "framework": "fastapi",
                        "image": "python:3.11-slim",
                        "port": 8000,
                        "command": "pip install fastapi uvicorn && uvicorn main:app --host 0.0.0.0 --port 8000"
                    }
        
        if (path / "manage.py").exists():
            return {
                "framework": "django",
                "image": "python:3.11-slim",
                "port": 8000,
                "command": "pip install django && python manage.py runserver 0.0.0.0:8000"
            }
        
        if (path / "package.json").exists():
            with open(path / "package.json") as f:
                content = f.read()
                if "express" in content:
                    return {
                        "framework": "express",
                        "image": "node:20-slim",
                        "port": 3000,
                        "command": "npm install && npm start"
                    }
        
        return {
            "framework": "unknown",
            "image": "python:3.11-slim",
            "port": 8000,
            "command": None
        }
    
    def deploy(
        self,
        app_name: str,
        image: str,
        port: int,
        command: Optional[str] = None,
        auto_detect: bool = False,
        project_path: Optional[str] = None
    ) -> Dict:
        """
        Deploy an application to Olares
        
        Args:
            app_name: Application name (will be sanitized)
            image: Docker image
            port: Application port
            command: Startup command (optional)
            auto_detect: Auto-detect framework (requires project_path)
            project_path: Path to project for auto-detection
        
        Returns:
            Dict with deployment info including external_url
        """
        
        if auto_detect and project_path:
            config = self.detect_framework(project_path)
            if config["framework"] != "unknown":
                image = config["image"]
                port = config["port"]
                command = command or config["command"]
        
        app_name = self._sanitize_app_name(app_name)
        
        cmd = [self.deploy_script, app_name, image, str(port)]
        if command:
            cmd.append(command)
        
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        
        if returncode != 0:
            return {
                "success": False,
                "error": stderr,
                "app_name": app_name
            }
        
        third_level_domain = self._get_third_level_domain(app_name)
        external_url = f"https://{third_level_domain}.{self.domain}" if third_level_domain else None
        
        return {
            "success": True,
            "app_name": app_name,
            "namespace": self.namespace,
            "port": port,
            "external_url": external_url,
            "internal_url": f"http://{app_name}-svc.{self.namespace}.svc.cluster.local:{port}",
            "third_level_domain": third_level_domain
        }
    
    def _get_third_level_domain(self, app_name: str) -> Optional[str]:
        cmd = [
            self.kubectl, "get", "deployment", app_name,
            "-n", self.namespace,
            "-o", "jsonpath={.metadata.annotations.applications\\.app\\.bytetrade\\.io/default-thirdlevel-domains}"
        ]
        
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        if returncode != 0 or not stdout:
            return None
        
        try:
            data = json.loads(stdout)
            return data[0]["thirdLevelDomain"]
        except:
            return None
    
    def get_app_info(self, app_name: str) -> Dict:
        """Get information about a deployed app"""
        app_name = self._sanitize_app_name(app_name)
        
        cmd = [self.manage_script, "info", app_name]
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        
        if returncode != 0:
            return {"success": False, "error": "App not found"}
        
        third_level_domain = self._get_third_level_domain(app_name)
        external_url = f"https://{third_level_domain}.{self.domain}" if third_level_domain else None
        
        return {
            "success": True,
            "app_name": app_name,
            "external_url": external_url,
            "output": stdout
        }
    
    def list_apps(self) -> Dict:
        """List all deployed applications"""
        cmd = [self.manage_script, "list"]
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        
        return {
            "success": returncode == 0,
            "output": stdout,
            "error": stderr if returncode != 0 else None
        }
    
    def get_logs(self, app_name: str, follow: bool = False) -> str:
        """Get application logs"""
        app_name = self._sanitize_app_name(app_name)
        
        cmd = [self.manage_script, "logs", app_name]
        if follow:
            cmd.append("-f")
        
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        return stdout
    
    def delete(self, app_name: str) -> Dict:
        """Delete an application"""
        app_name = self._sanitize_app_name(app_name)
        
        cmd = [self.manage_script, "delete", app_name]
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        
        return {
            "success": returncode == 0,
            "app_name": app_name,
            "output": stdout,
            "error": stderr if returncode != 0 else None
        }
    
    def get_all_urls(self) -> str:
        """Get all deployed apps with external URLs"""
        cmd = [self.urls_script]
        returncode, stdout, stderr = self._run_command(cmd, check=False)
        return stdout


def auto_deploy_after_development(
    app_name: str,
    project_path: str = ".",
    framework: Optional[str] = None
) -> Dict:
    """
    Automatic deployment after user completes development
    
    This is the main entry point for OpenCode to call after development is complete.
    
    Args:
        app_name: User-provided application name
        project_path: Path to the developed application
        framework: Optional framework hint (flask, fastapi, express, django)
    
    Returns:
        Dict with deployment status and external URL
    """
    deployer = OlaresDeployer()
    
    result = deployer.deploy(
        app_name=app_name,
        image="",
        port=0,
        auto_detect=True,
        project_path=project_path
    )
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python olares_deployer.py <app-name> <image> <port> [command]")
        print("   Or: python olares_deployer.py --auto-deploy <app-name> <project-path>")
        sys.exit(1)
    
    if sys.argv[1] == "--auto-deploy":
        result = auto_deploy_after_development(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".")
    else:
        deployer = OlaresDeployer()
        result = deployer.deploy(
            app_name=sys.argv[1],
            image=sys.argv[2],
            port=int(sys.argv[3]),
            command=sys.argv[4] if len(sys.argv) > 4 else None
        )
    
    print(json.dumps(result, indent=2))
