import subprocess
import threading
import psutil
import os
import queue

class ProcessManager:
    def __init__(self, agent):
        self.agent = agent
        self.processes = {}
        self.process_id = 0
    
    def run_shell(self, command, background=False):
        self.process_id += 1
        pid = f"proc_{self.process_id}"
        
        if background:
            thread = threading.Thread(target=self._run_process, args=(pid, command), daemon=True)
            thread.start()
            self.processes[pid] = {"command": command, "status": "running", "thread": thread}
            print(f"[ProcessManager] Started {pid}: {command}")
            return pid
        else:
            result = self._run_sync(command)
            return result
    
    def _run_process(self, pid, command):
        try:
            proc = subprocess.Popen(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            self.processes[pid]["proc"] = proc
            stdout, stderr = proc.communicate()
            self.processes[pid]["status"] = "completed"
            self.processes[pid]["returncode"] = proc.returncode
            self.processes[pid]["stdout"] = stdout.decode("utf-8", errors="ignore")
            self.processes[pid]["stderr"] = stderr.decode("utf-8", errors="ignore")
            print(f"[ProcessManager] {pid} completed with code {proc.returncode}")
        except Exception as e:
            self.processes[pid]["status"] = "failed"
            self.processes[pid]["error"] = str(e)
            print(f"[ProcessManager] {pid} failed: {e}")
    
    def _run_sync(self, command):
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=300
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out", "returncode": -1}
        except Exception as e:
            return {"error": str(e), "returncode": -1}
    
    def kill(self, pid):
        if pid in self.processes:
            proc_info = self.processes[pid]
            if "proc" in proc_info and hasattr(proc_info["proc"], "kill"):
                proc_info["proc"].kill()
                proc_info["status"] = "killed"
                print(f"[ProcessManager] Killed {pid}")
                return True
        return False
    
    def list_processes(self):
        results = []
        for pid, info in self.processes.items():
            status = info["status"]
            if "thread" in info and info["thread"].is_alive():
                status = "running"
            results.append({
                "pid": pid,
                "command": info["command"],
                "status": status,
                "returncode": info.get("returncode")
            })
        return results
    
    def get_output(self, pid):
        if pid in self.processes:
            info = self.processes[pid]
            output = {}
            if "stdout" in info:
                output["stdout"] = info["stdout"]
            if "stderr" in info:
                output["stderr"] = info["stderr"]
            return output
        return None
    
    def run_python(self, code):
        try:
            result = {}
            exec_globals = {"result": result}
            exec(code, exec_globals)
            return {"success": True, "result": result.get("result")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_processes(self):
        return [{
            "pid": p.pid,
            "name": p.name(),
            "cpu_percent": p.cpu_percent(),
            "memory_mb": p.memory_info().rss / (1024 * 1024)
        } for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"])][:20]