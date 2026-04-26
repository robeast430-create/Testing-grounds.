import os
import json
import yaml

class TemplateLibrary:
    def __init__(self):
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        self.templates = {
            "frontend": {
                "react_component": '''import React, { useState, useEffect } from 'react';

const {name} = () => {{
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {{
    fetchData();
  }}, []);

  const fetchData = async () => {{
    try {{
      const response = await fetch('/api/{name}');
      const result = await response.json();
      setData(result);
      setLoading(false);
    }} catch (err) {{
      setError(err.message);
      setLoading(false);
    }}
  }};

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{{error}}</div>;

  return (
    <div className="{name}">
      <h2>{'{name}'}</h2>
      <div className="content">
        {{data && (
          <pre>{{JSON.stringify(data, null, 2)}}</pre>
        )}}
      </div>
    </div>
  );
}};

export default {name};
''',
                "vue_component": '''<template>
  <div class="{name}">
    <h2>{{ title }}</h2>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else class="content">
      <pre>{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </div>
</template>

<script>
export default {{
  name: '{name}',
  data() {{
    return {{
      title: '{name}',
      data: null,
      loading: true,
      error: null
    }};
  }},
  async created() {{
    await this.fetchData();
  }},
  methods: {{
    async fetchData() {{
      try {{
        const response = await fetch('/api/{name}');
        this.data = await response.json();
      }} catch (err) {{
        this.error = err.message;
      }} finally {{
        this.loading = false;
      }}
    }}
  }}
}};
</script>

<style scoped>
.{name} {{
  padding: 20px;
}}
</style>
''',
                "svelte_component": '''<script>
  import {{ onMount }} from 'svelte';

  let data = null;
  let loading = true;
  let error = null;

  onMount(async () => {{
    await fetchData();
  }});

  async function fetchData() {{
    try {{
      const response = await fetch('/api/{name}');
      data = await response.json();
    }} catch (err) {{
      error = err.message;
    }} finally {{
      loading = false;
    }}
  }}
</script>

<div class="{name}">
  <h2>{name}</h2>
  {{#if loading}}
    <p>Loading...</p>
  {{/if}}
  {{#if error}}
    <p class="error">{{error}}</p>
  {{/if}}
  {{#if data}}
    <pre>{{JSON.stringify(data, null, 2)}}</p>
  {{/if}}
</div>
'''
            },
            "backend": {
                "flask_route": '''from flask import Blueprint, jsonify, request

{name}_bp = Blueprint('{name}', __name__, url_prefix='/api/{name}')

@{name}_bp.route('/', methods=['GET'])
def get_{name}():
    """Get all {name} items."""
    return jsonify({{"items": [], "count": 0}})

@{name}_bp.route('/<int:item_id>', methods=['GET'])
def get_{name}_item(item_id):
    """Get a specific {name} item."""
    return jsonify({{"id": item_id}})

@{name}_bp.route('/', methods=['POST'])
def create_{name}():
    """Create a new {name} item."""
    data = request.get_json()
    return jsonify({{"id": 1, **data}}), 201

@{name}_bp.route('/<int:item_id>', methods=['PUT'])
def update_{name}(item_id):
    """Update a {name} item."""
    data = request.get_json()
    return jsonify({{"id": item_id, **data}})

@{name}_bp.route('/<int:item_id>', methods=['DELETE'])
def delete_{name}(item_id):
    """Delete a {name} item."""
    return '', 204
''',
                "fastapi_endpoint": '''from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api/{name}", tags=["{name}"])

class {name}Model(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None

class {name}Create(BaseModel):
    name: str
    description: Optional[str] = None

class {name}Update(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

@{name}_storage: List[{name}Model] = []

@router.get("/", response_model=List[{name}Model])
async def get_all_{name}():
    """Get all {name} items."""
    return {name}_storage

@router.get("/{{item_id}}", response_model={name}Model)
async def get_{name}(item_id: int):
    """Get a specific {name} item."""
    for item in {name}_storage:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="{name} not found")

@router.post("/", response_model={name}Model, status_code=status.HTTP_201_CREATED)
async def create_{name}(item: {name}Create):
    """Create a new {name} item."""
    new_item = {name}Model(
        id=len({name}_storage) + 1,
        name=item.name,
        description=item.description,
        created_at=datetime.now()
    )
    {name}_storage.append(new_item)
    return new_item

@router.put("/{{item_id}}", response_model={name}Model)
async def update_{name}(item_id: int, item: {name}Update):
    """Update a {name} item."""
    for i, existing in enumerate({name}_storage):
        if existing.id == item_id:
            if item.name is not None:
                existing.name = item.name
            if item.description is not None:
                existing.description = item.description
            return existing
    raise HTTPException(status_code=404, detail="{name} not found")

@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{name}(item_id: int):
    """Delete a {name} item."""
    global {name}_storage
    {name}_storage = [item for item in {name}_storage if item.id != item_id]
''',
                "django_view": '''from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
import json

def {name}_list(request):
    """List all {name} items."""
    return JsonResponse({{"items": [], "count": 0}})

def {name}_detail(request, pk):
    """Get a specific {name} item."""
    return JsonResponse({{"id": pk}})

@csrf_exempt
@require_http_methods(["POST"])
def {name}_create(request):
    """Create a new {name} item."""
    data = json.loads(request.body)
    return JsonResponse({{"id": 1, **data}}, status=201)

@csrf_exempt
@require_http_methods(["PUT"])
def {name}_update(request, pk):
    """Update a {name} item."""
    data = json.loads(request.body)
    return JsonResponse({{"id": pk, **data}})

@csrf_exempt
@require_http_methods(["DELETE"])
def {name}_delete(request, pk):
    """Delete a {name} item."""
    return JsonResponse({{"deleted": True}})
''',
                "express_route": '''const express = require('express');
const router = express.Router();

// Mock data store
let {name}s = [
  {{ id: 1, name: 'Item 1', createdAt: new Date() }},
  {{ id: 2, name: 'Item 2', createdAt: new Date() }}
];

// GET /api/{name} - List all {name}s
router.get('/', (req, res) => {{
  res.json({{
    items: {name}s,
    count: {name}s.length
  }});
}});

// GET /api/{name}/:id - Get a specific {name}
router.get('/:id', (req, res) => {{
  const {{ id }} = req.params;
  const item = {name}s.find(i => i.id === parseInt(id));
  
  if (!item) {{
    return res.status(404).json({{ error: '{name} not found' }});
  }}
  
  res.json(item);
}});

// POST /api/{name} - Create a new {name}
router.post('/', (req, res) => {{
  const {{ name, description }} = req.body;
  const newItem = {{
    id: {name}s.length + 1,
    name,
    description,
    createdAt: new Date()
  }};
  
  {name}s.push(newItem);
  res.status(201).json(newItem);
}});

// PUT /api/{name}/:id - Update a {name}
router.put('/:id', (req, res) => {{
  const {{ id }} = req.params;
  const index = {name}s.findIndex(i => i.id === parseInt(id));
  
  if (index === -1) {{
    return res.status(404).json({{ error: '{name} not found' }});
  }}
  
  {name}s[index] = {{ ...{name}s[index], ...req.body }};
  res.json({name}s[index]);
}});

// DELETE /api/{name}/:id - Delete a {name}
router.delete('/:id', (req, res) => {{
  const {{ id }} = req.params;
  const index = {name}s.findIndex(i => i.id === parseInt(id));
  
  if (index === -1) {{
    return res.status(404).json({{ error: '{name} not found' }});
  }}
  
  {name}s.splice(index, 1);
  res.status(204).send();
}});

module.exports = router;
'''
            },
            "database": {
                "postgres_schema": '''-- Create {name} table
CREATE TABLE IF NOT EXISTS {name}s (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create index for faster lookups
CREATE INDEX idx_{name}s_name ON {name}s(name);
CREATE INDEX idx_{name}s_created_at ON {name}s(created_at DESC);

-- Add comments
COMMENT ON TABLE {name}s IS 'Table storing {name} information';
COMMENT ON COLUMN {name}s.name IS 'Name of the {name}';
COMMENT ON COLUMN {name}s.description IS 'Detailed description';
COMMENT ON COLUMN {name}s.is_active IS 'Whether the {name} is active';

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_{name}s_updated_at
    BEFORE UPDATE ON {name}s
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
''',
                "mongodb_schema": '''
// {name} Collection Schema
{{
  name: "{name}",
  version: 1,
  schema: {{
    _id: ObjectId,
    name: {{
      type: String,
      required: true,
      trim: true,
      maxlength: 255
    }},
    description: {{
      type: String,
      trim: true,
      maxlength: 2000
    }},
    createdAt: {{
      type: Date,
      default: Date.now
    }},
    updatedAt: {{
      type: Date,
      default: Date.now
    }},
    isActive: {{
      type: Boolean,
      default: true
    }},
    tags: [String],
    metadata: Object
  }},
  indexes: [
    {{ name: 'name_text', keys: {{ name: 'text' }} }},
    {{ name: 'createdAt_idx', keys: {{ createdAt: -1 }} }},
    {{ name: 'isActive_idx', keys: {{ isActive: 1 }} }}
  ],
  validators: {{
    $jsonSchema: {{
      bsonType: "object",
      required: ["name"],
      properties: {{
        name: {{
          bsonType: "string",
          minLength: 1,
          maxLength: 255
        }}
      }}
    }}
  }}
}}
''',
                "redis_schema": '''# Redis Key Schema for {name}

# Key patterns
{name}:all           -> Set of all {name} IDs
{name}:{{id}}        -> Hash containing {name} data
{name}:name:{{name}} -> ID of {name} by name lookup
{name}:created:sort -> Sorted set by creation time
{name}:count         -> Counter for total {name}s

# Example commands:
# HSET {name}:1 name "Test" description "Description" created_at "2024-01-01"
# SADD {name}:all 1
# SET {name}:name:Test 1
# ZADD {name}:created:sort 1704067200 1
# INCR {name}:count

# TTL settings (in seconds)
# {name}:{{id}} -> 86400 (24 hours)

# Memory optimization
# {name}:count -> Use INCR/DECR for atomic counter ops
# {name}:all -> Keep under 10000 members for performance
'''
            },
            "infrastructure": {
                "terraform_aws": '''# Terraform configuration for AWS {name}
terraform {{
  required_version = ">= 1.0"
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region
}}

# Variables
variable "aws_region" {{
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}}

variable "environment" {{
  description = "Environment name"
  type        = string
  default     = "dev"
}}

# {name} resources
resource "aws_instance" "{name}" {{
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  tags = {{
    Name        = "{name}-\\{{var.environment}}"
    Environment = var.environment
  }}
}}

# Security group
resource "aws_security_group" "{name}_sg" {{
  name        = "{name}-\\{{var.environment}}-sg"
  description = "Security group for {name}"

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  tags = {{
    Name = "{name}-\\{{var.environment}}-sg"
  }}
}}

# Outputs
output "{name}_instance_id" {{
  description = "Instance ID"
  value       = aws_instance.{name}.id
}}

output "{name}_public_ip" {{
  description = "Public IP address"
  value       = aws_instance.{name}.public_ip
}}
''',
                "github_actions": '''name: CI/CD Pipeline for {name}

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  NODE_VERSION: '18.x'
  PYTHON_VERSION: '3.11'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: \\${{ env.NODE_VERSION }}
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: \\${{ env.PYTHON_VERSION }}
      - run: pip install -r requirements.txt
      - run: pytest --cov=. --cov-report=xml

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build Docker image
        run: docker build -t \\${{ github.repository }}:\\${{ github.sha }} .
      - name: Push to registry
        run: |
          docker push \\${{ github.repository }}:\\${{ github.sha }}

  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to production
        run: |
          echo "Deploying..."
''',
                "kubernetes_manifest": '''apiVersion: v1
kind: Namespace
metadata:
  name: {name}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-deployment
  namespace: {name}
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
        version: v1
    spec:
      containers:
      - name: {name}
        image: {name}:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: {name}-service
  namespace: {name}
spec:
  type: LoadBalancer
  selector:
    app: {name}
  ports:
  - port: 80
    targetPort: 8080
'''
            },
            "testing": {
                "pytest_fixture": '''import pytest
import pytest_asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {{
        "id": 1,
        "name": "Test {name}",
        "description": "A test {name}",
        "is_active": True,
        "tags": ["test", "fixture"]
    }}

@pytest.fixture
def mock_db():
    """Provide a mock database."""
    db = Mock()
    db.query = Mock(return_value=[])
    db.insert = Mock(return_value={{"id": 1}})
    db.update = Mock(return_value={{"success": True}})
    db.delete = Mock(return_value={{"success": True}})
    return db

@pytest.fixture
def api_client():
    """Provide an API test client."""
    from flask import Flask
    app = Flask(__name__)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest_asyncio.fixture
async def async_mock():
    """Provide an async mock."""
    return AsyncMock()

@pytest.fixture(params=[
    {{"id": 1, "name": "Test 1"}},
    {{"id": 2, "name": "Test 2"}},
    {{"id": 3, "name": "Test 3"}}
])
def param_data(request):
    """Provide parameterized test data."""
    return request.param
''',
                "jest_test": '''describe('{name}', () => {{
  let {name}Service;
  let mockRepository;
  
  beforeEach(() => {{
    mockRepository = {{
      findById: jest.fn(),
      findAll: jest.fn(),
      create: jest.fn(),
      update: jest.fn(),
      delete: jest.fn()
    }};
    {name}Service = new {name}Service(mockRepository);
  }});

  describe('getById', () => {{
    it('should return a {name} by id', async () => {{
      const mockData = {{ id: 1, name: 'Test {name}' }};
      mockRepository.findById.mockResolvedValue(mockData);
      
      const result = await {name}Service.getById(1);
      
      expect(result).toEqual(mockData);
      expect(mockRepository.findById).toHaveBeenCalledWith(1);
    }});

    it('should throw error when {name} not found', async () => {{
      mockRepository.findById.mockResolvedValue(null);
      
      await expect({name}Service.getById(999)).rejects.toThrow('{name} not found');
    }});
  }});

  describe('create', () => {{
    it('should create a new {name}', async () => {{
      const inputData = {{ name: 'New {name}' }};
      const createdData = {{ id: 1, ...inputData }};
      mockRepository.create.mockResolvedValue(createdData);
      
      const result = await {name}Service.create(inputData);
      
      expect(result).toEqual(createdData);
      expect(mockRepository.create).toHaveBeenCalledWith(inputData);
    }});
  }});

  describe('update', () => {{
    it('should update an existing {name}', async () => {{
      const updateData = {{ name: 'Updated {name}' }};
      mockRepository.update.mockResolvedValue({{ id: 1, ...updateData }});
      
      const result = await {name}Service.update(1, updateData);
      
      expect(result.name).toBe('Updated {name}');
    }});
  }});

  describe('delete', () => {{
    it('should delete a {name}', async () => {{
      mockRepository.delete.mockResolvedValue({{ success: true }});
      
      await expect({name}Service.delete(1)).resolves.toBeTruthy();
    }});
  }});
}});
'''
            }
        }
    
    def get(self, category, template_name, **kwargs):
        template = self.templates.get(category, {}).get(template_name)
        if not template:
            return None
        
        return template.format(**kwargs)
    
    def list_categories(self):
        return list(self.templates.keys())
    
    def list_templates(self, category):
        return list(self.templates.get(category, {}).keys())
    
    def add_template(self, category, name, template):
        if category not in self.templates:
            self.templates[category] = {}
        self.templates[category][name] = template


