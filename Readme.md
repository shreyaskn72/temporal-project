This project uses Temporal running in Docker Compose while workflow workers and clients run directly on the host machine using the Python SDK. This keeps development simple while matching the architecture used in larger deployments.


# Temporal Python Hello World

A simple Temporal workflow example using:

- Temporal Server (Docker Compose)
- PostgreSQL
- Temporal UI
- Python SDK

## Prerequisites

- Docker Desktop
- Python 3.10+
- pip

---

## Project Structure

```text
.
├── docker-compose.yml
├── requirements.txt
├── workflows.py
├── worker.py
└── run_workflow.py
└──  api.py
```

---

## Start Temporal

Start Temporal Server, PostgreSQL, and Temporal UI:

```bash
docker compose up -d
```

Verify containers are running:

```bash
docker ps
```

Expected containers:

```text
temporal
temporal-postgres
temporal-ui
```

Open Temporal UI:

```text
http://localhost:8233
```

---

## Create Python Virtual Environment

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```cmd
python -m venv venv
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
temporalio
```

---

## Start Worker

Open a new terminal.

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run the worker:

```bash
python worker.py
```

Expected output:

```text
Worker started...
```

Leave this terminal running.

---

## Execute Workflow

Open another terminal.

Activate the virtual environment:

```bash
source venv/bin/activate
```

Run:

```bash
python run_workflow.py
```

Expected output:

```text
Hello Shreyas from Temporal!
```

---

## Verify Execution

Open Temporal UI:

```text
http://localhost:8233
```

You should see:

- Workflow execution
- Status: Completed
- Workflow history
- Activity execution details

---

## run by api

open terminal where api.py file exists run
```bash
uvicorn api:app --reload
```

Import postman collection attached to your postman to trigger apis.

### curl equivalent commands:
```bash
curl -X POST \
  http://localhost:8000/workflows/hello \
  -H "Content-Type: application/json" \
  -H "x-client-id: customer-a" \
  -d '{
        "name":"Shreyas"
      }'

```

Response is:
```bash
{
  "status": "STARTED",
  "workflow_id": "hello-cf7af93b-d47d-4e8a-9658-3fb863a9d457",
  "run_id": "e5dfd3a2-5a3f-41f5-8d43-9f7cfd0f74e4",
  "request_id": "7f44f4b7-11e2-48d5-b659-c8cb12cc8f0e",
  "client_id": "customer-a"
}
```

### status api curl:
```curl
curl http://localhost:8000/workflows/status/<workflow-id>
```
Example would be:
```curl
curl \
http://localhost:8000/workflows/status/hello-1e8a8a22-f1e7-4e4f-8a83-c4f9a8c8c4c2
```

Response while running:
```json
{
  "workflow_id": "hello-...",
  "run_id": "...",
  "workflow_type": "HelloWorkflow",
  "status": "RUNNING",
  "start_time": "2026-06-04T10:15:00Z",
  "close_time": null
}
```
Response after completion:
```json
{
  "workflow_id": "hello-...",
  "run_id": "...",
  "workflow_type": "HelloWorkflow",
  "status": "COMPLETED",
  "start_time": "2026-06-04T10:15:00Z",
  "close_time": "2026-06-04T10:15:01Z"
}
```
## Useful Commands

### View Temporal Logs

```bash
docker logs -f temporal
```

### View UI Logs

```bash
docker logs -f temporal-ui
```

### Stop Containers

```bash
docker compose down
```

### Stop Containers and Delete Database

```bash
docker compose down -v
```

### Restart Containers

```bash
docker compose restart
```

---

## Workflow Execution Flow

```text
run_workflow.py
        │
        ▼
Temporal Server
        │
        ▼
worker.py
        │
        ▼
HelloWorkflow
        │
        ▼
say_hello Activity
        │
        ▼
Result Returned
```

---

## Default Connection Details

Temporal Frontend:

```text
localhost:7233
```

Temporal UI:

```text
http://localhost:8233
```

PostgreSQL:

```text
Host: localhost
Port: 5432
Database: temporal
Username: temporal
Password: temporal
```