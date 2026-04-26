import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AdvancedScraper:
    def __init__(self, agent):
        self.agent = agent
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; NeuralAgent/1.0)"
        })
        self.visited = set()
        self.lock = threading.Lock()
    
    def scrape(self, url, selectors=None, delay=1):
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            time.sleep(delay)
            
            if selectors:
                return self._extract_with_selectors(soup, selectors)
            
            return {
                "title": soup.title.string if soup.title else None,
                "headings": [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3'])],
                "links": [urljoin(url, a.get("href")) for a in soup.find_all("a", href=True)],
                "images": [img.get("src") for img in soup.find_all("img", src=True)],
                "text": soup.get_text(separator=" ", strip=True)[:5000],
                "meta": self._extract_meta(soup),
                "status_code": response.status_code
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_with_selectors(self, soup, selectors):
        result = {}
        for name, selector in selectors.items():
            elements = soup.select(selector)
            result[name] = [el.text.strip() for el in elements if el.text.strip()]
        return result
    
    def _extract_meta(self, soup):
        meta = {}
        for tag in soup.find_all("meta"):
            name = tag.get("name") or tag.get("property")
            content = tag.get("content")
            if name and content:
                meta[name] = content
        return meta
    
    def scrape_all_links(self, url, max_depth=2, delay=1):
        results = {}
        self._scrape_recursive(url, results, depth=0, max_depth=max_depth, delay=delay)
        return results
    
    def _scrape_recursive(self, url, results, depth, max_depth, delay):
        if depth >= max_depth or url in self.visited:
            return
        
        with self.lock:
            if url in self.visited:
                return
            self.visited.add(url)
        
        try:
            page_data = self.scrape(url, delay=delay)
            results[url] = page_data
            
            if "links" in page_data:
                for link in page_data["links"][:20]:
                    if link.startswith("http"):
                        time.sleep(delay)
                        self._scrape_recursive(link, results, depth + 1, max_depth, delay)
        except Exception as e:
            pass
    
    def scrape_parallel(self, urls, max_workers=5, delay=0.5):
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.scrape, url, delay=delay): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                try:
                    results[url] = future.result()
                except Exception as e:
                    results[url] = {"error": str(e)}
        
        return results
    
    def scrape_dynamic(self, url, wait_for_selector=None, timeout=30):
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            driver = webdriver.Chrome()
            driver.get(url)
            
            if wait_for_selector:
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_selector))
                )
            
            page_source = driver.page_source
            driver.quit()
            
            soup = BeautifulSoup(page_source, "html.parser")
            return {
                "title": soup.title.string if soup.title else None,
                "text": soup.get_text(separator=" ", strip=True)[:5000],
                "links": [a.get("href") for a in soup.find_all("a", href=True)]
            }
        except ImportError:
            return {"error": "Selenium not installed"}
        except Exception as e:
            return {"error": str(e)}
    
    def scrape_api(self, url, method="GET", headers=None, params=None, json_data=None):
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=params,
                json=json_data
            )
            
            content_type = response.headers.get("Content-Type", "")
            
            if "application/json" in content_type:
                return response.json()
            else:
                return {"text": response.text[:5000], "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    def parse_html_table(self, url, table_index=0):
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            
            tables = soup.find_all("table")
            if table_index >= len(tables):
                return {"error": f"Table index {table_index} not found"}
            
            table = tables[table_index]
            headers = [th.text.strip() for th in table.find_all("th")]
            rows = []
            
            for tr in table.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if cells:
                    rows.append([cell.text.strip() for cell in cells])
            
            return {"headers": headers, "rows": rows}
        except Exception as e:
            return {"error": str(e)}
    
    def extract_jsonLd(self, url):
        try:
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.text, "html.parser")
            
            scripts = soup.find_all("script", type="application/ld+json")
            results = []
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    results.append(data)
                except:
                    pass
            
            return results
        except Exception as e:
            return {"error": str(e)}
    
    def extract_structured_data(self, url):
        scraped = self.scrape(url)
        if "error" in scraped:
            return scraped
        
        structured = {
            "urls": [],
            "emails": [],
            "phones": [],
            "social_media": [],
            "prices": [],
            "dates": []
        }
        
        all_text = scraped.get("text", "")
        
        all_links = scraped.get("links", [])
        structured["urls"] = [l for l in all_links if l.startswith("http")]
        
        email_pattern = r'[\w.-]+@[\w.-]+\.\w+'
        structured["emails"] = re.findall(email_pattern, all_text)
        
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        structured["phones"] = re.findall(phone_pattern, all_text)
        
        social_patterns = {
            "twitter": r'twitter\.com/\w+',
            "facebook": r'facebook\.com/\w+',
            "instagram": r'instagram\.com/\w+',
            "linkedin": r'linkedin\.com/in/\w+',
            "github": r'github\.com/\w+'
        }
        
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, all_text)
            structured["social_media"].extend([(platform, m) for m in matches])
        
        price_pattern = r'\$\d+(?:,\d{3})*(?:\.\d{2})?'
        structured["prices"] = re.findall(price_pattern, all_text)
        
        date_pattern = r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}'
        structured["dates"] = re.findall(date_pattern, all_text)
        
        return structured


