import os
import re
import ast
import subprocess
import json
from pathlib import Path

class CodeAnalyzer:
    def __init__(self, agent):
        self.agent = agent
    
    def analyze_file(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        ext = os.path.splitext(filepath)[1]
        
        if ext == ".py":
            return self._analyze_python(filepath)
        elif ext in [".js", ".ts"]:
            return self._analyze_js(filepath)
        else:
            return self._analyze_generic(filepath)
    
    def _analyze_python(self, filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            complexity = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    classes.append({"name": node.name, "methods": methods})
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)
                    complexity += self._cyclomatic_complexity(node)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            stats = os.stat(filepath)
            lines = len(content.splitlines())
            
            return {
                "file": filepath,
                "language": "Python",
                "lines": lines,
                "size_bytes": stats.st_size,
                "classes": len(classes),
                "functions": len(functions),
                "imports": len(imports),
                "complexity": complexity,
                "class_list": classes,
                "function_list": functions[:20],
                "import_list": imports[:20]
            }
        except SyntaxError as e:
            return f"Syntax error: {e}"
        except Exception as e:
            return f"Analysis error: {e}"
    
    def _cyclomatic_complexity(self, node):
        count = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                count += 1
            elif isinstance(child, ast.BoolOp):
                count += len(child.values) - 1
        return count
    
    def _analyze_js(self, filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            functions = re.findall(r'(?:function\s+(\w+)|(\w+)\s*[=:]\s*(?:async\s+)?\(|const\s+(\w+)\s*=)', content)
            classes = re.findall(r'class\s+(\w+)', content)
            imports = re.findall(r'(?:import|require)[\s(]?["\']([^"\']+)', content)
            exports = re.findall(r'export\s+(?:default\s+)?(?:function|class|const|let|var)?\s*(\w+)', content)
            
            lines = len(content.splitlines())
            
            return {
                "file": filepath,
                "language": "JavaScript/TypeScript",
                "lines": lines,
                "classes": len(classes),
                "functions": len(functions),
                "imports": len(imports),
                "exports": len(exports),
                "class_list": classes,
                "function_list": [f[0] or f[1] or f[2] for f in functions if any(f)][:20],
                "import_list": imports[:20]
            }
        except Exception as e:
            return f"Analysis error: {e}"
    
    def _analyze_generic(self, filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            lines = len(content.splitlines())
            chars = len(content)
            words = len(content.split())
            
            return {
                "file": filepath,
                "lines": lines,
                "characters": chars,
                "words": words
            }
        except Exception as e:
            return f"Error: {e}"
    
    def find_issues(self, filepath):
        issues = []
        
        if not os.path.exists(filepath):
            return [{"severity": "error", "message": f"File not found: {filepath}"}]
        
        ext = os.path.splitext(filepath)[1]
        
        if ext == ".py":
            issues.extend(self._check_python_issues(filepath))
        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
            issues.extend(self._check_js_issues(filepath))
        
        return issues
    
    def _check_python_issues(self, filepath):
        issues = []
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            if "print(" in content and not content.startswith("#!/"):
                issues.append({
                    "severity": "info",
                    "line": "mixed",
                    "message": "Consider using logging instead of print statements"
                })
            
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and len(ast.get_source_segment(content, node).splitlines()) > 50:
                    issues.append({
                        "severity": "warning",
                        "message": f"Function '{node.name}' is too long (>50 lines)"
                    })
            
            if "except:" in content:
                issues.append({
                    "severity": "warning",
                    "message": "Bare except clause found. Consider specifying exception type."
                })
            
            if re.search(r'==\s*True|==\s*False', content):
                issues.append({
                    "severity": "info",
                    "message": "Consider using 'is' for boolean comparisons"
                })
                
        except Exception as e:
            issues.append({"severity": "error", "message": str(e)})
        
        return issues
    
    def _check_js_issues(self, filepath):
        issues = []
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            if "var " in content:
                issues.append({
                    "severity": "info",
                    "message": "Consider using 'let' or 'const' instead of 'var'"
                })
            
            if "console.log" in content:
                issues.append({
                    "severity": "info",
                    "message": "Consider using a logging framework instead of console.log"
                })
            
            if "==" in content and "===" not in content:
                issues.append({
                    "severity": "warning",
                    "message": "Consider using '===' instead of '=='"
                })
                
        except Exception as e:
            issues.append({"severity": "error", "message": str(e)})
        
        return issues


class CodeGenerator:
    def __init__(self, agent):
        self.agent = agent
        self.templates = self._load_templates()
    
    def _load_templates(self):
        return {
            "python_class": '''class {class_name}:
    def __init__(self{params}):
{attributes}        pass
    
    def __str__(self):
        return f"{self.__class__.__name__}()"
''',
            "python_function": '''def {name}({params}):
    """{docstring}"""
{body}    return {return_value}
''',
            "python_test": '''import pytest
from {module} import {item}

class Test{item}:
    def test_{name}(self):
        pass
''',
            "javascript_function": '''function {name}({params}) {{
    {body}
    return {return_value};
}}
''',
            "html_page": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>Content goes here.</p>
    <script>
        console.log("Hello, World!");
    </script>
</body>
</html>
''',
            "react_component": '''import React from 'react';

function {name}() {{
    return (
        <div className="{name}">
            <h1>{name}</h1>
        </div>
    );
}}

export default {name};
''',
            "dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
''',
            "api_endpoint": '''from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/{endpoint}', methods=['GET', 'POST'])
def {endpoint}():
    if request.method == 'POST':
        data = request.get_json()
        # Handle POST request
        return jsonify({{"status": "success"}})
    # Handle GET request
    return jsonify({{"status": "ok"}})
'''
        }
    
    def generate(self, template_name, **kwargs):
        template = self.templates.get(template_name)
        if not template:
            return f"Template not found: {template_name}. Available: {', '.join(self.templates.keys())}"
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Missing template variable: {e}"
    
    def generate_file(self, filepath, template_name, **kwargs):
        content = self.generate(template_name, **kwargs)
        
        if content.startswith("Template not found") or content.startswith("Missing"):
            return content
        
        try:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
            return f"Generated {filepath}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def list_templates(self):
        return list(self.templates.keys())


class Linter:
    def __init__(self, agent):
        self.agent = agent
    
    def lint(self, filepath):
        if not os.path.exists(filepath):
            return [{"error": f"File not found: {filepath}"}]
        
        ext = os.path.splitext(filepath)[1]
        
        if ext == ".py":
            return self._lint_python(filepath)
        elif ext in [".js", ".ts"]:
            return self._lint_js(filepath)
        else:
            return [{"info": f"No linter available for {ext} files"}]
    
    def _lint_python(self, filepath):
        results = []
        
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", filepath],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                results.append({
                    "file": filepath,
                    "line": "N/A",
                    "severity": "error",
                    "message": result.stderr or "Syntax error"
                })
        except FileNotFoundError:
            pass
        
        with open(filepath, "r") as f:
            content = f.read()
            lines = content.splitlines()
            
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    results.append({
                        "file": filepath,
                        "line": i,
                        "severity": "warning",
                        "message": f"Line too long ({len(line)} > 120)"
                    })
                
                if line.rstrip() != line:
                    results.append({
                        "file": filepath,
                        "line": i,
                        "severity": "info",
                        "message": "Trailing whitespace"
                    })
                
                if line.endswith("\t"):
                    results.append({
                        "file": filepath,
                        "line": i,
                        "severity": "warning",
                        "message": "Tab character found. Consider using spaces."
                    })
        
        return results if results else [{"file": filepath, "severity": "info", "message": "No issues found"}]
    
    def _lint_js(self, filepath):
        results = []
        
        try:
            result = subprocess.run(
                ["npx", "eslint", filepath, "--format", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        for msg in item.get("messages", []):
                            results.append({
                                "file": filepath,
                                "line": msg.get("line", 0),
                                "severity": msg.get("severity", "warning"),
                                "message": msg.get("message", "")
                            })
                except:
                    pass
        except:
            pass
        
        return results if results else [{"file": filepath, "severity": "info", "message": "No issues found"}]


class DependencyManager:
    def __init__(self, agent):
        self.agent = agent
    
    def analyze_dependencies(self):
        deps = {}
        
        if os.path.exists("requirements.txt"):
            deps["python"] = self._parse_requirements()
        
        if os.path.exists("package.json"):
            deps["javascript"] = self._parse_package_json()
        
        if os.path.exists("Cargo.toml"):
            deps["rust"] = self._parse_cargo()
        
        if os.path.exists("go.mod"):
            deps["go"] = self._parse_go_mod()
        
        return deps
    
    def _parse_requirements(self):
        deps = []
        with open("requirements.txt", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    deps.append(line)
        return deps
    
    def _parse_package_json(self):
        with open("package.json", "r") as f:
            data = json.load(f)
        return {
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {})
        }
    
    def _parse_cargo(self):
        deps = []
        with open("Cargo.toml", "r") as f:
            in_deps = False
            for line in f:
                if line.strip() == "[dependencies]":
                    in_deps = True
                elif line.strip().startswith("["):
                    in_deps = False
                elif in_deps and line.strip():
                    deps.append(line.strip())
        return deps
    
    def _parse_go_mod(self):
        deps = []
        with open("go.mod", "r") as f:
            for line in f:
                if line.startswith("require ("):
                    continue
                if line.startswith(")"):
                    break
                if line.startswith("require"):
                    parts = line.split()
                    if len(parts) >= 2:
                        deps.append(parts[1])
        return deps
    
    def check_outdated(self):
        outdated = []
        
        if os.path.exists("requirements.txt"):
            try:
                result = subprocess.run(
                    ["pip", "list", "--outdated"],
                    capture_output=True,
                    text=True
                )
                outdated.extend(result.stdout.splitlines()[:20])
            except:
                pass
        
        if os.path.exists("package.json"):
            try:
                result = subprocess.run(
                    ["npm", "outdated"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    outdated.extend(result.stdout.splitlines()[:20])
            except:
                pass
        
        return outdated if outdated else ["All dependencies are up to date"]


class TestGenerator:
    def __init__(self, agent):
        self.agent = agent
    
    def generate_tests(self, filepath):
        if not os.path.exists(filepath):
            return f"File not found: {filepath}"
        
        ext = os.path.splitext(filepath)[1]
        
        if ext == ".py":
            return self._generate_pytest(filepath)
        elif ext in [".js", ".ts"]:
            return self._generate_jest(filepath)
        
        return f"No test generator for {ext} files"
    
    def _generate_pytest(self, filepath):
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            module = os.path.splitext(os.path.basename(filepath))[0]
            classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
            functions = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            
            test_lines = ["import pytest", f"from {module} import *", ""]
            
            for cls in classes:
                test_lines.append(f"class Test{cls}:")
                test_lines.append(f"    def test_init(self):")
                test_lines.append(f"        obj = {cls}()")
                test_lines.append(f"        assert obj is not None")
                test_lines.append("")
            
            for func in functions[:10]:
                if not func.startswith("_"):
                    test_lines.append(f"def test_{func}():")
                    test_lines.append(f"    result = {func}()")
                    test_lines.append(f"    # Add assertions")
                    test_lines.append("")
            
            test_file = filepath.replace(".py", "_test.py")
            
            if os.path.exists(test_file):
                return f"Test file already exists: {test_file}"
            
            with open(test_file, "w") as f:
                f.write("\n".join(test_lines))
            
            return f"Generated tests: {test_file}"
        
        except Exception as e:
            return f"Error generating tests: {e}"
    
    def _generate_jest(self, filepath):
        filename = os.path.splitext(os.path.basename(filepath))[0]
        test_file = os.path.join(os.path.dirname(filepath), f"{filename}.test.js")
        
        template = f'''describe('{filename}', () => {{
    beforeEach(() => {{
        // Setup
    }});

    afterEach(() => {{
        // Cleanup
    }});

    test('should initialize', () => {{
        expect(true).toBe(true);
    }});
}});
'''
        
        if os.path.exists(test_file):
            return f"Test file already exists: {test_file}"
        
        with open(test_file, "w") as f:
            f.write(template)
        
        return f"Generated tests: {test_file}"