class CICDTemplates:
    def __init__(self):
        self.pipelines = {}
        self._load_pipelines()
    
    def _load_pipelines(self):
        self.pipelines = {
            "github_actions": {
                "basic": '''name: CI Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          echo "Running tests..."
''',
                "docker_build": '''name: Docker Build & Push

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
'''
            },
            "gitlab_ci": {
                "basic": '''stages:
  - build
  - test
  - deploy

variables:
  DOCKER_IMAGE: registry.example.com/app

build:
  stage: build
  script:
    - echo "Building..."
  artifacts:
    paths:
      - build/

test:
  stage: test
  script:
    - echo "Testing..."
  needs:
    - build

deploy:
  stage: deploy
  script:
    - echo "Deploying..."
  only:
    - main
'''
            },
            "jenkinsfile": '''pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'app:latest'
    }
    
    stages {
        stage('Build') {
            steps {
                echo 'Building...'
            }
        }
        
        stage('Test') {
            steps {
                echo 'Testing...'
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying...'
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
'''
        }
    
    def get_pipeline(self, platform, name="basic"):
        return self.pipelines.get(platform, {}).get(name)


class WebhookTemplates:
    def __init__(self):
        self.templates = {
            "slack": {
                "message": '''{
  "blocks": [
    {{
      "type": "section",
      "text": {{
        "type": "mrkdwn",
        "text": "*Build Update*"
      }}
    }},
    {{
      "type": "section",
      "fields": [
        {{
          "type": "mrkdwn",
          "text": "*Status:* \\n${{status}}"
        }},
        {{
          "type": "mrkdwn",
          "text": "*Commit:* \\n${{commit}}"
        }}
      ]
    }},
    {{
      "type": "actions",
      "elements": [
        {{
          "type": "button",
          "text": {{"type": "plain_text", "text": "View Details"}},
          "url": "${{url}}"
        }}
      ]
    }}
  ]
}'''
            },
            "discord": {
                "embed": '''{{
  "title": "${{title}}",
  "description": "${{description}}",
  "color": 15105570,
  "fields": [
    {{
      "name": "Status",
      "value": "${{status}}",
      "inline": true
    }},
    {{
      "name": "Branch",
      "value": "${{branch}}",
      "inline": true
    }}
  ],
  "timestamp": "${{timestamp}}"
}}'''
            },
            "teams": {
                "message": '''{{
  "@type": "MessageCard",
  "@context": "http://schema.org/extensions",
  "themeColor": "0076D7",
  "summary": "${{summary}}",
  "sections": [{{
    "activityTitle": "${{title}}",
    "facts": [
      {{
        "name": "Status",
        "value": "${{status}}"
      }},
      {{
        "name": "Environment",
        "value": "${{environment}}"
      }}
    ],
    "markdown": true
  }}]
}}'''
            }
        }
    
    def get_template(self, platform, template_type="message"):
        return self.templates.get(platform, {}).get(template_type)


