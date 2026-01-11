# Molecular Mutation Pipeline

A system for generating molecular mutants using chemical mutation rules and evaluating pharmacological properties based on Lipinski's Rule of Five.

## Table of Contents

- [Pipeline Overview](#pipeline-overview)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [API Reference](#api-reference)

---

## Pipeline Overview

This pipeline performs:

1.  **Mutation Generation**: Generates molecular variants from input SMILES using chemical mutation rules (SMARTS reactions).
2.  **Property Calculation**: Calculates pharmacological properties (MW, LogP, HBD, HBA, TPSA, QED).
3.  **Filtering & Ranking**: Filters based on Lipinski's Rule of Five and ranks by QED score.
4.  **Storage**: Saves the results to PostgreSQL.

### The mutation rules include:

| Category | Description | Example |
|:---|:---|:---|
| **Small Modifications** | Small modifications on aromatic rings | Add F/Cl/Br, F↔Cl swap |
| **Bioisosteres** | Bioisosteric replacements | Carboxylic Acid → Tetrazole |
| **Chain Modifications** | Chain modifications | Methyl → Ethyl → Propyl |
| **Ring Modifications** | Ring structure modifications | Cyclopentane → Cyclohexane |

### DAG Pipeline Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  generate_      │────▶│  calculate_     │────▶│  save_to_       │
│  mutants (t1)   │     │  properties(t2) │     │  postgres (t3)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
   RDKit SMARTS            Lipinski's Rule       PostgreSQL
   Reactions               QED Score             Batch Insert
```

---

## 🛠 Tech Stack

### Backend API

| Technology | Version | Purpose |
|:---|:---|:---|
| **FastAPI** | 0.128.0 | REST API framework with async support, automatically generates OpenAPI docs. |
| **Uvicorn** | 0.40.0 | High-performance ASGI server for FastAPI. |
| **httpx** | 0.28.1 | Async HTTP client for calling the Airflow REST API. |
| **Pydantic** | 2.12.5 | Data validation and serialization. |

### Workflow Orchestration

| Technology | Version | Purpose |
|:---|:---|:---|
| **Apache Airflow** | 2.9.3 | Orchestration platform for managing DAGs, retry logic, and monitoring. |
| **LocalExecutor** | - | Allows running multiple tasks in parallel on the same machine. |

### Cheminformatics

| Technology | Version | Purpose |
|:---|:---|:---|
| **RDKit** | 2025.9.3 | Cheminformatics library: parses SMILES, runs SMARTS reactions, calculates molecular properties. |

### Data Storage

| Technology | Version | Purpose |
|:---|:---|:---|
| **PostgreSQL** | 13 | Database for storing mutant results, also serves as the metadata store for Airflow. |
| **Redis** | Latest | In-memory cache for temporarily storing mutants between Airflow tasks, speeding up data transfer. |

### Infrastructure

| Technology | Purpose |
|:---|:---|
| **Docker** | Packages the application into containers, ensuring it runs consistently across all environments. |
| **Docker Compose** | Manages the multi-container setup (FastAPI, Airflow, PostgreSQL, Redis). |

---

## Installation

### Minimum Requirements

- Docker >= 20.10
- Docker Compose >= 2.0
- 5GB Disk Space
- 2GB RAM

### Step 1: Clone the repository

```bash
git clone <repository-url>
cd model
```

### Step 2: Create the `.env` file

```bash
# .env
AIRFLOW_URL=http://airflow-webserver:8080
AIRFLOW_USERNAME=admin
AIRFLOW_PASSWORD=admin
```

### Step 3: Build and start the containers

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 4: Check the services

| Service | URL | Credentials |
|:---|:---|:---|
| FastAPI Docs | http://localhost:8000/docs | - |
| Airflow UI | http://localhost:8080 | admin / admin |

---

## API Reference

### POST `/run/`

Triggers the molecular mutant generation pipeline.

**Request:**

```bash
curl -X POST "http://localhost:8000/run/" \
  -H "Content-Type: application/json" \
  -d '["CC(C)Cc1ccc(C(C)C(=O)O)cc1", "c1ccccc1O"]'
```

**Request Body:**

```json
[
  "CC(C)Cc1ccc(C(C)C(=O)O)cc1",
  "c1ccccc1O"
]
```

**Response:**

```json
{
  "total_inputs": 2,
  "dag_run_id": "manual__20260111T150000123",
  "status": "success",
  "completed": true
}
```

**Response Fields:**

| Field | Type | Description |
|:---|:---|:---|
| total_inputs | int | The number of input SMILES. |
| dag_run_id | string | The ID of the DAG run in Airflow. |
| status | string | `success`, `failed`, or `timeout`. |
| completed | boolean | Whether the pipeline finished. |

### View results in PostgreSQL

```bash
# Access the PostgreSQL container
docker-compose exec postgres psql -U airflow -d airflow

# Query the results
SELECT * FROM molecule_mutants ORDER BY score DESC LIMIT 10;
```
