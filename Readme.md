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