class CronExpressions:
    SCHEDULE_EXAMPLES = {
        "every_minute": "* * * * *",
        "every_5_minutes": "*/5 * * * *",
        "every_15_minutes": "*/15 * * * *",
        "every_30_minutes": "*/30 * * * *",
        "every_hour": "0 * * * *",
        "every_day_midnight": "0 0 * * *",
        "every_day_noon": "0 12 * * *",
        "every_sunday": "0 0 * * 0",
        "every_monday": "0 0 * * 1",
        "every_month": "0 0 1 * *",
        "monday_to_friday": "0 0 * * 1-5",
        "weekends": "0 0 * * 0,6"
    }
    
    @classmethod
    def get(cls, schedule_name):
        return cls.SCHEDULE_EXAMPLES.get(schedule_name)
    
    @classmethod
    def validate(cls, expression):
        parts = expression.split()
        if len(parts) != 5:
            return False
        
        patterns = [
            r'^(\*|[\d,\-\/]+)$',  # minute
            r'^(\*|[\d,\-\/]+)$',  # hour
            r'^(\*|[\d,\-\/]+)$',  # day
            r'^(\*|[\d,\-\/]+)$',  # month
            r'^(\*|[\d,\-\/]+)$'   # weekday
        ]
        
        import re
        for i, part in enumerate(parts):
            if not re.match(patterns[i], part):
                return False
        
        return True


