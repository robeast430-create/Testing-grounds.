#!/usr/bin/env python3
"""
Advanced CI/CD Pipeline Generator
Generates complete CI/CD configurations for various platforms
"""

import json
import yaml
from typing import Dict, List, Optional

class CIPipelineGenerator:
    def __init__(self, project_name: str, language: str = "python"):
        self.project_name = project_name
        self.language = language
        self.config = {}
    
    def generate_github_actions(self, features: List[str] = None) -> str:
        """Generate GitHub Actions workflow"""
        if features is None:
            features = ["test", "lint", "build", "deploy"]
        
        workflow = {
            "name": f"{self.project_name} CI/CD",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
                "release": {"types": ["published"]}
            },
            "env": {
                "PYTHON_VERSION": "3.11",
                "NODE_VERSION": "18"
            },
            "jobs": {}
        }
        
        if "lint" in features:
            workflow["jobs"]["lint"] = self._lint_job()
        
        if "test" in features:
            workflow["jobs"]["test"] = self._test_job()
        
        if "build" in features:
            workflow["jobs"]["build"] = self._build_job()
        
        if "security" in features:
            workflow["jobs"]["security"] = self._security_job()
        
        if "deploy" in features:
            workflow["jobs"]["deploy"] = self._deploy_job()
        
        return json.dumps(workflow, indent=2)
    
    def _lint_job(self) -> Dict:
        return {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v5",
                 "with": {"python-version": "${{ env.PYTHON_VERSION }}"}},
                {"name": "Install dependencies",
                 "run": "pip install flake8 black mypy"},
                {"name": "Lint with flake8", "run": "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"},
                {"name": "Format check", "run": "black --check . || true"}
            ]
        }
    
    def _test_job(self) -> Dict:
        return {
            "runs-on": "ubuntu-latest",
            "needs": "lint",
            "services": {
                "postgres": {
                    "image": "postgres:15",
                    "env": {"POSTGRES_PASSWORD": "test"},
                    "options": "--health-cmd pg_isready --health-interval 10s"
                },
                "redis": {
                    "image": "redis:7",
                    "options": "--health-cmd 'redis-cli ping'"
                }
            },
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Set up Python", "uses": "actions/setup-python@v5",
                 "with": {"python-version": "${{ env.PYTHON_VERSION }}"}},
                {"name": "Cache pip packages", "uses": "actions/cache@v3",
                 "with": {"path": "~/.cache/pip", "key": "${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}"}},
                {"name": "Install dependencies", "run": "pip install -r requirements.txt"},
                {"name": "Run tests", "run": "pytest --cov=. --cov-report=xml --cov-report=html"},
                {"name": "Upload coverage", "uses": "codecov/codecov-action@v3",
                 "with": {"token": "${{ secrets.CODECOV_TOKEN }}"}
                }
            ]
        }
    
    def _build_job(self) -> Dict:
        return {
            "runs-on": "ubuntu-latest",
            "needs": "test",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Set up Docker Buildx", "uses": "docker/setup-buildx-action@v3"},
                {"name": "Build Docker image", "run": f"docker build -t ${{ github.repository }}:${{ github.sha }} ."},
                {"name": "Test Docker image", "run": f"docker run ${{ github.repository }}:${{ github.sha }} pytest"}
            ]
        }
    
    def _security_job(self) -> Dict:
        return {
            "runs-on": "ubuntu-latest",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Run Bandit", "run": "pip install bandit && bandit -r ."},
                {"name": "Safety check", "run": "pip install safety && safety check"},
                {"name": "Trivy vulnerability scan", "uses": "aquasecurity/trivy-action@master",
                 "with": {"scan-type": "fs", "scan-ref": "."}
                }
            ]
        }
    
    def _deploy_job(self) -> Dict:
        return {
            "runs-on": "ubuntu-latest",
            "needs": "build",
            "if": "github.ref == 'refs/heads/main'",
            "steps": [
                {"uses": "actions/checkout@v4"},
                {"name": "Deploy to production", "run": "echo 'Deploying to production...'"},
                {"name": "Notify Slack", "uses": "slackapi/slack-github-action@v1",
                 "with": {"payload": "{\"text\": \"Deployment complete for ${{ github.sha }}\"}"}
                }
            ]
        }
    
    def generate_gitlab_ci(self, features: List[str] = None) -> str:
        """Generate GitLab CI configuration"""
        if features is None:
            features = ["test", "build", "deploy"]
        
        ci = {
            "stages": ["lint", "test", "build", "deploy"],
            "variables": {
                "DOCKER_IMAGE": f"registry.gitlab.com/${{CI_PROJECT_PATH}}"
            }
        }
        
        if "lint" in features:
            ci["lint"] = {
                "stage": "lint",
                "image": "python:3.11",
                "script": ["pip install flake8 black", "flake8 .", "black --check ."]
            }
        
        if "test" in features:
            ci["test"] = {
                "stage": "test",
                "image": "python:3.11",
                "services": ["postgres:15", "redis:7"],
                "script": ["pip install -r requirements.txt", "pytest", "coverage run -m pytest"],
                "coverage": "/TOTAL.*\\s+(\\d+%)/"
            }
        
        if "build" in features:
            ci["build"] = {
                "stage": "build",
                "image": "docker:20.10",
                "services": ["docker:20.10-dind"],
                "script": [
                    "docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY",
                    f"docker build -t $DOCKER_IMAGE:$CI_COMMIT_SHA .",
                    f"docker push $DOCKER_IMAGE:$CI_COMMIT_SHA"
                ]
            }
        
        if "deploy" in features:
            ci["deploy"] = {
                "stage": "deploy",
                "script": ["echo 'Deploying...'"],
                "only": ["main"]
            }
        
        return yaml.dump(ci, default_flow_style=False)
    
    def generate_jenkinsfile(self, features: List[str] = None) -> str:
        """Generate Jenkinsfile"""
        if features is None:
            features = ["test", "build", "deploy"]
        
        jenkinsfile = '''pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "%s"
        REGISTRY = "registry.example.com"
    }
    
    stages {
''' % self.project_name
        
        if "test" in features:
            jenkinsfile += '''        stage('Test') {
            steps {
                sh '''
                    pip install -r requirements.txt
                    pytest --junitxml=test-results.xml --cov=. --cov-report=xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                    cobertura coberturaReportFile: 'coverage.xml'
                }
            }
        }
