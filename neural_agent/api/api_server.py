import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request("GET")
    
    def do_POST(self):
        self._handle_request("POST")
    
    def _handle_request(self, method):
        if method == "POST":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
            except:
                self._send_error(400, "Invalid JSON")
                return
            
            if self.path == "/learn":
                content = data.get("content", "")
                mem_type = data.get("type", "general")
                self.server.agent.memory.add(content, mem_type)
                self._send_json({"status": "ok", "learned": content[:100]})
            elif self.path == "/do":
                task = data.get("task", "")
                task_id = self.server.agent.tasks.execute(task)
                self._send_json({"status": "ok", "task_id": task_id})
            elif self.path == "/recall":
                query = data.get("query", "")
                memories = self.server.agent.memory.recall(query)
                self._send_json({"results": [{"content": m[0], "score": m[1]} for m in memories]})
            elif self.path == "/fetch":
                url = data.get("url", "")
                if url:
                    result = self.server.agent.web.summarize_page(url)
                    self._send_json({"status": "ok", "result": result})
                else:
                    self._send_error(400, "URL required")
            elif self.path == "/search":
                query = data.get("query", "")
                results = self.server.agent.web.search(query)
                self._send_json({"results": results})
            elif self.path == "/run":
                cmd = data.get("command", "")
                result = self.server.agent.processes.run_shell(cmd)
                self._send_json(result)
            elif self.path == "/kill":
                self.server.agent.kill_switch.trigger()
                self._send_json({"status": "killed"})
            elif self.path == "/chat":
                message = data.get("message", "")
                response = self.server.agent.core.query(message)
                self._send_json({"response": response})
            elif self.path == "/sim/create":
                name = data.get("name", "default")
                dim = data.get("dimension", "3d").lower()
                from neural_agent.simulation import Dimension as SimDim
                dim_map = {"2d": SimDim.DIM_2D, "3d": SimDim.DIM_3D, "4d": SimDim.DIM_4D}
                dimension = dim_map.get(dim, SimDim.DIM_3D)
                sim = self.server.agent.simulation.create_simulation(name, dimension)
                self._send_json({"status": "ok", "name": name, "dimension": dim})
            elif self.path == "/sim/step":
                name = data.get("name", "default")
                sim = self.server.agent.simulation.get_simulation(name)
                if sim:
                    sim.step()
                    self._send_json({"status": "ok"})
                else:
                    self._send_error(404, "Simulation not found")
            elif self.path == "/sim/render":
                name = data.get("name", "default")
                html = self.server.agent.simulation.render(name)
                self._send_json({"status": "ok", "html": len(html), "content": html[:500]})
            elif self.path == "/sim/blender":
                name = data.get("name", "default")
                output = data.get("output", "/tmp/simulation.png")
                result = self.server.agent.simulation.export_blender(name, output)
                self._send_json(result)
            else:
                self._send_error(404, "Not found")
            return
        
        if self.path == "/":
            self.path = "/index.html"
        
        if self.path == "/index.html" or self.path.endswith(".html"):
            try:
                with open(self.path.lstrip("/"), "r") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(content.encode("utf-8"))
            except:
                self._send_error(404, "Not found")
            return
        
        if self.path == "/status":
            self._send_json({"status": "running", "uptime": time.time()})
        elif self.path == "/stats":
            self._send_json(self.server.agent.monitor.get_stats())
        elif self.path == "/sysinfo":
            self._send_json(self.server.agent.monitor.get_system_info())
        elif self.path == "/memory":
            memories = []
            for t in self.server.agent.memory.metadata["memories"][-50:]:
                memories.append(t)
            self._send_json({"count": self.server.agent.memory.count(), "recent": memories})
        elif self.path == "/tasks":
            self._send_json(self.server.agent.tasks.list_tasks())
        elif self.path == "/schedule":
            self._send_json(self.server.agent.scheduler.list())
        elif self.path == "/config":
            self._send_json(json.loads(self.server.agent.config.export()))
        elif self.path == "/sim/list":
            sims = self.server.agent.simulation.list_simulations()
            self._send_json({"simulations": sims})
        elif self.path == "/sim/status":
            sims = {}
            for name in self.server.agent.simulation.list_simulations():
                sim = self.server.agent.simulation.get_simulation(name)
                sims[name] = {"type": type(sim).__name__, "time": getattr(sim, 'time', 0)}
            self._send_json(sims)
        else:
            self._send_error(404, "Not found")
    
    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))
    
    def _send_error(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}).encode("utf-8"))
    
    def log_message(self, format, *args):
        print(f"[API] {args[0]}")

class APIServer:
    def __init__(self, agent, port=8080):
        self.agent = agent
        self.port = port
        self.server = None
        self.running = False
    
    def start(self):
        self.server = HTTPServer(("0.0.0.0", self.port), APIHandler)
        self.server.agent = self.agent
        self.running = True
        
        thread = threading.Thread(target=self._serve, daemon=True)
        thread.start()
        
        print(f"[APIServer] Running on http://localhost:{self.port}")
        return f"http://localhost:{self.port}"
    
    def _serve(self):
        self.server.serve_forever()
    
    def stop(self):
        if self.server:
            self.server.shutdown()
            self.running = False
            print("[APIServer] Stopped")