class ErrorCodes:
    CODES = {
        "auth": {
            1001: "Invalid credentials",
            1002: "Token expired",
            1003: "Unauthorized access",
            1004: "Account locked",
            1005: "Session expired"
        },
        "validation": {
            2001: "Invalid input format",
            2002: "Missing required field",
            2003: "Field too long",
            2004: "Invalid email format",
            2005: "Password too weak"
        },
        "database": {
            3001: "Connection failed",
            3002: "Query timeout",
            3003: "Duplicate entry",
            3004: "Foreign key violation",
            3005: "Record not found"
        },
        "api": {
            4001: "Rate limit exceeded",
            4002: "Invalid API key",
            4003: "Endpoint not found",
            4004: "Method not allowed",
            4005: "Request too large"
        },
        "system": {
            5001: "Internal server error",
            5002: "Service unavailable",
            5003: "Maintenance mode",
            5004: "Configuration error",
            5005: "Resource not available"
        }
    }
    
    @classmethod
    def get(cls, category, code):
        return cls.CODES.get(category, {}).get(code)
    
    @classmethod
    def format_response(cls, category, code, details=None):
        message = cls.get(category, code)
        return {
            "error": {
                "code": code,
                "category": category,
                "message": message,
                "details": details
            }
        }


class MarkdownTemplates:
    TEMPLATES = {
        "readme": '''# {project_name}

{description}

## Installation

```bash
pip install {package_name}
```

## Quick Start

```python
import {package_name}

# Your code here
```

## Features

- Feature 1
- Feature 2
- Feature 3

## Documentation

For full documentation, visit [docs](docs/).

## License

{license}
''',
        "changelog": '''# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Initial implementation

### Changed

### Deprecated

### Removed

### Fixed

### Security
''',
        "contributing": '''# Contributing to {project_name}

Welcome! We're glad you're interested in contributing.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a branch

## Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
```

## Making Changes

1. Make your changes
2. Add tests
3. Update documentation
4. Submit a pull request

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
''',
        "pull_request": '''## Description

<!-- What does this PR do? -->

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Checklist

- [ ] Tests pass
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No warnings introduced

## Screenshots (if applicable)

<!-- Add screenshots here -->
'''
    }
    
    @classmethod
    def get(cls, template_name, **kwargs):
        template = cls.TEMPLATES.get(template_name)
        if template:
            return template.format(**kwargs)
        return None


class JSONSchemas:
    SCHEMAS = {
        "error": {
            "type": "object",
            "properties": {
                "error": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "integer"},
                        "message": {"type": "string"},
                        "details": {"type": "object"}
                    },
                    "required": ["code", "message"]
                }
            },
            "required": ["error"]
        },
        "pagination": {
            "type": "object",
            "properties": {
                "items": {"type": "array"},
                "total": {"type": "integer"},
                "page": {"type": "integer"},
                "page_size": {"type": "integer"},
                "has_next": {"type": "boolean"},
                "has_prev": {"type": "boolean"}
            },
            "required": ["items", "total", "page", "page_size"]
        },
        "api_response": {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "data": {"type": "object"},
                "error": {"type": "object"},
                "meta": {"type": "object"}
            },
            "required": ["success"]
        }
    }
    
    @classmethod
    def get(cls, schema_name):
        return cls.SCHEMAS.get(schema_name)
    
    @classmethod
    def validate(cls, schema_name, data):
        import jsonschema
        schema = cls.SCHEMAS.get(schema_name)
        if not schema:
            return False
        
        try:
            jsonschema.validate(data, schema)
            return True
        except jsonschema.ValidationError:
            return False