# Neural Agent - Complete Documentation

## Overview

Neural Agent is an advanced AI agent system with persistent memory, autonomous thinking, task execution, web access, and a kill switch for safety. It's designed as a personal AI assistant that can learn, remember, and perform tasks.

## Installation

### Requirements
- Python 3.8+
- Linux environment (designed for Linux)

### Quick Install

```bash
git clone https://github.com/robeast430-create/Testing-grounds.
cd Testing-grounds.
pip install -r requirements.txt
pip install -e .
```

### Using Docker

```bash
docker build -t neural-agent .
docker run -p 8080:8080 neural-agent
```

## Usage

### Command Line

```bash
# Start with login
neural-agent

# Skip authentication
neural-agent --no-auth

# Start with web dashboard
neural-agent --web

# Start on custom port
neural-agent --port 9000

# User management
neural-agent user add <username> <password>
neural-agent user list
neural-agent user delete <username>
```

### Web Dashboard

Access at `http://localhost:8080` when running with `--web` flag.

## Commands

### Core Commands

| Command | Description |
|---------|-------------|
| `learn <info>` | Store information in memory |
| `think <query>` | Think about something |
| `recall <query>` | Search memories |
| `do <task>` | Execute a task |
| `quit` | Exit the agent |
| `KILL` | Activate kill switch |

### File Operations

| Command | Description |
|---------|-------------|
| `read ` | Read a file |
| `write ` | Write to a file |
| `list` | List directory |
| `setdir <dir>` | Change directory |
| `import ` | Import file content |

### Web Commands

| Command | Description |
|---------|-------------|
| `search <query>` | Web search |
| `fetch <url>` | Fetch webpage content |
| `crawl <url>` | Crawl website |

### System Commands

| Command | Description |
|---------|-------------|
| `sysinfo` | System information |
| `stats` | Agent statistics |
| `top` | Top processes |
| `disk` | Disk usage |
| `network` | Network status |
| `battery` | Battery status |
| `hostname` | System hostname |
| `ip` | IP address |

### Git Commands

| Command | Description |
|---------|-------------|
| `git status` | Show working tree status |
| `git log` | Show commit logs |
| `git diff` | Show changes |
| `git add <files>` | Stage changes |
| `git commit <msg>` | Commit changes |
| `git push` | Push to remote |
| `git pull` | Pull from remote |
| `git branch` | List branches |
| `git checkout <branch>` | Switch branches |

### Build Commands

| Command | Description |
|---------|-------------|
| `build` | Build project |
| `build clean` | Clean build artifacts |
| `project info` | Project information |

### Docker Commands

| Command | Description |
|---------|-------------|
| `docker ps` | List containers |
| `docker images` | List images |
| `docker start <name>` | Start container |
| `docker stop <name>` | Stop container |

### Network Commands

| Command | Description |
|---------|-------------|
| `ping <host>` | Ping a host |
| `nslookup <host>` | DNS lookup |
| `dig <domain>` | DNS query |
| `scan <host>` | Port scan |
| `ssl <host>` | SSL certificate check |
| `ipinfo` | IP information |

### Security Commands

| Command | Description |
|---------|-------------|
| `hash <algo> <text>` | Hash text |
| `encode base64 <text>` | Base64 encode |
| `decode base64 <text>` | Base64 decode |
| `passgen` | Generate password |

### Code Commands

| Command | Description |
|---------|-------------|
| `analyze ` | Analyze code file |
| `issues ` | Find code issues |
| `lint ` | Lint code file |
| `gen <template>` | Generate from template |
| `gentest ` | Generate tests |

### Database Commands

| Command | Description |
|---------|-------------|
| `db stats` | Database statistics |
| `db search <query>` | Search database |

### Project Commands

| Command | Description |
|---------|-------------|
| `projects` | List projects |
| `project create <name>` | Create project |
| `project tasks <id>` | List project tasks |
| `project task add <id> <title>` | Add task |
| `project stats <id>` | Project statistics |

### Monitoring Commands

| Command | Description |
|---------|-------------|
| `alerts` | List alerts |
| `alert add <name> <cond> <val>` | Add alert |
| `uptime check <url>` | Check uptime |
| `uptime status` | Uptime status |
| `health` | Health check |

### Other Commands

| Command | Description |
|---------|-------------|
| `plugins` | List plugins |
| `notifications` | Show notifications |
| `prompts` | List prompt templates |
| `watch <dir>` | Watch directory |
| `export` | Export all data |
| `import <file>` | Import data |
| `backup` | Create backup |
| `cache` | Cache information |
| `history` | Command history |

## API Endpoints

### GET Endpoints

- `/status` - Agent status
- `/stats` - Statistics
- `/sysinfo` - System information
- `/memory` - Memory contents
- `/tasks` - Task list
- `/schedule` - Scheduled tasks
- `/config` - Configuration

### POST Endpoints

- `/learn` - Learn information
- `/do` - Execute task
- `/recall` - Search memory
- `/fetch` - Fetch URL
- `/search` - Web search
- `/run` - Run command
- `/chat` - Chat message
- `/kill` - Kill agent

## Architecture

### Core Components

```
neural_agent/
├── core/           # Neural network core
├── memory/         # Memory bank
├── tasks/          # Task execution
├── interface/      # CLI interface
├── web/            # Web crawler
├── files/          # File management
├── utils/          # Utilities
├── auth/           # Authentication
├── plugins/       # Plugin system
├── database/       # Database layer
├── notifications/  # Notifications
├── conversation/   # Conversation management
├── tools/          # Various tools
├── prompts/        # Prompt templates
├── bluetooth/      # Bluetooth control
├── voice/          # Voice control
├── coding/         # Code features
├── ml/             # ML/AI models
├── scraping/       # Web scraping
├── templates/      # Code templates
└── cloud/          # Cloud integrations
```

### Data Storage

- `auth_data/` - User data, sessions, history
- `memory_db/` - Memory storage (ChromaDB)
- `config.json` - Configuration

## Configuration

Edit `config.json` to customize:

```json
{
  "agent": {
    "name": "NeuralAgent",
    "max_memory": 10000
  },
  "timeouts": {
    "think": 60,
    "fetch": 30
  },
  "web": {
    "user_agent": "Mozilla/5.0",
    "max_depth": 3
  },
  "logging": {
    "level": "INFO",
    "file": "agent.log"
  }
}
```

## Plugins

Available plugins:
- `math` - Mathematical operations
- `date` - Date/time utilities
- `weather` - Weather information
- `translate` - Language translation
- `code` - Code execution
- `reminder` - Set reminders
- `calculator` - Basic calculator
- `url_shortener` - URL shortening
- `qrcode` - QR code generation
- `screenshot` - Take screenshots

## Prompt Templates

Available templates:
- `greeting` - Greeting message
- `summary` - Content summarization
- `analyze` - Analysis template
- `explain` - Simple explanation
- `help_request` - Help request
- `research` - Research template
- `code_review` - Code review
- `task_breakdown` - Task breakdown

## Security

### Authentication

Users are stored with hashed passwords (PBKDF2).

### Kill Switch

Type `KILL` to immediately terminate the agent.

### Rate Limiting

Built-in rate limiting for API endpoints.

## Troubleshooting

### Common Issues

**ImportError: No module named 'xxx'**
```bash
pip install xxx
```

**Permission denied**
```bash
chmod +x install.sh
./install.sh
```

**Connection refused**
- Check if port is in use
- Try a different port: `neural-agent --port 8081`

## License

MIT License - See LICENSE file

## Support

For issues and feature requests, visit the GitHub repository.