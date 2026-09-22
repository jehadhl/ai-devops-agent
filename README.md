🐙 OpsKraken

<p align="center"><strong>AI DevOps experimentation with MCP, Docker, GitHub, and intelligent agents.</strong></p>
<p align="center">A hands-on engineering project exploring how AI agents can interact with real DevOps systems through the Model Context Protocol.</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/MCP-Server-6C63FF" alt="MCP">
  <img src="https://img.shields.io/badge/Docker-Integrated-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/GitHub-Integrated-181717?logo=github&logoColor=white" alt="GitHub">
  <img src="https://img.shields.io/badge/Package%20Manager-uv-DE5FE9" alt="uv">
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#docker-integration">Docker</a> •
  <a href="#github-integration">GitHub</a> •
  <a href="#setup">Setup</a> •
  <a href="#roadmap">Roadmap</a>
</p>

Overview

OpsKraken is a portfolio and learning project focused on building an AI-driven DevOps assistant with the Model Context Protocol (MCP).

The current implementation provides a modular MCP server with real integrations for Docker and GitHub.

Current capabilities

🐳 Docker integration

🐙 GitHub integration

⚙️ Dynamic MCP registration

🔌 Provider-based architecture

🧩 Manager / API / client separation

♻️ Provider lifecycle management

🔐 Environment-based configuration

🛡️ Structured error handling

[!NOTE]
OpsKraken is an engineering practice project, not a SaaS platform.

Architecture

flowchart LR
    USER["👤 User / AI Agent"]
    CLIENT["🧠 MCP Client"]
    SERVER["⚙️ OpsKraken MCP Server"]
    DOCKER["🐳 Docker"]
    GITHUB["🐙 GitHub"]
    ENGINE["Docker Engine"]
    GHAPI["GitHub REST API"]

    USER --> CLIENT --> SERVER
    SERVER --> DOCKER --> ENGINE
    SERVER --> GITHUB --> GHAPI

Provider design

flowchart LR
    MCP["MCP Tool"]
    REG["Registry"]
    MAN["Manager"]
    API["API Layer"]
    CLIENT["Client Provider"]
    EXT["External System"]

    MCP --> REG --> MAN --> API --> CLIENT --> EXT

Layer

Responsibility

Registry

Exposes provider capabilities through MCP

Manager

Handles domain logic and response shaping

API Layer

Defines provider-specific operations

Client Provider

Handles connectivity, auth, requests, and low-level errors

AppContext

Stores providers and manages their lifecycle

Docker Integration

The Docker integration communicates with the local Docker Engine through the Docker SDK.

flowchart LR
    MCP["MCP Server"]
    REG["Docker Registry"]
    MAN["Docker Managers"]
    SDK["Docker SDK"]
    ENGINE["Docker Engine"]

    MCP --> REG --> MAN --> SDK --> ENGINE

Supported areas

Containers

Images

Logs

Networks

Volumes

The Docker provider is intended for environments where OpsKraken has local access to the Docker Engine.

GitHub Integration

The GitHub provider communicates with the GitHub REST API through a layered client, API, manager, and MCP registry architecture.

flowchart LR
    MCP["MCP Server"]
    REG["GitHub Registry"]
    MAN["GitHub Managers"]
    API["GitHub API"]
    CLIENT["GitHub Client"]
    GH["GitHub REST API"]

    MCP --> REG --> MAN --> API --> CLIENT --> GH

Supported areas

Repository information

Authenticated repositories

Organization repositories

GitHub Actions workflows

Workflow runs

Workflow dispatch

Pull requests

Issues

Releases

Project Structure

ai-devops-agent/
├── apps/
│   ├── agent/
│   └── mcp_server/
│       ├── src/ai_devops_mcp/
│       │   ├── core/
│       │   ├── server/
│       │   └── tools/
│       │       ├── docker/
│       │       └── github/
│       ├── .env.example
│       ├── pyproject.toml
│       └── uv.lock
├── tests/
├── .gitignore
└── README.md

Setup

Requirements

Python 3.12+

uv

Docker Desktop or Docker Engine

GitHub fine-grained personal access token

Clone

git clone https://github.com/jehadhl/ai-devops-agent.git
cd ai-devops-agent/apps/mcp_server

Install

uv sync

Configure

cp .env.example .env

Example:

APP_NAME=OpsKraken MCP
LOG_LEVEL=INFO
DOCKER_RETRY_ATTEMPTS=3
DOCKER_RETRY_DELAY=1.0
GITHUB_TOKEN=
GITHUB_API_URL=https://api.github.com
GITHUB_TIMEOUT=10
FAIL_ON_TOOL_REGISTRATION_ERROR=false

[!IMPORTANT]
Never commit .env, access tokens, private keys, or other secrets.

Run

uv run --env-file .env python -m ai_devops_mcp.main

AI Agent Direction

The next phase connects an AI agent to OpsKraken through an MCP client.

flowchart LR
    USER["👤 User"]
    AGENT["🤖 AI Agent"]
    MCP["MCP Client"]
    SERVER["OpsKraken MCP"]
    DEVOPS["Docker / GitHub"]

    USER --> AGENT --> MCP --> SERVER --> DEVOPS

The agent layer will focus on:

MCP tool discovery

MCP resources

MCP prompts

Tool selection

Multi-step execution

Context management

Short-term memory

Multi-agent orchestration

Example:

User:
"Why is my backend container failing?"

Agent:
1. Discover available MCP capabilities
2. Inspect the container
3. Read recent logs
4. Analyze the failure
5. Explain the likely cause

Roadmap

MCP

MCP server

Shared AppContext

Docker integration

GitHub integration

MCP resources

MCP prompts

AI Agent

MCP client

LLM integration

Tool discovery

Tool selection

Multi-step execution

Context management

Short-term memory

Multi-Agent

Supervisor agent

Docker specialist

GitHub specialist

Incident analysis agent

Agent routing / orchestration

Security

Never commit .env

Never commit GitHub tokens

Use fine-grained GitHub tokens

Grant only required repository permissions

Never log secrets

Keep Docker Engine access local

Validate destructive operations before execution

Tech Stack

Technology

Purpose

Python

Core language

MCP

AI tool protocol

Docker SDK

Docker Engine integration

GitHub REST API

GitHub integration

Requests

GitHub HTTP client

uv

Dependency management

Author

Jehad Hlewi
Software Engineer
GitHub: @jehadhl

<p align="center">
  <strong>OpsKraken</strong><br/>
  Exploring MCP, AI agents, and real DevOps tooling.
</p>