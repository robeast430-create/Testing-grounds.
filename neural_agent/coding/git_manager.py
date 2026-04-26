import subprocess
import os
import json
from datetime import datetime

class GitManager:
    def __init__(self, agent):
        self.agent = agent
        self.repo_path = "."
    
    def is_git_repo(self):
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def status(self):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if not result.stdout.strip():
                return "Clean working directory"
            
            files = result.stdout.strip().split("\n")
            return f"Changes:\n{result.stdout}"
        except Exception as e:
            return f"Error: {e}"
    
    def diff(self, file=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "diff"]
            if file:
                cmd.append(file)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout or "No changes"
        except Exception as e:
            return f"Error: {e}"
    
    def staged_diff(self):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout or "No staged changes"
        except Exception as e:
            return f"Error: {e}"
    
    def add(self, files=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        if files is None:
            files = ["."]
        
        try:
            result = subprocess.run(
                ["git", "add"] + files,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Added {len(files)} file(s) to staging"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def commit(self, message):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Committed: {message[:50]}"
            else:
                return f"Commit failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def log(self, limit=10):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "log", f"--oneline", f"-n{limit}"],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.stdout or "No commits"
        except Exception as e:
            return f"Error: {e}"
    
    def branch(self, action=None, name=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            if action == "list":
                result = subprocess.run(
                    ["git", "branch", "-a"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout or "No branches"
            
            elif action == "create" and name:
                result = subprocess.run(
                    ["git", "branch", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"Created branch: {name}"
                return f"Error: {result.stderr}"
            
            elif action == "checkout" and name:
                result = subprocess.run(
                    ["git", "checkout", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"Switched to branch: {name}"
                return f"Error: {result.stderr}"
            
            elif action == "delete" and name:
                result = subprocess.run(
                    ["git", "branch", "-d", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"Deleted branch: {name}"
                return f"Error: {result.stderr}"
            
            else:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return f"Current branch: {result.stdout.strip()}"
        except Exception as e:
            return f"Error: {e}"
    
    def push(self, remote="origin", branch=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "push"]
            if remote:
                cmd.append(remote)
            if branch:
                cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Pushed to {remote}"
            else:
                return f"Push failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def pull(self, remote="origin", branch=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "pull"]
            if remote:
                cmd.append(remote)
            if branch:
                cmd.append(branch)
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Pulled from {remote}"
            else:
                return f"Pull failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def clone(self, repo_url, path=None):
        try:
            cmd = ["git", "clone", repo_url]
            if path:
                cmd.append(path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return f"Cloned {repo_url}"
            else:
                return f"Clone failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Clone timed out"
        except Exception as e:
            return f"Error: {e}"
    
    def remote(self, action=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            if action == "list":
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout or "No remotes"
            
            elif action and action.startswith("add "):
                parts = action.split()
                if len(parts) >= 3:
                    name, url = parts[1], parts[2]
                    result = subprocess.run(
                        ["git", "remote", "add", name, url],
                        cwd=self.repo_path,
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return f"Added remote {name}"
                    return f"Error: {result.stderr}"
            
            elif action and action.startswith("remove "):
                name = action.split()[1]
                result = subprocess.run(
                    ["git", "remote", "remove", name],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"Removed remote {name}"
                return f"Error: {result.stderr}"
            
            else:
                result = subprocess.run(
                    ["git", "remote", "-v"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout or "No remotes"
        except Exception as e:
            return f"Error: {e}"
    
    def stash(self, action=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            if action == "push" or action is None:
                result = subprocess.run(
                    ["git", "stash", "push", "-m", "WIP"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return "Stashed changes" if result.returncode == 0 else f"Error: {result.stderr}"
            
            elif action == "pop":
                result = subprocess.run(
                    ["git", "stash", "pop"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return "Popped stash" if result.returncode == 0 else f"Error: {result.stderr}"
            
            elif action == "list":
                result = subprocess.run(
                    ["git", "stash", "list"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout or "No stashes"
            
            else:
                result = subprocess.run(
                    ["git", "stash", "list"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                return result.stdout or "No stashes"
        except Exception as e:
            return f"Error: {e}"
    
    def merge(self, branch):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "merge", branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Merged {branch}"
            else:
                return f"Merge failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def rebase(self, branch):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            result = subprocess.run(
                ["git", "rebase", branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Rebased onto {branch}"
            else:
                return f"Rebase failed: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def tag(self, name, message=None):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "tag", name]
            if message:
                cmd.extend(["-m", message])
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return f"Created tag: {name}"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"
    
    def clean(self, dry_run=False, force=False):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "clean"]
            if dry_run:
                cmd.append("-n")
            if force:
                cmd.append("-fd")
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return result.stdout or "Nothing to clean"
        except Exception as e:
            return f"Error: {e}"
    
    def reset(self, hard=False):
        if not self.is_git_repo():
            return "Not a git repository"
        
        try:
            cmd = ["git", "reset"]
            if hard:
                cmd.append("--hard")
            
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return "Reset complete"
            else:
                return f"Error: {result.stderr}"
        except Exception as e:
            return f"Error: {e}"