'''
        
        if "build" in features:
            jenkinsfile += '''        stage('Build') {
            steps {
                sh '''
                    docker build -t $DOCKER_IMAGE:$BUILD_NUMBER .
                    docker push $REGISTRY/$DOCKER_IMAGE:$BUILD_NUMBER
                '''
            }
        }
'''
        
        if "deploy" in features:
            jenkinsfile += '''        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    kubectl set image deployment/%s image=$REGISTRY/$DOCKER_IMAGE:$BUILD_NUMBER
                '''
            }
        }
''' % self.project_name
        
        jenkinsfile += '''    }
    
    post {
        always {
            cleanWs()
        }
        success {
            emailext subject: 'SUCCESS: $PROJECT_NAME',
                     body: 'Build completed successfully',
                     to: 'team@example.com'
        }
        failure {
            emailext subject: 'FAILURE: $PROJECT_NAME',
                     body: 'Build failed',
                     to: 'team@example.com'
        }
    }
}
'''
        return jenkinsfile
    
    def generate_azure_pipelines(self, features: List[str] = None) -> str:
        """Generate Azure Pipelines configuration"""
        if features is None:
            features = ["test", "build", "deploy"]
        
        pipeline = {
            "trigger": ["main", "develop"],
            "pr": ["main", "develop"],
            "variables": {
                "pythonVersion": "3.11",
                "dockerRegistryServiceConnection": "DockerHub",
                "imageRepository": self.project_name,
                "dockerfilePath": "$(Build.SourcesDirectory)/Dockerfile",
                "tag": "$(Build.BuildId)"
            },
            "stages": []
        }
        
        if any(f in features for f in ["lint", "test"]):
            stage = {
                "stage": "Build_and_Test",
                "jobs": [{
                    "job": "Build",
                    "pool": {"vmImage": "ubuntu-latest"},
                    "steps": [
                        {"task": "UsePythonVersion@0", "inputs": {"versionSpec": "$(pythonVersion)"}},
                        {"task": "Bash@0", "displayName": "Install dependencies",
                         "inputs": {"script": "pip install -r requirements.txt"}}
                    ]
                }]
            }
            
            if "test" in features:
                stage["jobs"][0]["steps"].append(
                    {"task": "Bash@0", "displayName": "Run tests",
                     "inputs": {"script": "pytest --junitxml=test-results.xml"}}
                )
                stage["jobs"][0]["steps"].append(
                    {"task": "PublishTestResults@0", "inputs": {"testResultsFiles": "**/test-results.xml"}}
                )
            
            pipeline["stages"].append(stage)
        
        return json.dumps(pipeline, indent=2)