class DataPipeline:
    def __init__(self, agent):
        self.agent = agent
        self.transformers = []
        self.data = None
    
    def load_json(self, filepath):
        with open(filepath, "r") as f:
            self.data = json.load(f)
        return self
    
    def load_csv(self, filepath):
        import csv
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            self.data = list(reader)
        return self
    
    def load_text(self, filepath):
        with open(filepath, "r") as f:
            self.data = f.readlines()
        return self
    
    def filter(self, condition):
        if isinstance(self.data, list):
            self.data = [item for item in self.data if condition(item)]
        return self
    
    def map(self, transform_fn):
        if isinstance(self.data, list):
            self.data = [transform_fn(item) for item in self.data]
        else:
            self.data = transform_fn(self.data)
        return self
    
    def group_by(self, key):
        grouped = {}
        for item in self.data:
            k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            if k not in grouped:
                grouped[k] = []
            grouped[k].append(item)
        return grouped
    
    def aggregate(self, key, agg_fn):
        if isinstance(self.data, list):
            values = [item.get(key) for item in self.data if isinstance(item, dict) and key in item]
            return agg_fn(values)
        return None
    
    def sort_by(self, key, reverse=False):
        if isinstance(self.data, list):
            self.data = sorted(self.data, key=lambda x: x.get(key) if isinstance(x, dict) else getattr(x, key, None), reverse=reverse)
        return self
    
    def join(self, other, key):
        other_dict = {item.get(key) if isinstance(item, dict) else getattr(item, key, None): item for item in other}
        joined = []
        for item in self.data:
            k = item.get(key) if isinstance(item, dict) else getattr(item, key, None)
            if k in other_dict:
                joined.append({**item, **other_dict[k]})
        self.data = joined
        return self
    
    def deduplicate(self, keys=None):
        if keys is None:
            if isinstance(self.data, list):
                self.data = [dict(t) for t in set([tuple(sorted(d.items())) for d in self.data])]
        else:
            seen = set()
            result = []
            for item in self.data:
                key_tuple = tuple(item.get(k) for k in keys)
                if key_tuple not in seen:
                    seen.add(key_tuple)
                    result.append(item)
            self.data = result
        return self
    
    def pivot(self, index_key, columns_key, values_key):
        pivot_table = {}
        for item in self.data:
            index_val = item.get(index_key)
            col_val = item.get(columns_key)
            val = item.get(values_key)
            
            if index_val not in pivot_table:
                pivot_table[index_val] = {}
            pivot_table[index_val][col_val] = val
        
        return pivot_table
    
    def fillna(self, value):
        if isinstance(self.data, list):
            for item in self.data:
                if isinstance(item, dict):
                    for key, val in item.items():
                        if val is None:
                            item[key] = value
        return self
    
    def select_columns(self, columns):
        if isinstance(self.data, list):
            self.data = [{k: v for k, v in item.items() if k in columns} for item in self.data]
        return self
    
    def save_json(self, filepath):
        with open(filepath, "w") as f:
            json.dump(self.data, f, indent=2, default=str)
        return self
    
    def save_csv(self, filepath):
        if not self.data:
            return self
        
        import csv
        with open(filepath, "w", newline="") as f:
            if isinstance(self.data[0], dict):
                writer = csv.DictWriter(f, fieldnames=self.data[0].keys())
                writer.writeheader()
                writer.writerows(self.data)
            else:
                f.write("\n".join(str(d) for d in self.data))
        return self
    
    def get(self):
        return self.data


