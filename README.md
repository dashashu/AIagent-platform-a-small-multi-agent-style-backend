agent-platform
==============

Version: 0.1.0 (see pyproject.toml)

What it is
----------
Python project that exposes a chat-style HTTP API (via LangServe / LangChain), routes
messages to specialized agents (incident handling, Cassandra-oriented DB path), and
ships a separate MCP (Model Context Protocol) server for ticketing tools.

This repo does not train models. Configure an OpenAI-compatible endpoint if you want
LLM-based routing or richer answers.

FLOWCHART:
flowchart TD
    User([User HTTP Request]) --> FastAPI[FastAPI App / LangServe]
    FastAPI --> Runnable{LangChain Runnable Router}
    Runnable -->|Incident Intent| IncidentAgent[Incident Handling Agent]
    Runnable -->|Database Intent| CassandraAgent[Cassandra DB Agent]
    IncidentAgent --> MCPServer[Isolated MCP Server]
    MCPServer --> Ticketing[External Ticketing REST API]
(User HTTP Request)
                        │
                        ▼
             [FastAPI App / LangServe]
                        │
                        ▼
           /─────────────────────────\
          │ LangChain Runnable Router │
           \─────────────────────────/
             │                     │
      Incident Intent       Database Intent
             │                     │
             ▼                     ▼
    [Incident Handling     [Cassandra DB Agent]
          Agent]
            │
            ▼
   [Isolated MCP Server]
            │
            ▼
    [External Ticketing
         REST API]

Requirements
------------
- Python 3.10+
- Virtual environment recommended


Install
-------
From the project root (directory containing pyproject.toml):

  python3 -m venv .venv
  source .venv/bin/activate          (Windows: .venv\Scripts\activate)
  pip install -e .

Optional Cassandra driver for the DB agent:

  pip install -e ".[cassandra]"


Run the chat HTTP service
-------------------------
  agent-chat

Default bind: 0.0.0.0:8080 (see agent_platform.chat.main).

Health check:
  GET http://localhost:8080/health

LangServe invoke (example):
  POST http://localhost:8080/v1/chat/invoke
  Content-Type: application/json

  {
    "input": {
      "message": "What is the status of INC-12345?",
      "user_id": null,
      "session_id": null
    }
  }

Other LangServe routes may be available under /v1/chat/ (e.g. playground) depending
on LangServe defaults.


Run the ticketing MCP server (stdio)
------------------------------------
Used by MCP clients (e.g. Cursor) as a subprocess:

  agent-mcp-ticketing

Configure ticketing REST base URL and API key (see environment variables below).
If unset, MCP tools return a structured "not configured" response.


Environment variables (prefix AGENT_)
-------------------------------------
Loaded from the environment; optional .env file is supported (see config.py).

LLM (OpenAI-compatible API), optional routing:
  AGENT_LLM_BASE_URL       Base URL of your API (no trailing slash issues handled in code)
  AGENT_LLM_API_KEY        API key / token
  AGENT_LLM_MODEL          Model name (default in code: your-trained-model)
  AGENT_USE_LLM_ROUTING    Set true to classify routes with the LLM instead of heuristics only

Cassandra (optional):
  AGENT_CASSANDRA_HOSTS    Comma-separated host list
  AGENT_CASSANDRA_KEYSPACE
  AGENT_CASSANDRA_USERNAME
  AGENT_CASSANDRA_PASSWORD

Ticketing HTTP backend (optional; used by MCP client):
  AGENT_TICKETING_BASE_URL
  AGENT_TICKETING_API_KEY

Do not commit real secrets. Use .env locally and keep it out of version control
(.gitignore includes .env).


Source layout (src/agent_platform)
----------------------------------
  chat/              FastAPI app + LangServe routes, Pydantic request/response models
  langchain_pipeline Runnable orchestration and routing helpers
  orchestrator/      Thin wrapper around the same runnable for in-process use
  agents/            Incident agent, Cassandra agent, shared base types
  mcp/               Ticketing MCP server entrypoint
  ticketing/         HTTP client for a generic ticketing REST API
  llm/               Optional raw OpenAI-compatible HTTP client (legacy / utilities)
  config.py          Settings and env binding


License / support
-----------------
Add your own license and contact information here if you distribute this project.
