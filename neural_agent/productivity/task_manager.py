import json
import os
from datetime import datetime
from uuid import uuid4

class Task:
    def __init__(self, title, description="", priority="medium", due_date=None):
        self.id = str(uuid4())[:8]
        self.title = title
        self.description = description
        self.priority = priority
        self.status = "todo"
        self.due_date = due_date
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.completed_at = None
        self.tags = []
        self.subtasks = []
        self.comments = []
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "tags": self.tags,
            "subtasks": self.subtasks,
            "comments": self.comments
        }
    
    @staticmethod
    def from_dict(data):
        task = Task(data["title"], data.get("description", ""), data.get("priority", "medium"), data.get("due_date"))
        task.id = data["id"]
        task.status = data.get("status", "todo")
        task.created_at = data.get("created_at", datetime.now().isoformat())
        task.updated_at = data.get("updated_at", datetime.now().isoformat())
        task.completed_at = data.get("completed_at")
        task.tags = data.get("tags", [])
        task.subtasks = data.get("subtasks", [])
        task.comments = data.get("comments", [])
        return task


class Project:
    def __init__(self, name, description=""):
        self.id = str(uuid4())[:8]
        self.name = name
        self.description = description
        self.tasks = []
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.tags = []
    
    def add_task(self, task):
        self.tasks.append(task)
        self.updated_at = datetime.now().isoformat()
    
    def remove_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self.updated_at = datetime.now().isoformat()
    
    def get_task(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_tasks_by_status(self, status):
        return [t for t in self.tasks if t.status == status]
    
    def get_tasks_by_priority(self, priority):
        return [t for t in self.tasks if t.priority == priority]
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": self.tags
        }
    
    @staticmethod
    def from_dict(data):
        project = Project(data["name"], data.get("description", ""))
        project.id = data["id"]
        project.created_at = data.get("created_at", datetime.now().isoformat())
        project.updated_at = data.get("updated_at", datetime.now().isoformat())
        project.tags = data.get("tags", [])
        project.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return project


class ProjectManager:
    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.projects_file = os.path.join(data_dir, "projects.json")
        self.projects = self._load()
    
    def _load(self):
        if os.path.exists(self.projects_file):
            with open(self.projects_file, "r") as f:
                data = json.load(f)
                return [Project.from_dict(p) for p in data]
        return []
    
    def _save(self):
        with open(self.projects_file, "w") as f:
            json.dump([p.to_dict() for p in self.projects], f, indent=2)
    
    def create_project(self, name, description=""):
        project = Project(name, description)
        self.projects.append(project)
        self._save()
        return project
    
    def delete_project(self, project_id):
        self.projects = [p for p in self.projects if p.id != project_id]
        self._save()
        return "Project deleted"
    
    def get_project(self, project_id):
        for p in self.projects:
            if p.id == project_id:
                return p
        return None
    
    def create_task(self, project_id, title, description="", priority="medium", due_date=None):
        project = self.get_project(project_id)
        if not project:
            return "Project not found"
        
        task = Task(title, description, priority, due_date)
        project.add_task(task)
        self._save()
        return task
    
    def update_task(self, project_id, task_id, **kwargs):
        project = self.get_project(project_id)
        if not project:
            return "Project not found"
        
        task = project.get_task(task_id)
        if not task:
            return "Task not found"
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now().isoformat()
        
        if kwargs.get("status") == "done":
            task.completed_at = datetime.now().isoformat()
        
        self._save()
        return task
    
    def delete_task(self, project_id, task_id):
        project = self.get_project(project_id)
        if not project:
            return "Project not found"
        
        project.remove_task(task_id)
        self._save()
        return "Task deleted"
    
    def list_projects(self):
        return [{
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "task_count": len(p.tasks),
            "created_at": p.created_at
        } for p in self.projects]
    
    def list_tasks(self, project_id, status=None, priority=None):
        project = self.get_project(project_id)
        if not project:
            return []
        
        tasks = project.tasks
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        
        return [t.to_dict() for t in tasks]
    
    def get_stats(self, project_id):
        project = self.get_project(project_id)
        if not project:
            return {}
        
        tasks = project.tasks
        return {
            "total": len(tasks),
            "todo": len([t for t in tasks if t.status == "todo"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "done": len([t for t in tasks if t.status == "done"]),
            "blocked": len([t for t in tasks if t.status == "blocked"]),
            "high_priority": len([t for t in tasks if t.priority == "high" and t.status != "done"]),
            "overdue": len([t for t in tasks if t.due_date and t.due_date < datetime.now().isoformat() and t.status != "done"])
        }
    
    def export_project(self, project_id, filepath):
        project = self.get_project(project_id)
        if not project:
            return "Project not found"
        
        with open(filepath, "w") as f:
            json.dump(project.to_dict(), f, indent=2)
        
        return f"Exported to {filepath}"
    
    def import_project(self, filepath):
        if not os.path.exists(filepath):
            return "File not found"
        
        with open(filepath, "r") as f:
            data = json.load(f)
        
        project = Project.from_dict(data)
        project.id = str(uuid4())[:8]
        self.projects.append(project)
        self._save()
        
        return f"Imported project: {project.name}"


class KanbanBoard:
    def __init__(self, project_manager):
        self.pm = project_manager
        self.columns = ["todo", "in_progress", "review", "done"]
    
    def board(self, project_id):
        project = self.pm.get_project(project_id)
        if not project:
            return "Project not found"
        
        board = {}
        for col in self.columns:
            board[col] = [t.to_dict() for t in project.tasks if t.status == col]
        
        return board
    
    def move_task(self, project_id, task_id, new_status):
        return self.pm.update_task(project_id, task_id, status=new_status)
    
    def add_comment(self, project_id, task_id, comment):
        project = self.pm.get_project(project_id)
        if not project:
            return "Project not found"
        
        task = project.get_task(task_id)
        if not task:
            return "Task not found"
        
        task.comments.append({
            "text": comment,
            "created_at": datetime.now().isoformat()
        })
        self.pm._save()
        
        return "Comment added"
    
    def add_subtask(self, project_id, task_id, title):
        project = self.pm.get_project(project_id)
        if not project:
            return "Project not found"
        
        task = project.get_task(task_id)
        if not task:
            return "Task not found"
        
        subtask = {
            "id": str(uuid4())[:8],
            "title": title,
            "done": False
        }
        task.subtasks.append(subtask)
        self.pm._save()
        
        return "Subtask added"
    
    def complete_subtask(self, project_id, task_id, subtask_id):
        project = self.pm.get_project(project_id)
        if not project:
            return "Project not found"
        
        task = project.get_task(task_id)
        if not task:
            return "Task not found"
        
        for st in task.subtasks:
            if st["id"] == subtask_id:
                st["done"] = True
                break
        
        self.pm._save()
        return "Subtask completed"