class KubernetesConfigGenerator:
    def __init__(self, app_name: str, image: str):
        self.app_name = app_name
        self.image = image
    
    def generate_deployment(self, replicas: int = 3, port: int = 80) -> str:
        """Generate Kubernetes deployment"""
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self.app_name,
                "labels": {"app": self.app_name}
            },
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": self.app_name}},
                "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 0}},
                "template": {
                    "metadata": {"labels": {"app": self.app_name}},
                    "spec": {
                        "containers": [{
                            "name": self.app_name,
                            "image": self.image,
                            "ports": [{"containerPort": port}],
                            "resources": {
                                "requests": {"memory": "64Mi", "cpu": "250m"},
                                "limits": {"memory": "128Mi", "cpu": "500m"}
                            },
                            "livenessProbe": {
                                "httpGet": {"path": "/health", "port": port},
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {"path": "/ready", "port": port},
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            },
                            "env": [{"name": "ENV", "value": "production"}],
                            "imagePullPolicy": "Always"
                        }]
                    }
                }
            }
        }
        return yaml.dump(deployment, default_flow_style=False)
    
    def generate_service(self, port: int = 80, target_port: int = 80) -> str:
        """Generate Kubernetes service"""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": f"{self.app_name}-service"},
            "spec": {
                "type": "LoadBalancer",
                "selector": {"app": self.app_name},
                "ports": [{"port": port, "targetPort": target_port}]
            }
        }
        return yaml.dump(service, default_flow_style=False)
    
    def generate_ingress(self, host: str, path: str = "/") -> str:
        """Generate Kubernetes ingress"""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.app_name}-ingress",
                "annotations": {
                    "nginx.ingress.kubernetes.io/rewrite-target": "/",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod"
                }
            },
            "spec": {
                "ingressClassName": "nginx",
                "tls": [{"hosts": [host], "secretName": f"{self.app_name}-tls"}],
                "rules": [{
                    "host": host,
                    "http": {"paths": [{"path": path, "pathType": "Prefix",
                                       "backend": {"service": {"name": f"{self.app_name}-service",
                                                               "port": {"number": 80}}}}]}
                }]
            }
        }
        return yaml.dump(ingress, default_flow_style=False)
    
    def generate_configmap(self, data: Dict[str, str]) -> str:
        """Generate Kubernetes configmap"""
        configmap = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {"name": f"{self.app_name}-config"},
            "data": data
        }
        return yaml.dump(configmap, default_flow_style=False)
    
    def generate_secret(self, data: Dict[str, str]) -> str:
        """Generate Kubernetes secret"""
        import base64
        encoded = {k: base64.b64encode(v.encode()).decode() for k, v in data.items()}
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {"name": f"{self.app_name}-secret"},
            "type": "Opaque",
            "data": encoded
        }
        return yaml.dump(secret, default_flow_style=False)
    
    def generate_hpa(self, min_replicas: int = 2, max_replicas: int = 10) -> str:
        """Generate Kubernetes Horizontal Pod Autoscaler"""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": f"{self.app_name}-hpa"},
            "spec": {
                "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": self.app_name},
                "minReplicas": min_replicas,
                "maxReplicas": max_replicas,
                "metrics": [{
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {"type": "Utilization", "averageUtilization": 70}
                    }
                }]
            }
        }
        return yaml.dump(hpa, default_flow_style=False)
    
    def generate_pdb(self, min_available: int = 1) -> str:
        """Generate Kubernetes Pod Disruption Budget"""
        pdb = {
            "apiVersion": "policy/v1",
            "kind": "PodDisruptionBudget",
            "metadata": {"name": f"{self.app_name}-pdb"},
            "spec": {
                "minAvailable": min_available,
                "selector": {"matchLabels": {"app": self.app_name}}
            }
        }
        return yaml.dump(pdb, default_flow_style=False)


