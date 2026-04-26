import json
import os
from datetime import datetime

class PromptTemplate:
    def __init__(self, name, template, description=""):
        self.name = name
        self.template = template
        self.description = description
        self.variables = self._extract_variables()
    
    def _extract_variables(self):
        import re
        return re.findall(r'\{(\w+)\}', self.template)
    
    def render(self, **kwargs):
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            return f"Missing variable: {e}"
    
    def __str__(self):
        return f"{self.name}: {self.description}"

class PromptManager:
    def __init__(self, agent):
        self.agent = agent
        self.templates = {}
        self.templates_file = "./auth_data/prompt_templates.json"
        self._load_templates()
        self._init_defaults()
    
    def _load_templates(self):
        if os.path.exists(self.templates_file):
            with open(self.templates_file, "r") as f:
                data = json.load(f)
                for name, info in data.items():
                    self.templates[name] = PromptTemplate(
                        name, info["template"], info.get("description", "")
                    )
    
    def _save_templates(self):
        data = {name: {
            "template": t.template,
            "description": t.description
        } for name, t in self.templates.items()}
        
        with open(self.templates_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _init_defaults(self):
        if not self.templates:
            defaults = {
                "greeting": {
                    "template": "Hello, {name}! Welcome to {system_name}. How can I assist you today?",
                    "description": "Greeting template"
                },
                "summary": {
                    "template": "Please summarize the following information concisely:\n\n{content}",
                    "description": "Summarize content"
                },
                "analyze": {
                    "template": "Analyze the following and provide insights:\n\n{content}\n\nConsider: {considerations}",
                    "description": "Analyze content with considerations"
                },
                "explain": {
                    "template": "Explain in simple terms what the following means:\n\n{content}",
                    "description": "Simple explanation"
                },
                "help_request": {
                    "template": "The user needs help with: {task}\n\nContext: {context}\n\nPlease provide guidance.",
                    "description": "Help request with context"
                },
                "research": {
                    "template": "Research the topic '{topic}' and provide comprehensive information.",
                    "description": "Research template"
                },
                "code_review": {
                    "template": "Review the following code for issues and improvements:\n\n```{language}\n{code}\n```",
                    "description": "Code review template"
                },
                "task_breakdown": {
                    "template": "Break down this task into steps:\n\n{task}\n\nConsider: {constraints}",
                    "description": "Break down task into steps"
                }
            }
            
            for name, info in defaults.items():
                self.templates[name] = PromptTemplate(name, info["template"], info["description"])
            
            self._save_templates()
    
    def add_template(self, name, template, description=""):
        self.templates[name] = PromptTemplate(name, template, description)
        self._save_templates()
        return f"Template '{name}' added"
    
    def get_template(self, name):
        return self.templates.get(name)
    
    def render_template(self, name, **kwargs):
        template = self.templates.get(name)
        if not template:
            return f"Template not found: {name}"
        return template.render(**kwargs)
    
    def list_templates(self):
        return [{
            "name": name,
            "description": t.description,
            "variables": t.variables
        } for name, t in self.templates.items()]
    
    def delete_template(self, name):
        if name in self.templates:
            del self.templates[name]
            self._save_templates()
            return f"Template '{name}' deleted"
        return f"Template not found: {name}"
    
    def update_template(self, name, template=None, description=None):
        if name not in self.templates:
            return f"Template not found: {name}"
        
        t = self.templates[name]
        if template:
            t.template = template
            t.variables = t._extract_variables()
        if description:
            t.description = description
        
        self._save_templates()
        return f"Template '{name}' updated"