class APIGenerator:
    def __init__(self, agent):
        self.agent = agent
        self.routes = []
        self.middleware = []
    
    def add_route(self, method, path, handler, middleware=None):
        self.routes.append({
            "method": method.upper(),
            "path": path,
            "handler": handler,
            "middleware": middleware or []
        })
    
    def add_middleware(self, middleware):
        self.middleware.append(middleware)
    
    def generate_flask_app(self):
        template = '''from flask import Flask, request, jsonify

app = Flask(__name__)

'''
        
        for route in self.routes:
            handler_code = self._generate_handler(route)
            template += f'''
@app.route("{route['path']}", methods=["{route['method']}"])
{handler_code}
'''
        
        template += '''
if __name__ == "__main__":
    app.run(debug=True, port=5000)
'''
        
        return template
    
    def generate_express_app(self):
        template = '''const express = require('express');
const app = express();
app.use(express.json());

'''
        
        for route in self.routes:
            method = route['method'].lower()
            path = route['path']
            template += f'''
app.{method}("{path}", (req, res) => {{
    res.json({{ status: "ok" }});
}});
'''
        
        template += '''
app.listen(3000, () => {
    console.log("Server running on port 3000");
});
'''
        
        return template
    
    def generate_fastapi_app(self):
        template = '''from fastapi import FastAPI

app = FastAPI()

'''
        
        for route in self.routes:
            method = route['method'].lower()
            path = route['path']
            
            if method == "get":
                template += f'''
@app.get("{path}")
async def handler():
    return {{"status": "ok"}}
'''
            elif method == "post":
                template += f'''
@app.post("{path}")
async def handler(data: dict = None):
    return {{"status": "ok", "data": data}}
'''
            else:
                template += f'''
@app.{method}("{path}")
async def handler():
    return {{"status": "ok"}}
'''
        
        template += '''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        
        return template
    
    def generate_django_views(self):
        template = '''from django.http import JsonResponse

'''
        
        for i, route in enumerate(self.routes):
            method = route['method'].lower()
            path = route['path']
            func_name = f"view_{i}"
            
            template += f'''
def {func_name}(request):
    return JsonResponse({{"status": "ok"}})
'''
        
        template += '''
# Add to urls.py:
# path('endpoint/', views.view_0),
'''
        
        return template
    
    def _generate_handler(self, route):
        method = route['method'].lower()
        
        if method == "get":
            return '''def handler():
    return jsonify({"status": "ok", "params": request.args.to_dict()})
'''
        elif method == "post":
            return '''def handler():
    return jsonify({"status": "ok", "data": request.get_json()})
'''
        else:
            return '''def handler():
    return jsonify({"status": "ok"})
'''


class ConfigGenerator:
    def __init__(self):
        pass
    
    def generate_docker_compose(self, services):
        compose = {
            "version": "3.8",
            "services": {}
        }
        
        for service in services:
            service_name = service.get("name", "service")
            compose["services"][service_name] = {
                "image": service.get("image", f"{service_name}:latest"),
                "ports": service.get("ports", []),
                "environment": service.get("environment", []),
                "volumes": service.get("volumes", []),
                "depends_on": service.get("depends_on", [])
            }
        
        return json.dumps(compose, indent=2)
    
    def generate_kubernetes_deployment(self, name, image, replicas=1, port=80):
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": name},
            "spec": {
                "replicas": replicas,
                "selector": {"matchLabels": {"app": name}},
                "template": {
                    "metadata": {"labels": {"app": name}},
                    "spec": {
                        "containers": [{
                            "name": name,
                            "image": image,
                            "ports": [{"containerPort": port}]
                        }]
                    }
                }
            }
        }
        return json.dumps(deployment, indent=2)
    
    def generate_nginx_config(self, server_name, upstream_port=8000):
        return f'''
server {{
    listen 80;
    server_name {server_name};

    location / {{
        proxy_pass http://localhost:{upstream_port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }}

    location /static/ {{
        alias /app/static/;
        expires 30d;
    }}

    location /media/ {{
        alias /app/media/;
        expires 7d;
    }}
}}
'''
    
    def generate_env_file(self, variables):
        lines = []
        for key, value in variables.items():
            if isinstance(value, list):
                value = ",".join(str(v) for v in value)
            lines.append(f"{key}={value}")
        return "\n".join(lines)
    
    def generate_gitignore(self, project_type="python"):
        templates = {
            "python": '''
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/
.env
',
            "node": '''
node_modules/
.env
dist/
build/
*.log
.DS_Store
coverage/
.nyc_output/
.cache/
',
            "go": '''
*.exe
*.exe~
*.test
*.out
vendor/
.env
bin/
',
            "rust": '''
target/
Cargo.lock
.env
*.rs.bk
'
        }
        
        return templates.get(project_type, templates["python"])
    
    def generate_github_workflow(self, name, on_push_branches=None, jobs=None):
        workflow = {
            "name": name,
            "on": {
                "push": {"branches": on_push_branches or ["main"]},
                "pull_request": {"branches": on_push_branches or ["main"]}
            },
            "jobs": jobs or {}
        }
        
        return json.dumps(workflow, indent=2)
    
    def generate_makefile(self, targets):
        lines = []
        
        for target_name, target_data in targets.items():
            deps = target_data.get("deps", [])
            commands = target_data.get("commands", [])
            
            deps_str = " ".join(deps) if deps else ""
            lines.append(f"{target_name}: {deps_str}")
            
            for cmd in commands:
                lines.append(f"\t{cmd}")
            
            lines.append("")
        
        return "\n".join(lines)