#!/usr/bin/env python3
"""
Repo Onboarder - GitHub-integrated codebase analyzer
Generates comprehensive onboarding documentation for repositories.
"""

import os
import json
import yaml
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import argparse
import tempfile
import shutil

# Try to load python-dotenv if available
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# External dependencies
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

@dataclass
class Config:
    """Configuration for the onboarder"""
    depth: int = 3
    max_items_per_dir: int = 10
    ignore: List[str] = None
    structure_include: List[str] = None
    structure_exclude: List[str] = None
    routes_frameworks: List[str] = None
    output_dir: str = "onboarding"
    pr_mode: str = "auto"
    llm_enabled: bool = True
    llm_model: str = "claude-3-haiku-20240307"
    
    def __post_init__(self):
        if self.ignore is None:
            self.ignore = [
                ".git", "node_modules", ".venv", "__pycache__", "dist", "build", 
                "out", "target", "coverage", ".next", ".turbo", ".mypy_cache", 
                ".pytest_cache", ".DS_Store", "*.pyc", "*.pyo"
            ]
        if self.structure_include is None:
            self.structure_include = ["**/*"]
        if self.structure_exclude is None:
            self.structure_exclude = []
        if self.routes_frameworks is None:
            self.routes_frameworks = ["express", "flask", "fastapi", "django", "nextjs"]

