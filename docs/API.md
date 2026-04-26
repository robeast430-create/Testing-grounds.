# API Reference

## NeuralAgent Class

### Constructor

```python
agent = NeuralAgent(config_file="config.json", data_dir="./auth_data")
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `memory` | MemoryBank | Persistent memory storage |
| `core` | NeuralCore | Neural network processing |
| `tasks` | TaskEngine | Task execution engine |
| `web` | WebCrawler | Web access capabilities |
| `files` | FileManager | File operations |
| `bluetooth` | BluetoothManager | Bluetooth control |
| `voice` | VoiceManager | Voice/TTS capabilities |
| `git` | GitManager | Git operations |
| `build` | BuildManager | Project building |
| `db` | Database | SQLite database |
| `notifications` | NotificationManager | Notification system |

### Methods

#### `start()`
Start the agent and begin interactive session.

#### `shutdown()`
Gracefully shutdown the agent.

---

## MemoryBank

### Methods

#### `add(content, type="general")`
Add information to memory.

#### `recall(query, top_k=5)`
Search memory for related content.

#### `search(query, limit=10)`
Full-text search in memory.

#### `save()`
Persist memory to disk.

#### `load()`
Load memory from disk.

#### `clear()`
Clear all memories.

---

## WebCrawler

### Methods

#### `fetch(url, timeout=30)`
Fetch webpage content.

#### `parse(html)`
Parse HTML to text.

#### `search(query, limit=10)`
Search the web.

#### `crawl(url, depth=1, max_pages=10)`
Crawl website recursively.

#### `summarize_page(url)`
Get page summary.

---

## FileManager

### Methods

#### `read(filepath)`
Read file contents.

#### `write(filepath, content)`
Write content to file.

#### `list(directory=".")`
List directory contents.

#### `delete(filepath)`
Delete file or directory.

#### `copy(source, dest)`
Copy file or directory.

#### `move(source, dest)`
Move file or directory.

---

## GitManager

### Methods

#### `status()`
Get git status.

#### `add(files)`
Stage files.

#### `commit(message)`
Create commit.

#### `push(remote="origin", branch=None)`
Push to remote.

#### `pull(remote="origin", branch=None)`
Pull from remote.

#### `log(limit=10)`
Get commit log.

#### `branch(action=None, name=None)`
Manage branches.

---

## BuildManager

### Methods

#### `build(target=None)`
Build project.

#### `clean()`
Clean build artifacts.

#### `detect_project_type()`
Detect project type.

#### `get_project_info()`
Get project information.

---

## BluetoothManager

### Methods

#### `scan(duration=10)`
Scan for devices.

#### `pair(mac)`
Pair with device.

#### `connect(mac)`
Connect to device.

#### `disconnect(mac)`
Disconnect device.

#### `status()`
Bluetooth status.

---

## CodeAnalyzer

### Methods

#### `analyze_file(filepath)`
Analyze code file.

#### `find_issues(filepath)`
Find code issues.

---

## CodeGenerator

### Methods

#### `generate(template_name, **kwargs)`
Generate from template.

#### `generate_file(filepath, template_name, **kwargs)`
Generate and save file.

#### `list_templates()`
List available templates.

---

## ProjectManager

### Methods

#### `create_project(name, description="")`
Create new project.

#### `get_project(project_id)`
Get project by ID.

#### `create_task(project_id, title, ...)`
Add task to project.

#### `update_task(project_id, task_id, **kwargs)`
Update task.

#### `list_projects()`
List all projects.

#### `get_stats(project_id)`
Get project statistics.

---

## AlertManager

### Methods

#### `add_alert(name, condition, threshold, message)`
Add alert.

#### `list_alerts()`
List all alerts.

#### `remove_alert(name)`
Remove alert.

---

## HTTPClient

### Methods

#### `get(endpoint, params=None)`
GET request.

#### `post(endpoint, data=None, json=None)`
POST request.

#### `put(endpoint, data=None, json=None)`
PUT request.

#### `delete(endpoint)`
DELETE request.

#### `set_header(key, value)`
Set header.

#### `set_auth(token)`
Set authorization token.

---

## SQLManager

### Methods

#### `connect(db_name)`
Connect to database.

#### `execute(db_name, query, params=None)`
Execute SQL query.

#### `create_table(db_name, table_name, columns)`
Create table.

#### `insert(db_name, table, data)`
Insert row.

#### `select(db_name, table, where=None, limit=100)`
Select rows.

#### `list_tables(db_name)`
List tables.

---

## CacheManager

### Methods

#### `get(key, max_age=3600)`
Get cached value.

#### `set(key, value, ttl=3600)`
Set cached value.

#### `delete(key)`
Delete cached value.

#### `clear()`
Clear all cache.

---

## Example Usage

### Basic Usage

```python
from neural_agent import NeuralAgent

agent = NeuralAgent()
agent.start()
```

### API Server

```python
from neural_agent import NeuralAgent
from neural_agent.api.api_server import APIServer

agent = NeuralAgent()
api = APIServer(agent, port=8080)
api.start()
```

### With Custom Config

```python
agent = NeuralAgent(config_file="my_config.json", data_dir="./my_data")
```

### Accessing Components

```python
agent.memory.add("Python is a programming language")
results = agent.memory.recall("programming")
print(results)

agent.web.search("latest AI news")
agent.git.status()
agent.build.build()
```