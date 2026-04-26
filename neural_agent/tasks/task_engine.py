import subprocess
import threading
import asyncio

class TaskEngine:
    def __init__(self, agent):
        self.agent = agent
        self.running_tasks = {}
        self.task_id_counter = 0

    def execute(self, task_description):
        self.task_id_counter += 1
        task_id = f"task_{self.task_id_counter}"
        
        task_thread = threading.Thread(target=self._run_task, args=(task_id, task_description))
        task_thread.daemon = True
        task_thread.start()
        
        self.running_tasks[task_id] = {"description": task_description, "thread": task_thread}
        print(f"[TaskEngine] Started {task_id}: {task_description}")
        return task_id

    def _run_task(self, task_id, description):
        try:
            result = self._analyze_and_execute(description)
            self.running_tasks[task_id]["result"] = result
            print(f"[TaskEngine] {task_id} completed: {result}")
        except Exception as e:
            self.running_tasks[task_id]["error"] = str(e)
            print(f"[TaskEngine] {task_id} failed: {e}")

    def _analyze_and_execute(self, description):
        description_lower = description.lower()
        
        if "fetch" in description_lower or "get" in description_lower or "download" in description_lower:
            return self._handle_fetch(description)
        elif "search" in description_lower or "find" in description_lower:
            return self._handle_search(description)
        elif "save" in description_lower or "write" in description_lower:
            return self._handle_save(description)
        elif "run" in description_lower or "execute" in description_lower:
            return self._handle_run(description)
        elif "read" in description_lower or "file" in description_lower or "import" in description_lower:
            import re
            file_match = re.search(r'(?:read|file|import)\s+(.+)', description, re.IGNORECASE)
            if file_match:
                filepath = file_match.group(1).strip()
                return self.agent.files.read(filepath)
            return self.agent.files.list()
        elif "list" in description_lower or "dir" in description_lower or "ls" in description_lower:
            return self.agent.files.list()
        elif "delete" in description_lower or "remove" in description_lower:
            import re
            file_match = re.search(r'(?:delete|remove)\s+(.+)', description, re.IGNORECASE)
            if file_match:
                filepath = file_match.group(1).strip()
                return self.agent.files.delete(filepath)
            return "Specify file to delete"
        elif "copy" in description_lower or "cp" in description_lower:
            import re
            match = re.search(r'copy\s+(.+?)\s+(?:to|->)\s+(.+)', description, re.IGNORECASE)
            if match:
                src, dst = match.groups()
                return self.agent.files.copy(src.strip(), dst.strip())
            return "Usage: copy <source> to <dest>"
        elif "move" in description_lower or "mv" in description_lower:
            import re
            match = re.search(r'move\s+(.+?)\s+(?:to|->)\s+(.+)', description, re.IGNORECASE)
            if match:
                src, dst = match.groups()
                return self.agent.files.move(src.strip(), dst.strip())
            return "Usage: move <source> to <dest>"
        elif "mkdir" in description_lower or "create dir" in description_lower:
            import re
            dir_match = re.search(r'(?:mkdir|create dir)\s+(.+)', description, re.IGNORECASE)
            if dir_match:
                return self.agent.files.set_workdir(dir_match.group(1).strip())
            return "Usage: mkdir <directory>"
        elif "info" in description_lower or "stat" in description_lower:
            import re
            file_match = re.search(r'(?:info|stat)\s+(.+)', description, re.IGNORECASE)
            if file_match:
                return self.agent.files.info(file_match.group(1).strip())
            return "Specify file for info"
        else:
            return f"Analyzing task '{description}'..."

    def _handle_fetch(self, description):
        import re
        url_match = re.search(r'https?://[^\s]+', description)
        if url_match:
            url = url_match.group()
            return self.agent.web.summarize_page(url)
        return "Fetch task noted. Would need URL to fetch resources."

    def _handle_search(self, description):
        import re
        query_match = re.search(r'search ["\']?(.+?)["\']?$', description)
        if query_match:
            query = query_match.group(1).strip()
            results = self.agent.web.search(query, limit=5)
            return f"Search results for '{query}':\n" + "\n".join(f"- {r['title']}: {r['url']}" for r in results)
        # Try to do a web search
        words = description.lower().replace("search", "").replace("find", "").strip()
        if words:
            results = self.agent.web.search(words, limit=5)
            return f"Search results for '{words}':\n" + "\n".join(f"- {r['title']}: {r['url']}" for r in results)
        return "Search task noted. Would search memory first."

    def _handle_save(self, description):
        return "Save task noted. Would save to memory or file."

    def _handle_run(self, description):
        return "Run task noted. Analyzing command to execute..."

    def _handle_read(self, description):
        return "Read task noted. Would read specified file."

    def list_tasks(self):
        return {tid: {"description": t["description"], "status": "running" if t["thread"].is_alive() else "completed"} 
                for tid, t in self.running_tasks.items()}

    def stop_task(self, task_id):
        if task_id in self.running_tasks:
            del self.running_tasks[task_id]
            print(f"[TaskEngine] Stopped {task_id}")
            return True
        return False