class RepoAnalyzer:
    """Main analyzer class for repository analysis"""
    
    def __init__(self, repo_path: str, config: Config):
        self.repo_path = Path(repo_path).resolve()
        self.config = config
        self.analysis = {
            "stack": {"languages": [], "frameworks": [], "managers": [], "runtimes": [], 
                     "npm_scripts": {}, "externals": []},
            "entrypoints": [],
            "routes": [],
            "roles": [],
            "systems": {"nodes": [], "kinds": {}},
            "scanned_files": [],
            "tree": ""
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Run complete analysis of the repository"""
        print(f"🔍 Analyzing repository: {self.repo_path}")
        
        # Load configuration
        self._load_config()
        
        # Analyze tech stack
        self._analyze_tech_stack()
        
        # Find entrypoints
        self._find_entrypoints()
        
        # Analyze project structure
        self._analyze_structure()
        
        # Extract HTTP routes
        self._extract_routes()
        
        # Detect external systems
        self._detect_external_systems()
        
        # Generate LLM explanation
        if self.config.llm_enabled and ANTHROPIC_AVAILABLE:
            self._generate_llm_explanation()
        
        return self.analysis
    
    def _load_config(self):
        """Load configuration from .onboarder.yml if present"""
        config_file = self.repo_path / ".onboarder.yml"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = yaml.safe_load(f)
                    for key, value in user_config.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
            except Exception as e:
                print(f"⚠️  Warning: Could not load config file: {e}")
    
    def _analyze_tech_stack(self):
        """Analyze technology stack from package files"""
        print("📦 Analyzing tech stack...")
        
        # Node.js detection
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                    self.analysis["stack"]["languages"].append("JavaScript/TypeScript")
                    self.analysis["stack"]["managers"].append("npm")
                    self.analysis["stack"]["runtimes"].append("Node.js")
                    
                    # Extract npm scripts
                    if "scripts" in pkg:
                        self.analysis["stack"]["npm_scripts"] = pkg["scripts"]
                    
                    # Detect frameworks
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    frameworks = self._detect_node_frameworks(deps)
                    self.analysis["stack"]["frameworks"].extend(frameworks)
                    
            except Exception as e:
                print(f"⚠️  Could not parse package.json: {e}")
        
        # Python detection
        for py_file in ["requirements.txt", "pyproject.toml", "Pipfile", "setup.py"]:
            if (self.repo_path / py_file).exists():
                self.analysis["stack"]["languages"].append("Python")
                if py_file == "requirements.txt":
                    self.analysis["stack"]["managers"].append("pip")
                elif py_file == "pyproject.toml":
                    self.analysis["stack"]["managers"].append("poetry")
                elif py_file == "Pipfile":
                    self.analysis["stack"]["managers"].append("pipenv")
                break
        
        # Go detection
        if (self.repo_path / "go.mod").exists():
            self.analysis["stack"]["languages"].append("Go")
            self.analysis["stack"]["managers"].append("go mod")
            self.analysis["stack"]["runtimes"].append("Go")
        
        # Rust detection
        if (self.repo_path / "Cargo.toml").exists():
            self.analysis["stack"]["languages"].append("Rust")
            self.analysis["stack"]["managers"].append("cargo")
            self.analysis["stack"]["runtimes"].append("Rust")
        
        # Java/Kotlin detection
        for build_file in ["pom.xml", "build.gradle", "build.gradle.kts"]:
            if (self.repo_path / build_file).exists():
                self.analysis["stack"]["languages"].append("Java/Kotlin")
                if build_file == "pom.xml":
                    self.analysis["stack"]["managers"].append("Maven")
                else:
                    self.analysis["stack"]["managers"].append("Gradle")
                break
    
    def _detect_node_frameworks(self, deps: Dict[str, str]) -> List[str]:
        """Detect Node.js frameworks from dependencies"""
        frameworks = []
        framework_map = {
            "express": "Express.js",
            "next": "Next.js",
            "react": "React",
            "vue": "Vue.js",
            "svelte": "Svelte",
            "@nestjs/core": "NestJS",
            "fastify": "Fastify",
            "koa": "Koa.js"
        }
        
        for dep in deps.keys():
            if dep in framework_map:
                frameworks.append(framework_map[dep])
        
        return frameworks
    
    def _find_entrypoints(self):
        """Find application entrypoints and startup scripts"""
        print("🚀 Finding entrypoints...")
        
        entrypoint_patterns = [
            "index.js", "index.ts", "index.mjs",
            "server.js", "server.ts", "app.js", "app.ts",
            "main.js", "main.ts", "main.py", "main.go", "main.rs",
            "wsgi.py", "asgi.py", "manage.py",
            "cmd/main.go", "src/main.rs",
            "src/main/java/**/Main.java", "src/main/kotlin/**/Main.kt"
        ]
        
        for pattern in entrypoint_patterns:
            for file_path in self.repo_path.rglob(pattern):
                if self._should_ignore_file(file_path):
                    continue
                rel_path = file_path.relative_to(self.repo_path)
                self.analysis["entrypoints"].append(str(rel_path))
        
        # Check for shebangs in small files
        for file_path in self.repo_path.rglob("*.py"):
            if file_path.stat().st_size < 10000:  # Small files only
                try:
                    with open(file_path, 'r') as f:
                        first_line = f.readline().strip()
                        if first_line.startswith('#!'):
                            rel_path = file_path.relative_to(self.repo_path)
                            self.analysis["entrypoints"].append(str(rel_path))
                except:
                    pass
    
    def _analyze_structure(self):
        """Analyze project structure and generate tree"""
        print("📁 Analyzing project structure...")
        
        tree_lines = []
        self._build_tree(self.repo_path, "", tree_lines, 0)
        self.analysis["tree"] = "\n".join(tree_lines)
        
        # Generate roles for key files
        self._assign_file_roles()
    
    def _build_tree(self, path: Path, prefix: str, lines: List[str], depth: int):
        """Recursively build directory tree"""
        if depth >= self.config.depth:
            return
        
        try:
            items = sorted([p for p in path.iterdir() if not p.name.startswith('.')])
            items = [p for p in items if not self._should_ignore_file(p)]
            
            # Limit items per directory
            if len(items) > self.config.max_items_per_dir:
                items = items[:self.config.max_items_per_dir]
                has_more = True
            else:
                has_more = False
            
            for i, item in enumerate(items):
                is_last = i == len(items) - 1 and not has_more
                current_prefix = "└── " if is_last else "├── "
                
                if item.is_dir():
                    icon = "📁"
                    lines.append(f"{prefix}{current_prefix}{icon} {item.name}/")
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    self._build_tree(item, next_prefix, lines, depth + 1)
                else:
                    icon = "📄"
                    lines.append(f"{prefix}{current_prefix}{icon} {item.name}")
                
                if self._should_scan_file(item):
                    rel_path = item.relative_to(self.repo_path)
                    self.analysis["scanned_files"].append(str(rel_path))
            
            if has_more:
                lines.append(f"{prefix}└── ... and {len(sorted([p for p in path.iterdir() if not p.name.startswith('.')])) - self.config.max_items_per_dir} more")
                
        except PermissionError:
            lines.append(f"{prefix}└── [Permission denied]")
    
    def _should_ignore_file(self, path: Path) -> bool:
        """Check if file should be ignored"""
        rel_path = path.relative_to(self.repo_path)
        
        for ignore_pattern in self.config.ignore:
            if ignore_pattern in str(rel_path) or path.name == ignore_pattern:
                return True
        
        return False
    
    def _should_scan_file(self, path: Path) -> bool:
        """Check if file should be scanned for content"""
        if not path.is_file():
            return False
        
        if self._should_ignore_file(path):
            return False
        
        # Only scan text files under reasonable size
        if path.stat().st_size > 100000:  # 100KB limit
            return False
        
        text_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.go', '.rs', '.java', '.kt', 
                          '.html', '.css', '.json', '.yaml', '.yml', '.toml', '.md', '.txt'}
        
        return path.suffix.lower() in text_extensions
    
    def _assign_file_roles(self):
        """Assign likely roles to files based on path heuristics"""
        role_patterns = {
            # Backend patterns
            "routes/": "API Routes",
            "router/": "API Routes", 
            "app.js": "Main Application",
            "server.js": "Server Entry Point",
            "index.js": "Entry Point",
            "main.js": "Entry Point",
            "controllers/": "Business Logic",
            "models/": "Data Models",
            "middleware/": "HTTP Middleware",
            "middlewares/": "HTTP Middleware",
            "services/": "Business Services",
            "utils/": "Utilities",
            "lib/": "Library Code",
            "helpers/": "Helper Functions",
            "config/": "Configuration",
            "settings/": "Configuration",
            "migrations/": "Database Migrations",
            "seeds/": "Database Seeds",
            
            # Frontend patterns
            "components/": "UI Components",
            "views/": "UI Views",
            "pages/": "UI Pages",
            "templates/": "UI Templates",
            "static/": "Static Assets",
            "public/": "Public Assets",
            "assets/": "Assets",
            "styles/": "Styling",
            "css/": "Styling",
            "scss/": "Styling",
            "sass/": "Styling",
            "less/": "Styling",
            
            # Testing patterns
            "tests/": "Tests",
            "test/": "Tests",
            "spec/": "Tests",
            "__tests__/": "Tests",
            "test_": "Test File",
            ".test.": "Test File",
            ".spec.": "Test File",
            
            # Documentation
            "readme": "Documentation",
            "docs/": "Documentation",
            "documentation/": "Documentation",
            "changelog": "Documentation",
            "license": "Documentation",
            "contributing": "Documentation",
            
            # Configuration files
            "package.json": "Package Configuration",
            "requirements.txt": "Dependencies",
            "pyproject.toml": "Python Configuration",
            "cargo.toml": "Rust Configuration",
            "go.mod": "Go Module",
            "pom.xml": "Maven Configuration",
            "build.gradle": "Gradle Configuration",
            "dockerfile": "Docker Configuration",
            "docker-compose": "Docker Configuration",
            ".env": "Environment Configuration",
            ".gitignore": "Git Configuration",
            ".github/": "GitHub Configuration",
            "workflows/": "CI/CD Configuration",
            
            # Build and deployment
            "dist/": "Build Output",
            "build/": "Build Output",
            "out/": "Build Output",
            "target/": "Build Output",
            "coverage/": "Test Coverage",
            "node_modules/": "Dependencies",
            
            # Database
            "migrations/": "Database Migrations",
            "seeds/": "Database Seeds",
            "schema/": "Database Schema",
            "sql/": "SQL Scripts",
        }
        
        for file_path in self.analysis["scanned_files"]:
            rel_path = file_path.lower()
            role = "General Code"
            
            # Check for exact filename matches first
            filename = Path(file_path).name.lower()
            for pattern, role_name in role_patterns.items():
                if pattern.endswith('/'):
                    # Directory pattern
                    if pattern[:-1] in rel_path:
                        role = role_name
                        break
                elif pattern in filename or pattern in rel_path:
                    # File pattern
                    role = role_name
                    break
            
            # Special cases for specific file extensions
            if role == "General Code":
                ext = Path(file_path).suffix.lower()
                if ext in ['.js', '.ts', '.jsx', '.tsx']:
                    if 'test' in filename or 'spec' in filename:
                        role = "Test File"
                    elif 'config' in filename or 'settings' in filename:
                        role = "Configuration"
                    elif 'index' in filename or 'main' in filename:
                        role = "Entry Point"
                    else:
                        role = "JavaScript/TypeScript Code"
                elif ext in ['.py']:
                    if 'test' in filename or 'spec' in filename:
                        role = "Test File"
                    elif 'config' in filename or 'settings' in filename:
                        role = "Configuration"
                    elif 'main' in filename or '__init__' in filename:
                        role = "Entry Point"
                    else:
                        role = "Python Code"
                elif ext in ['.go']:
                    if 'test' in filename:
                        role = "Test File"
                    elif 'main' in filename:
                        role = "Entry Point"
                    else:
                        role = "Go Code"
                elif ext in ['.rs']:
                    if 'test' in filename:
                        role = "Test File"
                    elif 'main' in filename:
                        role = "Entry Point"
                    else:
                        role = "Rust Code"
                elif ext in ['.html', '.htm']:
                    role = "HTML Template"
                elif ext in ['.css', '.scss', '.sass', '.less']:
                    role = "Styling"
                elif ext in ['.json']:
                    role = "Configuration/Data"
                elif ext in ['.md']:
                    role = "Documentation"
                elif ext in ['.yml', '.yaml']:
                    role = "Configuration"
                elif ext in ['.sql']:
                    role = "Database Script"
                elif ext in ['.sh', '.bash']:
                    role = "Shell Script"
                elif ext in ['.dockerfile', '.dockerignore']:
                    role = "Docker Configuration"
            
            self.analysis["roles"].append([file_path, role])
        
        # Limit to reasonable number
        if len(self.analysis["roles"]) > 120:
            self.analysis["roles"] = self.analysis["roles"][:120]
            self.analysis["roles"].append(["...", "and more files"])
    
    def _extract_routes(self):
        """Extract HTTP routes from code files"""
        print("🛣️  Extracting HTTP routes...")
        
        route_patterns = {
            "express": [
                r'(?:app|router)\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
                r'(?:app|router)\.(get|post|put|delete|patch|options|head)\s*\(\s*`([^`]+)`'
            ],
            "flask": [
                r'@app\.route\s*\(\s*["\']([^"\']+)["\']',
                r'@app\.route\s*\(\s*`([^`]+)`'
            ],
            "fastapi": [
                r'@app\.(get|post|put|delete|patch|options|head)\s*\(\s*["\']([^"\']+)["\']',
                r'@app\.(get|post|put|delete|patch|options|head)\s*\(\s*`([^`]+)`'
            ],
            "django": [
                r'path\s*\(\s*["\']([^"\']+)["\']',
                r'path\s*\(\s*`([^`]+)`'
            ]
        }
        
        routes = set()
        
        for file_path in self.analysis["scanned_files"]:
            if not self._should_scan_file(self.repo_path / file_path):
                continue
                
            try:
                with open(self.repo_path / file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for framework, patterns in route_patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, content, re.MULTILINE)
                        for match in matches:
                            if len(match.groups()) == 2:
                                method, path = match.groups()
                                method = method.upper()
                            else:
                                method = "GET"
                                path = match.group(1)
                            
                            # Normalize path to avoid duplicates
                            path = path.strip('"\'`')
                            # Create a unique key for deduplication
                            route_key = (framework, method, path)
                            routes.add((framework, method, path, file_path))
                            
            except Exception as e:
                continue
        
        # Convert to list and sort for consistent output
        self.analysis["routes"] = sorted(list(routes), key=lambda x: (x[0], x[1], x[2]))
    
    def _detect_external_systems(self):
        """Detect external systems and integrations"""
        print("🔗 Detecting external systems...")
        
        # Known SDK patterns with descriptions
        sdk_patterns = {
            "Stripe": {"patterns": ["stripe", "stripe-"], "description": "Payment processing"},
            "Twilio": {"patterns": ["twilio"], "description": "Communication platform"},
            "Sentry": {"patterns": ["sentry", "@sentry/"], "description": "Error monitoring"},
            "Redis": {"patterns": ["redis", "ioredis"], "description": "In-memory database"},
            "MongoDB": {"patterns": ["mongodb", "mongoose"], "description": "NoSQL database"},
            "PostgreSQL": {"patterns": ["pg", "postgres", "postgresql"], "description": "SQL database"},
            "MySQL": {"patterns": ["mysql", "mysql2"], "description": "SQL database"},
            "Kafka": {"patterns": ["kafka", "kafkajs"], "description": "Message streaming"},
            "RabbitMQ": {"patterns": ["amqplib", "rabbitmq"], "description": "Message broker"},
            "AWS": {"patterns": ["aws-sdk", "@aws-sdk"], "description": "Cloud services"},
            "GCP": {"patterns": ["@google-cloud/", "google-cloud-"], "description": "Google Cloud Platform"},
            "Azure": {"patterns": ["@azure/", "azure-"], "description": "Microsoft Azure"},
            "OpenAI": {"patterns": ["openai", "@openai/"], "description": "AI/ML services"},
            "Anthropic": {"patterns": ["anthropic", "@anthropic/"], "description": "AI/ML services"}
        }
        
        # Check package.json for SDKs
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    pkg = json.load(f)
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    
                    for system, info in sdk_patterns.items():
                        for dep in deps.keys():
                            if any(pattern in dep.lower() for pattern in info["patterns"]):
                                if system not in self.analysis["stack"]["externals"]:
                                    self.analysis["stack"]["externals"].append(system)
                                break
            except:
                pass
        
        # Scan code for environment variables and URLs
        env_vars = set()
        urls = set()
        
        for file_path in self.analysis["scanned_files"]:
            if not self._should_scan_file(self.repo_path / file_path):
                continue
                
            try:
                with open(self.repo_path / file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find environment variables
                env_matches = re.findall(r'process\.env\.(\w+)|os\.environ\.get\(["\'](\w+)["\']', content)
                for match in env_matches:
                    env_vars.add(match[0] or match[1])
                
                # Find URLs (basic pattern)
                url_matches = re.findall(r'https?://[^\s"\'<>]+', content)
                for url in url_matches:
                    if 'localhost' not in url and '127.0.0.1' not in url:
                        urls.add(url)
                        
            except:
                continue
        
        # Add environment variables to systems (deduplicated)
        if env_vars:
            if len(env_vars) > 12:
                self.analysis["systems"]["nodes"].append("Environment Variables")
                self.analysis["systems"]["kinds"]["Environment Variables"] = ["env", f"{len(env_vars)} variables"]
            else:
                env_list = sorted(list(env_vars))
                self.analysis["systems"]["nodes"].append("Environment Variables")
                self.analysis["systems"]["kinds"]["Environment Variables"] = ["env", f"Variables: {', '.join(env_list[:5])}{'...' if len(env_list) > 5 else ''}"]
        
        # Add URLs to systems (deduplicated by domain)
        domains = set()
        for url in sorted(urls):
            domain = re.sub(r'https?://([^/]+).*', r'\1', url)
            domains.add(domain)
        
        for domain in sorted(domains):
            self.analysis["systems"]["nodes"].append(domain)
            self.analysis["systems"]["kinds"][domain] = ["url", "External API/Service"]
    
    def _generate_llm_explanation(self):
        """Generate LLM explanation using Anthropic Claude"""
        if not ANTHROPIC_AVAILABLE:
            return
        
        try:
            # Get API key from environment
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                print("⚠️  No ANTHROPIC_API_KEY found, skipping LLM explanation")
                return
            
            client = anthropic.Anthropic(api_key=api_key)
            
            # Prepare context
            context = {
                "tech_stack": self.analysis["stack"],
                "entrypoints": self.analysis["entrypoints"],
                "routes": self.analysis["routes"],
                "external_systems": self.analysis["systems"]["nodes"],
                "file_roles": self.analysis["roles"][:20]  # Limit for token budget
            }
            
            prompt = f"""
            Analyze this codebase and provide a concise explanation in 5 sections:
            
            1. What this repo likely does
            2. How to run it
            3. Key moving parts and relations
            4. External systems it touches
            5. Next tasks for a new dev
            
            Context: {json.dumps(context, indent=2)}
            
            Keep each section to 2-3 sentences maximum. Be specific and actionable.
            """
            
            response = client.messages.create(
                model=self.config.llm_model,
                max_tokens=1000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )
            
            self.analysis["llm_explanation"] = response.content[0].text
            
        except Exception as e:
            print(f"⚠️  LLM explanation failed: {e}")
    
    def generate_outputs(self):
        """Generate all output files"""
        print("📝 Generating output files...")
        
        output_dir = self.repo_path / self.config.output_dir
        output_dir.mkdir(exist_ok=True)
        
        # Generate JSON report
        with open(output_dir / "report.json", 'w') as f:
            json.dump(self.analysis, f, indent=2)
        
        # Generate Markdown overview
        self._generate_markdown_overview(output_dir)
        
        # Generate Mermaid diagrams
        self._generate_mermaid_diagrams(output_dir)
        
        # Generate HTML viewer
        self._generate_html_viewer(output_dir)
        
        print(f"✅ Onboarding files generated in: {output_dir}")
    
    def _generate_markdown_overview(self, output_dir: Path):
        """Generate Markdown overview file"""
        md_content = f"""# Repository Overview

## Tech Snapshot

**Languages:** {', '.join(self.analysis['stack']['languages']) or 'Not detected'}
**Frameworks:** {', '.join(self.analysis['stack']['frameworks']) or 'Not detected'}
**Package Managers:** {', '.join(self.analysis['stack']['managers']) or 'Not detected'}
**Runtimes:** {', '.join(self.analysis['stack']['runtimes']) or 'Not detected'}

## Entrypoints & Startup Scripts

{chr(10).join(f"- `{ep}`" for ep in self.analysis['entrypoints']) or 'No entrypoints detected'}

### NPM Scripts
{chr(10).join(f"- `{name}`: {script}" for name, script in self.analysis['stack']['npm_scripts'].items()) if self.analysis['stack']['npm_scripts'] else 'No npm scripts found'}

## Project Structure

```
{self.analysis['tree']}
```

## HTTP Routes

{chr(10).join(f"- **{method}** `{path}` ({framework})" for framework, method, path, source in self.analysis['routes']) or 'No routes detected'}

## External Systems & Integrations

**Dependencies:** {', '.join(self.analysis['stack']['externals']) or 'None detected'}

**Environment Variables & URLs:**
{chr(10).join(f"- {node}" for node in self.analysis['systems']['nodes']) or 'None detected'}

## Key Files & Roles

{chr(10).join(f"- `{path}` - {role}" for path, role in self.analysis['roles'])}

## High-Level Explainer

{self.analysis.get('llm_explanation', 'LLM explanation not available')}
"""
        
        with open(output_dir / "repo_overview.md", 'w') as f:
            f.write(md_content)
    
    def _generate_mermaid_diagrams(self, output_dir: Path):
        """Generate Mermaid diagram files"""
        # Structure diagram
        structure_mmd = self._generate_structure_mermaid()
        with open(output_dir / "mermaid_structure.mmd", 'w') as f:
            f.write(structure_mmd)
        
        # Routes diagram
        routes_mmd = self._generate_routes_mermaid()
        with open(output_dir / "mermaid_routes.mmd", 'w') as f:
            f.write(routes_mmd)
        
        # Systems diagram
        systems_mmd = self._generate_systems_mermaid()
        with open(output_dir / "mermaid_systems.mmd", 'w') as f:
            f.write(systems_mmd)
    
    def _generate_structure_mermaid(self) -> str:
        """Generate Mermaid structure diagram"""
        lines = ["graph TD"]
        lines.append("    subgraph Structure [Project Structure]")
        
        # Create a proper tree structure
        dirs = set()
        files_by_dir = defaultdict(list)
        
        for file_path in self.analysis["scanned_files"]:
            parts = Path(file_path).parts
            if len(parts) > 1:
                dir_name = parts[0]
                dirs.add(dir_name)
                files_by_dir[dir_name].append(parts[1] if len(parts) > 1 else "")
        
        # Add main directories and their files
        for i, dir_name in enumerate(sorted(dirs)[:8]):  # Limit to 8 dirs
            dir_id = f"dir{i}"
            lines.append(f"        {dir_id}[\"{dir_name}/\"]")
            lines.append(f"        Structure --> {dir_id}")
            
            # Add some key files from each directory
            key_files = files_by_dir[dir_name][:3]  # Max 3 files per dir
            for j, file_name in enumerate(key_files):
                if file_name:  # Skip empty names
                    file_id = f"file{i}_{j}"
                    lines.append(f"        {file_id}[\"{file_name}\"]")
                    lines.append(f"        {dir_id} --> {file_id}")
        
        lines.append("    end")
        return "\n".join(lines)
    
    def _generate_routes_mermaid(self) -> str:
        """Generate Mermaid routes diagram"""
        if not self.analysis["routes"]:
            return "graph TD\n    subgraph Routes [HTTP Routes]\n        none[No routes detected]\n    end"
        
        lines = ["graph TD"]
        lines.append("    subgraph Routes [HTTP Routes]")
        
        for i, (framework, method, path, source) in enumerate(self.analysis["routes"][:20]):  # Limit to 20 routes
            route_id = f"route{i}"
            lines.append(f"        {route_id}[\"{method} {path}\"]")
            lines.append(f"        Routes --> {route_id}")
        
        lines.append("    end")
        return "\n".join(lines)
    
    def _generate_systems_mermaid(self) -> str:
        """Generate Mermaid systems diagram"""
        if not self.analysis["systems"]["nodes"]:
            return "graph TD\n    subgraph Systems [External Systems]\n        none[No external systems detected]\n    end"
        
        lines = ["graph TD"]
        lines.append("    subgraph Systems [External Systems]")
        lines.append("        app[Application]")
        
        for i, node in enumerate(self.analysis["systems"]["nodes"][:12]):  # Limit to 12 systems
            system_id = f"sys{i}"
            # Get description from kinds if available
            kinds = self.analysis["systems"]["kinds"].get(node, [])
            description = kinds[1] if len(kinds) > 1 else ""
            
            if description:
                lines.append(f"        {system_id}[\"{node}<br/>{description}\"]")
            else:
                lines.append(f"        {system_id}[\"{node}\"]")
            lines.append(f"        app --> {system_id}")
        
        lines.append("    end")
        return "\n".join(lines)
    
    def _generate_html_viewer(self, output_dir: Path):
        """Generate HTML viewer"""
        # Read the content files
        markdown_content = ""
        structure_mmd = ""
        routes_mmd = ""
        systems_mmd = ""
        
        try:
            with open(output_dir / "repo_overview.md", 'r', encoding='utf-8') as f:
                markdown_content = f.read()
        except:
            markdown_content = "# Error loading markdown content"
        
        try:
            with open(output_dir / "mermaid_structure.mmd", 'r', encoding='utf-8') as f:
                structure_mmd = f.read()
        except:
            structure_mmd = ""
        
        try:
            with open(output_dir / "mermaid_routes.mmd", 'r', encoding='utf-8') as f:
                routes_mmd = f.read()
        except:
            routes_mmd = ""
        
        try:
            with open(output_dir / "mermaid_systems.mmd", 'r', encoding='utf-8') as f:
                systems_mmd = f.read()
        except:
            systems_mmd = ""
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Repository Onboarding</title>
    <link rel="stylesheet" href="templates/style.css">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Repository Onboarding</h1>
            <p>Comprehensive overview of this codebase</p>
        </header>
        
        <nav class="tabs">
            <button class="tab-button active" onclick="showTab('overview')">Overview</button>
            <button class="tab-button" onclick="showTab('structure')">Structure</button>
            <button class="tab-button" onclick="showTab('routes')">HTTP Routes</button>
            <button class="tab-button" onclick="showTab('systems')">External Systems</button>
            <button class="tab-button" onclick="showTab('raw')">Raw Markdown</button>
        </nav>
        
        <div id="overview" class="tab-content active">
            <div id="markdown-content"></div>
        </div>
        
        <div id="structure" class="tab-content">
            <h2>Project Structure</h2>
            <div id="structure-diagram"></div>
        </div>
        
        <div id="routes" class="tab-content">
            <h2>HTTP Routes</h2>
            <div id="routes-diagram"></div>
        </div>
        
        <div id="systems" class="tab-content">
            <h2>External Systems</h2>
            <div id="systems-diagram"></div>
        </div>
        
        <div id="raw" class="tab-content">
            <h2>Raw Markdown</h2>
            <pre id="raw-markdown"></pre>
        </div>
    </div>
    
    <script>
        // Embedded content
        const markdownContent = {json.dumps(markdown_content)};
        const structureMmd = {json.dumps(structure_mmd)};
        const routesMmd = {json.dumps(routes_mmd)};
        const systemsMmd = {json.dumps(systems_mmd)};
        
        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            // Render markdown
            document.getElementById('markdown-content').innerHTML = marked.parse(markdownContent);
            document.getElementById('raw-markdown').textContent = markdownContent;
            
            // Initialize Mermaid
            mermaid.initialize({{ startOnLoad: false }});
            
            // Render diagrams
            if (structureMmd.trim()) {{
                mermaid.render('structure-svg', structureMmd).then(({{svg}}) => {{
                    document.getElementById('structure-diagram').innerHTML = svg;
                }}).catch(err => {{
                    console.error('Structure diagram error:', err);
                    document.getElementById('structure-diagram').innerHTML = '<p>Error rendering structure diagram</p>';
                }});
            }} else {{
                document.getElementById('structure-diagram').innerHTML = '<p>(none)</p>';
            }}
            
            if (routesMmd.trim()) {{
                mermaid.render('routes-svg', routesMmd).then(({{svg}}) => {{
                    document.getElementById('routes-diagram').innerHTML = svg;
                }}).catch(err => {{
                    console.error('Routes diagram error:', err);
                    document.getElementById('routes-diagram').innerHTML = '<p>Error rendering routes diagram</p>';
                }});
            }} else {{
                document.getElementById('routes-diagram').innerHTML = '<p>(none)</p>';
            }}
            
            if (systemsMmd.trim()) {{
                mermaid.render('systems-svg', systemsMmd).then(({{svg}}) => {{
                    document.getElementById('systems-diagram').innerHTML = svg;
                }}).catch(err => {{
                    console.error('Systems diagram error:', err);
                    document.getElementById('systems-diagram').innerHTML = '<p>Error rendering systems diagram</p>';
                }});
            }} else {{
                document.getElementById('systems-diagram').innerHTML = '<p>(none)</p>';
            }}
        }});
        
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-button').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>"""
        
        with open(output_dir / "index.html", 'w') as f:
            f.write(html_content)
        
        # Create templates directory and CSS
        templates_dir = output_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        css_content = """/* Repo Onboarder Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.tabs {
    display: flex;
    margin-bottom: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

.tab-button {
    flex: 1;
    padding: 15px 20px;
    border: none;
    background: white;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 14px;
    font-weight: 500;
}

.tab-button:hover {
    background: #f8f9fa;
}

.tab-button.active {
    background: #007bff;
    color: white;
}

.tab-content {
    display: none;
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tab-content.active {
    display: block;
}

h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e9ecef;
}

h3 {
    color: #495057;
    margin: 20px 0 10px 0;
}

ul, ol {
    margin: 10px 0 20px 20px;
}

li {
    margin: 5px 0;
}

code {
    background: #f8f9fa;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
}

pre {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    overflow-x: auto;
    margin: 10px 0;
}

pre code {
    background: none;
    padding: 0;
}

#raw-markdown {
    white-space: pre-wrap;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 12px;
    line-height: 1.4;
}

/* Mermaid diagram styling */
.mermaid {
    text-align: center;
    margin: 20px 0;
}

/* Responsive */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .tabs {
        flex-direction: column;
    }
    
    .tab-button {
        border-bottom: 1px solid #e9ecef;
    }
    
    .tab-content {
        padding: 20px;
    }
}"""
        
        with open(templates_dir / "style.css", 'w') as f:
            f.write(css_content)

def load_environment():
    """Load environment variables from .env file if available"""
    if DOTENV_AVAILABLE:
        # Try to load .env file from current directory
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
            print("📄 Loaded environment variables from .env file")
        else:
            print("💡 Tip: Create a .env file with ANTHROPIC_API_KEY for LLM features")
    else:
        print("💡 Install python-dotenv for .env file support: pip install python-dotenv")

def clone_github_repo(github_url: str) -> str:
    """Clone a GitHub repository and return the local path"""
    import tempfile
    import subprocess
    
    # Extract repo name from URL
    repo_name = github_url.split('/')[-1].replace('.git', '')
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix=f"onboarder_{repo_name}_")
    repo_path = Path(temp_dir) / repo_name
    
    print(f"📥 Cloning {github_url}...")
    try:
        subprocess.run(['git', 'clone', github_url, str(repo_path)], 
                      check=True, capture_output=True, text=True)
        print(f"✅ Repository cloned to: {repo_path}")
        return str(repo_path)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clone repository: {e.stderr}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="Repo Onboarder - Generate onboarding documentation")
    parser.add_argument("path", help="Path to repository to analyze or GitHub URL")
    parser.add_argument("--config", help="Path to config file", default=".onboarder.yml")
    parser.add_argument("--output", help="Output directory", default="onboarding")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM explanation")
    parser.add_argument("--load-env", action="store_true", help="Load environment variables from .env file")
    parser.add_argument("--clone", action="store_true", help="Force clone if path looks like a GitHub URL")
    
    args = parser.parse_args()
    
    # Load environment variables if requested
    if args.load_env:
        load_environment()
    
    # Create configuration
    config = Config()
    config.output_dir = args.output
    if args.no_llm:
        config.llm_enabled = False
    
    # Check if path is a GitHub URL
    github_url = None
    if args.path.startswith(('https://github.com/', 'git@github.com:')) or args.clone:
        github_url = args.path
        if not github_url.startswith('https://'):
            github_url = github_url.replace('git@github.com:', 'https://github.com/')
        if not github_url.endswith('.git'):
            github_url += '.git'
        
        # Clone the repository
        repo_path = clone_github_repo(github_url)
    else:
        # Check if local path exists
        repo_path = Path(args.path)
        if not repo_path.exists():
            print(f"❌ Error: Path '{args.path}' does not exist")
            print("💡 Tip: Use a GitHub URL like 'https://github.com/user/repo' to clone and analyze")
            sys.exit(1)
        repo_path = str(repo_path)
    
    # Run analysis
    analyzer = RepoAnalyzer(repo_path, config)
    try:
        analyzer.analyze()
        analyzer.generate_outputs()
        print("🎉 Analysis complete!")
        
        if github_url:
            print(f"📁 Results saved in: {Path(repo_path) / config.output_dir}")
            print(f"🌐 Open: {Path(repo_path) / config.output_dir / 'index.html'}")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
