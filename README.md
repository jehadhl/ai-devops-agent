<div align="center">

# 🐙 OpsKraken

**AI-Powered DevOps Assistant with Model Context Protocol (MCP)**

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-Server-6C63FF?style=for-the-badge)](https://modelcontextprotocol.io/)
[![Docker](https://img.shields.io/badge/Docker-Integrated-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![GitHub API](https://img.shields.io/badge/GitHub-API-181717?style=for-the-badge&logo=github&logoColor=white)](https://docs.github.com/en/rest)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

</div>

---

## Overview

OpsKraken is an AI-driven DevOps automation platform built on **Model Context Protocol (MCP)** to intelligently interact with Docker, GitHub, Kubernetes, and AWS systems.

### ✨ Features

- 🐳 **Docker** - Container lifecycle, images, networks, volumes, logs
- 🐙 **GitHub** - Repos, workflows, PRs, issues, releases
- 🤖 **AI Agents** - Multi-agent architecture for intelligent automation
- 🔌 **MCP Integration** - Dynamic tool registration and provider management
- 🛡️ **Production-Ready** - Error handling, logging, type safety

---

## 🏗️ Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    👤 User Request                          │
│          "Deploy app and monitor performance"              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
          ┌──────────────────────────────────┐
          │  🤖 Supervisor Agent (Orchestrator)
          │  • Parse request                 │
          │  • Plan multi-step workflow      │
          │  • Coordinate specialists       │
          │  • Monitor progress             │
          └─────────┬──────────┬─────────┬───┘
                    │          │         │
        ┌───────────┘          │         └───────────┐
        │                      │                     │
        ▼                      ▼                      ▼
   ┌────────────┐      ┌────────────┐      ┌────────────┐
   │ 🐳 Docker  │      │ 🐙 GitHub  │      │ ☸️ K8s     │
   │ Specialist │      │ Specialist │      │ Specialist │
   └────┬───────┘      └────┬───────┘      └────┬───────┘
        │                   │                    │
        │ ▼                 │ ▼                  │ ▼
        │ • Build image     │ • Create PR       │ • Deploy pods
        │ • Run container   │ • Trigger CI/CD   │ • Scale replicas
        │ • Get logs        │ • Monitor runs    │ • Monitor health
        │
        └─────────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────────────┐
        │  📋 MCP Protocol Bridge       │
        │  (Tool Discovery & Execution) │
        └───────────┬───────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐ ┌────────┐ ┌────────┐
   │ Docker │ │GitHub  │ │  K8s   │
   │ Tools  │ │ Tools  │ │ Tools  │
   └────┬───┘ └────┬───┘ └────┬───┘
        │          │          │
        ▼          ▼          ▼
   ┌────────────────────────────────┐
   │   🧰 Provider System           │
   │   • Connection pooling         │
   │   • Error handling             │
   │   • Retry logic                │
   │   • Rate limiting              │
   └────────┬───────────────────────┘
            │
   ┌────────┼────────┬──────────┐
   │        │        │          │
   ▼        ▼        ▼          ▼
 Docker  GitHub   K8s API   AWS API
 Engine  REST     Server    Endpoints
```

### How Multi-Agent System Works

The OpsKraken system uses a **3-tier intelligence model** with LLM, Planning, and Memory:

```
User Request
     │
     ▼
┌─────────────────────────────────────────────────┐
│  🧠 LLM Layer (Claude/GPT)                      │
│  • Understand natural language                  │
│  • Reason about complex tasks                   │
│  • Generate execution plans                     │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  📋 Planning & Memory Layer                     │
│  • Break task into sub-steps                    │
│  • Store execution context                      │
│  • Track completed tasks                        │
│  • Learn from previous operations               │
└──────────────┬──────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────┐
│  🤖 Supervisor Agent (Orchestrator)             │
│  • Coordinate specialist agents                 │
│  • Manage parallel execution                    │
│  • Handle failures and retries                  │
│  • Update memory with results                   │
└──────────────┬──────────────────────────────────┘
               │
     ┌─────────┼─────────┐
     │         │         │
     ▼         ▼         ▼
 Docker    GitHub      K8s
Specialist Specialist Specialist
  Agents    Agents     Agents
```

### Key Components

**1. LLM Integration** 🧠
- Claude AI for understanding user intent
- Natural language task decomposition
- Intelligent decision making
- Context-aware responses

**2. Planning Engine** 📋
- Multi-step workflow generation
- Dependency resolution
- Parallel execution optimization
- Failure recovery strategies

**3. Memory System** 💾
- Short-term: Current execution context
- Long-term: Operation history & learnings
- Session state persistence
- Cross-agent communication log

**4. Supervisor Agent** 🤖
- Routes tasks to specialist agents
- Executes tasks in parallel
- Aggregates results
- Updates memory with outcomes

**5. Specialist Agents** ⚙️
- **Docker**: Container lifecycle operations
- **GitHub**: Repository & CI/CD management
- **K8s**: Orchestration & deployment

## Agent Responsibilities

🤖 Supervisor Agent — LLM-guided planning • Task routing • Result aggregation

🐳 Docker Specialist — Build & push images • Deploy containers • Scale & monitor

🐙 GitHub Specialist — Manage repos • Trigger workflows • Track PRs & issues

☸️ K8s Specialist — Deploy pods • Scale replicas • Monitor cluster health

## Layered Architecture

🧠 LLM Layer — Understand user intent • Reason about tasks • Generate plans

📋 Planning & Memory — Decompose tasks • Store context • Track history

📌 MCP Tools — AI-accessible capabilities • Tool discovery & registration

⚙️ Manager — Domain logic • Response transformation • Error handling

🔌 Client Provider — Low-level API operations • Auth & connectivity

🧰 AppContext — Provider lifecycle • State management • Resource cleanup



## 📁 Project Structure

```
ai-devops-agent/
├── apps/
│   ├── agent/                    # AI agent layer (future)
│   │
│   └── mcp_server/
│       ├── src/ai_devops_mcp/
│       │   ├── core/
│       │   │   ├── config.py
│       │   │   ├── logging.py
│       │   │   └── exceptions.py
│       │   │
│       │   ├── server/
│       │   │   ├── mcp_server.py      # MCP server
│       │   │   ├── context.py         # Provider lifecycle
│       │   │   └── main.py            # Entry point
│       │   │
│       │   └── tools/
│       │       ├── docker/
│       │       │   ├── client.py
│       │       │   ├── containers.py
│       │       │   ├── images.py
│       │       │   ├── registry.py
│       │       │   └── ...
│       │       │
│       │       └── github/
│       │           ├── client.py
│       │           ├── repositories.py
│       │           ├── workflows.py
│       │           ├── registry.py
│       │           └── ...
│       │
│       ├── tests/
│       │   ├── unit/
│       │   └── integration/
│       │
│       ├── .env.example
│       ├── pyproject.toml
│       └── README.md
│
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker Engine/Desktop running
- GitHub token (optional)

### Installation

```bash
# Clone repository
git clone https://github.com/jehadhl/ai-devops-agent.git
cd ai-devops-agent/apps/mcp_server

# Install dependencies
uv sync --with dev

# Configure environment
cp .env.example .env
# Edit .env with your GITHUB_TOKEN and org
```

### Run Server

```bash
uv run dev
```

Expected output:
```
INFO: Starting AI DevOps MCP
INFO: Docker client connected successfully
INFO: GitHub client initialized
INFO: MCP server ready with 50+ tools
```

---

## 📋 Available Tools

### Docker
- `docker_list_containers`, `docker_get_container_info`, `docker_run_container`
- `docker_stop_container`, `docker_remove_container`
- `docker_list_images`, `docker_pull_image`, `docker_build_image`
- `docker_get_container_logs`, `docker_get_container_stats`

### GitHub
- `github_get_repository`, `github_list_repositories`
- `github_list_workflows`, `github_get_workflow_runs`, `github_trigger_workflow`
- `github_list_pull_requests`, `github_list_issues`, `github_list_releases`

---

### 👨‍💻 Author

**Jehad Hlewi**  
Software Engineer | DevOps Enthusiast | AI/ML Explorer

- 🔗 **GitHub:** [@jehadhl](https://github.com/jehadhl)
- 💼 **LinkedIn:** [Jehad Hlewi](https://linkedin.com/in/je7d)


