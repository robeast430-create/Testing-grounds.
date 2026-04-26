# Neural Agent

An advanced AI agent with persistent memory, autonomous thinking, task execution, and a kill switch.

## Runs On
```
Linux • macOS • Windows • Android • Raspberry Pi • Termux • Any Unix
```

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/robeast430-create/Testing-grounds./main/install.sh | bash
```

## Run

```bash
neural-agent start
# or for terminal UI
linai
```

## Features

- **Memory**: Persistent semantic memory with recall
- **Thinking**: Autonomous reasoning and problem solving
- **Tasks**: Background task execution
- **Simulations**: 2D/3D/4D physics simulations
- **APK Build**: Package as Android app
- **Kill Switch**: Emergency shutdown
- **Web UI**: Dashboard at http://localhost:8080

## Commands

```bash
neural-agent --web          # Start with web dashboard
neural-agent user add admin password  # Create user
neural-agent sim create mysim 3d       # Create 3D simulation
neural-agent apk all                  # Build APK
linai                               # Terminal UI
```