import sys
import threading

class ChatInterface:
    def __init__(self, agent):
        self.agent = agent

    def start(self):
        print("\n=== Neural Agent ===")
        print("Commands: learn <info>, do <task>, think <query>, recall <query>,")
        print("         read <file>, list, search <query>, fetch <url>,")
        print("         setdir <dir>, KILL, quit")
        print("====================\n")
        
        while self.agent.can_run():
            try:
                user_input = input("You> ").strip()
                if not user_input:
                    continue
                
                self.process_input(user_input)
            except KeyboardInterrupt:
                print("\n[Interrupted]")
                self.agent.shutdown()
                break
            except EOFError:
                break
        
        print("Session ended.")

    def process_input(self, user_input):
        if user_input.upper() == "QUIT":
            self.agent.shutdown()
            return
        
        if user_input.upper() == "KILL":
            self.agent.kill_switch.trigger()
            print("Kill switch engaged. Goodnight.")
            return
        
        if user_input.startswith("learn "):
            info = user_input[6:].strip()
            self.agent.memory.add(info, "learned")
            print(f"Learned: {info}")
            return
        
        if user_input.startswith("do "):
            task = user_input[3:].strip()
            task_id = self.agent.tasks.execute(task)
            print(f"Task started: {task_id}")
            return
        
        if user_input.startswith("think "):
            query = user_input[6:].strip()
            response = self.agent.core.think(query)
            print(f"Agent> {response}")
            return
        
        if user_input.startswith("recall "):
            query = user_input[7:].strip()
            memories = self.agent.memory.recall(query)
            if memories:
                print("Memories:")
                for mem, score in memories:
                    print(f"  - {mem} ({score:.2f})")
            else:
                print("No memories found.")
            return
        
        if user_input.startswith("read ") or user_input.startswith("import "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                print(self.agent.files.read(parts[1].strip()))
            else:
                print("Usage: read ")
            return
        
        if user_input.startswith("list") or user_input == "ls":
            print(self.agent.files.list())
            return
        
        if user_input.startswith("setdir "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                print(self.agent.files.set_workdir(parts[1].strip()))
            else:
                print("Usage: setdir <directory>")
            return
        
        if user_input.startswith("search "):
            query = user_input[7:].strip()
            results = self.agent.web.search(query, limit=5)
            print(f"Search results for '{query}':")
            for r in results:
                print(f"- {r['title']}: {r['url']}")
            return
        
        if user_input.startswith("fetch "):
            parts = user_input.split(" ", 1)
            if len(parts) > 1:
                url = parts[1].strip()
                result = self.agent.web.summarize_page(url)
                print(result)
            else:
                print("Usage: fetch <url>")
            return
        
        response = self.agent.core.query(user_input)
        print(f"Agent> {response}")