class HelmChartGenerator:
    def __init__(self, chart_name: str):
        self.chart_name = chart_name
        self.k8s = KubernetesConfigGenerator(chart_name, f"{chart_name}:latest")
    
    def generate_chart(self) -> Dict:
        """Generate complete Helm chart structure"""
        chart = {
            "Chart.yaml": {
                "apiVersion": "v2",
                "name": self.chart_name,
                "version": "1.0.0",
                "appVersion": "1.0.0",
                "type": "application",
                "description": f"A Helm chart for {chart_name}",
                "keywords": [self.chart_name],
                "maintainers": [{"name": "Team"}]
            },
            "values.yaml": self._generate_values(),
            "templates/deployment.yaml": self.k8s.generate_deployment(),
            "templates/service.yaml": self.k8s.generate_service(),
            "templates/ingress.yaml": self.k8s.generate_ingress("example.com"),
            "templates/configmap.yaml": self.k8s.generate_configmap({"ENV": "production"}),
            "templates/secrets.yaml": self.k8s.generate_secret({"API_KEY": "secret"}),
            "templates/hpa.yaml": self.k8s.generate_hpa(),
            "templates/pdb.yaml": self.k8s.generate_pdb(),
            ".helmignore": self._generate_helmignore(),
            "README.md": self._generate_readme()
        }
        return chart
    
    def _generate_values(self) -> Dict:
        return {
            "replicaCount": 3,
            "image": {
                "repository": self.chart_name,
                "tag": "latest",
                "pullPolicy": "IfNotPresent"
            },
            "service": {
                "type": "LoadBalancer",
                "port": 80
            },
            "ingress": {
                "enabled": True,
                "className": "nginx",
                "host": "example.com",
                "annotations": {}
            },
            "resources": {
                "limits": {"cpu": "500m", "memory": "128Mi"},
                "requests": {"cpu": "250m", "memory": "64Mi"}
            },
            "autoscaling": {
                "enabled": True,
                "minReplicas": 2,
                "maxReplicas": 10,
                "targetCPUUtilizationPercentage": 70
            },
            "nodeSelector": {},
            "tolerations": [],
            "affinity": {}
        }
    
    def _generate_helmignore(self) -> str:
        return '''# Patterns to ignore when building packages.
# This supports shell glob matching.
.git/
.hg/
.helmignore
README.md
.travis.yml
.project
.pytest_cache/
'''
    
    def _generate_readme(self) -> str:
        return f'''# {self.chart_name}

A Helm chart for {self.chart_name}.

## Usage

```bash
helm install {self.chart_name} ./
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| replicaCount | Number of replicas | 3 |
| image.repository | Image repository | {self.chart_name} |
| service.port | Service port | 80 |
'''


if __name__ == "__main__":
    gen = CIPipelineGenerator("neural-agent", "python")
    
    print("GitHub Actions:")
    print(gen.generate_github_actions())
    
    print("\nGitLab CI:")
    print(gen.generate_gitlab_ci())
    
    k8s = KubernetesConfigGenerator("neural-agent", "neural-agent:latest")
    
    print("\nKubernetes Deployment:")
    print(k8s.generate_deployment())
    
    helm = HelmChartGenerator("neural-agent")
    chart = helm.generate_chart()
    
    print("\nHelm Chart Structure:")
    for key in chart.keys():
        print(f"  - {key}")