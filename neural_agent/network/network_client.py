import requests
import json
import urllib.parse
from datetime import datetime

class HTTPClient:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.last_response = None
    
    def request(self, method, endpoint, **kwargs):
        url = f"{self.base_url}{endpoint}" if self.base_url else endpoint
        
        response = self.session.request(method, url, **kwargs)
        self.last_response = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text,
            "json": None
        }
        
        try:
            self.last_response["json"] = response.json()
        except:
            pass
        
        return self.last_response
    
    def get(self, endpoint, params=None, **kwargs):
        return self.request("GET", endpoint, params=params, **kwargs)
    
    def post(self, endpoint, data=None, json=None, **kwargs):
        return self.request("POST", endpoint, data=data, json=json, **kwargs)
    
    def put(self, endpoint, data=None, json=None, **kwargs):
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)
    
    def patch(self, endpoint, data=None, json=None, **kwargs):
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)
    
    def delete(self, endpoint, **kwargs):
        return self.request("DELETE", endpoint, **kwargs)
    
    def set_header(self, key, value):
        self.session.headers[key] = value
    
    def set_auth(self, token):
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def format_response(self, response, format="simple"):
        if format == "simple":
            return f"Status: {response['status_code']}\n{response['body'][:500]}"
        elif format == "json":
            return json.dumps(response.get("json", response["body"]), indent=2)
        elif format == "headers":
            return json.dumps(response["headers"], indent=2)
        else:
            return response["body"]


class RESTClient(HTTPClient):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.resources = {}
    
    def register_resource(self, name, endpoints):
        self.resources[name] = endpoints
    
    def resource(self, name):
        if name not in self.resources:
            return None
        
        return RESTResource(self, self.resources[name])
    
    def get_resource(self, name, path, params=None):
        if name not in self.resources:
            return {"error": f"Unknown resource: {name}"}
        
        endpoints = self.resources[name]
        if path not in endpoints:
            return {"error": f"Unknown path: {path}"}
        
        url = endpoints[path]
        return self.get(url, params=params)
    
    def create_resource(self, name, data):
        if name not in self.resources:
            return {"error": f"Unknown resource: {name}"}
        
        endpoints = self.resources[name]
        if "create" not in endpoints:
            return {"error": "Create endpoint not defined"}
        
        return self.post(endpoints["create"], json=data)
    
    def update_resource(self, name, id, data):
        if name not in self.resources:
            return {"error": f"Unknown resource: {name}"}
        
        endpoints = self.resources[name]
        if "update" not in endpoints:
            return {"error": "Update endpoint not defined"}
        
        url = endpoints["update"].replace("{id}", str(id))
        return self.put(url, json=data)
    
    def delete_resource(self, name, id):
        if name not in self.resources:
            return {"error": f"Unknown resource: {name}"}
        
        endpoints = self.resources[name]
        if "delete" not in endpoints:
            return {"error": "Delete endpoint not defined"}
        
        url = endpoints["delete"].replace("{id}", str(id))
        return self.delete(url)


class RESTResource:
    def __init__(self, client, endpoints):
        self.client = client
        self.endpoints = endpoints
    
    def list(self, params=None):
        return self.client.get(self.endpoints.get("list", "/"), params=params)
    
    def get(self, id):
        url = self.endpoints.get("get", "/{id}").replace("{id}", str(id))
        return self.client.get(url)
    
    def create(self, data):
        return self.client.post(self.endpoints.get("create", "/"), json=data)
    
    def update(self, id, data):
        url = self.endpoints.get("update", "/{id}").replace("{id}", str(id))
        return self.client.put(url, json=data)
    
    def delete(self, id):
        url = self.endpoints.get("delete", "/{id}").replace("{id}", str(id))
        return self.client.delete(url)


class APITester:
    def __init__(self):
        self.tests = []
        self.results = []
    
    def add_test(self, name, method, url, expected_status=200, data=None):
        self.tests.append({
            "name": name,
            "method": method,
            "url": url,
            "expected_status": expected_status,
            "data": data
        })
    
    def run_tests(self):
        results = []
        for test in self.tests:
            try:
                response = requests.request(
                    test["method"],
                    test["url"],
                    json=test.get("data")
                )
                
                passed = response.status_code == test["expected_status"]
                results.append({
                    "name": test["name"],
                    "passed": passed,
                    "status": response.status_code,
                    "expected": test["expected_status"]
                })
            except Exception as e:
                results.append({
                    "name": test["name"],
                    "passed": False,
                    "error": str(e)
                })
        
        self.results = results
        return results
    
    def summary(self):
        if not self.results:
            return "No tests run"
        
        passed = sum(1 for r in self.results if r.get("passed"))
        total = len(self.results)
        
        return f"Tests: {passed}/{total} passed\n" + "\n".join([
            f"  {'✓' if r.get('passed') else '✗'} {r['name']}"
            for r in self.results
        ])


class WebSocketClient:
    def __init__(self, url):
        self.url = url
        self.ws = None
        self.messages = []
    
    def connect(self):
        try:
            import websocket
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            return "WebSocket connection initiated"
        except ImportError:
            return "websocket-client not installed"
    
    def send(self, message):
        if self.ws:
            self.ws.send(message)
            return f"Sent: {message}"
        return "Not connected"
    
    def receive(self):
        if self.messages:
            return self.messages.pop(0)
        return None
    
    def _on_message(self, ws, message):
        self.messages.append(message)
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")


class GraphQLClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.session = requests.Session()
    
    def query(self, query, variables=None, operation_name=None):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name
        
        response = self.session.post(self.endpoint, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "errors" in data:
                return {"errors": data["errors"]}
            return data.get("data", {})
        else:
            return {"error": f"HTTP {response.status_code}", "body": response.text}
    
    def mutation(self, mutation, variables=None):
        return self.query(mutation, variables)
    
    def introspect(self):
        query = """
        {
            __schema {
                types {
                    name
                    fields {
                        name
                        type {
                            name
                            kind
                        }
                    }
                }
            }
        }
        """
        return self.query(query)