NVIDIA Kumo Relational is a structured-data foundation model for prediction over relational, multi-table data. It uses declared schemas, relationships, entity tables, fact tables, context rows, and prediction rows without requiring callers to flatten connected tables into a single feature table.

The NVIDIA Kumo Relational Inference Microservice (NIM), release 1.0.0, accepts JSON arrays-format relational payloads through a structured-data API, validates the task, schema, context, and prediction contract, and invokes the Kumo Relational driver for synchronous inference.

This model is ready for commercial or non-commercial use.

## Model Architecture:

**Architecture Type:** Transformer **Network Architecture:** NVIDIA Kumo Relational 1.0.0 uses a table-invariant row encoder and exchanges information across connected tables and context labels with a Relational Graph Transformer. **Total Parameters:** 3.1*10^7

### Input:

**Input Types:** Tabular **Input Formats:** JSON arrays-format relational tables **Input Parameters:** One Dimensional (1D) **Other Properties Related to Input:** Requests declare an instance table, optional related tables, relationships, task metadata, labeled context rows, and prediction rows. Binary classification, multiclass classification, regression, and forecasting require exactly one entity table. Temporal link prediction requires source and target entity tables.

### Output:

**Output Types:** Tabular **Output Format:** JSON prediction results **Output Parameters:** One Dimensional (1D) **Other Properties Related to Output:** Task-dependent outputs include predictions, probabilities, scores, rankings, quantiles, embeddings, and single-row diagnostic explanations.

**Our AI models are designed and/or optimized to run on NVIDIA GPU-accelerated systems. By leveraging NVIDIA's hardware (e.g. GPU cores) and software frameworks (e.g., CUDA libraries), the model achieves faster training and inference times compared to CPU-only solutions.**

___

![[Screenshot 2026-09-27 120652.png]]

___
```

import json

import requests


payload = {
    "model": "kumo-relational",
    "task": {
        "kind": "binary_classification",
        "target": {
            "column_name": "label",
            "dtype": "bool",
            "classes": ["false", "true"],
            "positive_class": "true",
        },
        "entity_table_names": ["accounts"],
        "anchor_time_column": "anchor_time",
    },
    "schema": {
        "instance_table": {
            "columns": {
                "instance_id": {
                    "dtype": "int64",
                    "stype": "ID",
                    "nullable": False,
                },
                "anchor_time": {
                    "dtype": "timestamp[us]",
                    "stype": "timestamp",
                    "nullable": False,
                },
                "account_id": {
                    "dtype": "int64",
                    "stype": "ID",
                    "nullable": False,
                },
                "label": {
                    "dtype": "bool",
                    "stype": "categorical",
                },
            },
            "primary_key": "instance_id",
        },
        "related_tables": {
            "accounts": {
                "columns": {
                    "instance_id": {
                        "dtype": "int64",
                        "stype": "ID",
                        "nullable": False,
                    },
                    "account_id": {
                        "dtype": "int64",
                        "stype": "ID",
                        "nullable": False,
                    },
                    "amount": {
                        "dtype": "float64",
                        "stype": "numerical",
                    },
                    "segment": {
                        "dtype": "string",
                        "stype": "categorical",
                    },
                },
                "primary_key": ["instance_id", "account_id"],
            }
        },
        "relationships": [
            {
                "source_columns": ["instance_id", "account_id"],
                "target_table": "accounts",
                "target_columns": ["instance_id", "account_id"],
            }
        ],
    },
    "context": {
        "instance_table": {
            "format": "arrays",
            "columns": ["instance_id", "anchor_time", "account_id", "label"],
            "rows": [
                [0, "2025-01-01T00:00:00Z", 100, False],
                [1, "2025-01-01T00:00:00Z", 101, True],
                [2, "2025-01-02T00:00:00Z", 102, False],
                [3, "2025-01-02T00:00:00Z", 103, True],
            ],
        },
        "related_tables": {
            "accounts": {
                "format": "arrays",
                "columns": ["instance_id", "account_id", "amount", "segment"],
                "rows": [
                    [0, 100, 10.5, "small"],
                    [1, 101, 250.0, "enterprise"],
                    [2, 102, 12.0, "small"],
                    [3, 103, 300.0, "enterprise"],
                ],
            }
        },
    },
    "predict": {
        "instance_table": {
            "format": "arrays",
            "columns": ["instance_id", "anchor_time", "account_id"],
            "rows": [[4, "2025-02-01T00:00:00Z", 104]],
        },
        "related_tables": {
            "accounts": {
                "format": "arrays",
                "columns": ["instance_id", "account_id", "amount", "segment"],
                "rows": [[4, 104, 275.0, "enterprise"]],
            }
        },
    },
    "output": {"fields": ["prediction", "probabilities"]},
}

response = requests.post(
    "https://ai.api.nvidia.com/v1/structured-data/nvidia/kumo-relational/predictions",
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer $NVIDIA_API_KEY",
    },
    json=payload,
)
response.raise_for_status()

print(json.dumps(response.json(), indent=2))

```
___
## NVIDIA NIM Deployment Guide for Kumo Relational Model

This webpage outlines the three-step process for deploying the NVIDIA NIM inference microservice for the Kumo Relational model, enabling users to run the model on their own infrastructure without external model mounts or runtime downloads.

**Key Details:**
- **Step 1: Generate API Key**: Users must first generate an API key to authenticate their deployment.
- **Step 2: Pull and Run the NIM**: Deploy the container using the provided command; it serves the packaged `kumo-relational` model and listens on internal port 8000 by default. Users can change the listen port via the `NIM_HTTP_API_PORT` environment variable, ensuring the Docker port mapping is updated accordingly.
- **Step 3: Test the NIM**: Verify the deployment by making a local API call using a `curl` command to the `POST /v1/predictions` endpoint, as detailed in the API reference.

Following below steps allows for a self-contained deployment of the Kumo Relational model, streamlining the transition from model access to local inference service.


```markdown
# Kumo Relational Model Info with Code to Set Up

## Overview
Follow the steps below to download and run the NVIDIA NIM inference microservice for this model on your infrastructure of choice.

## Step 1: Generate API Key
You must first generate an API key to authenticate with the NVIDIA NIM service.

## Step 2: Pull and Run the NIM
Pull and run the NVIDIA NIM using the command below. The container serves the single packaged `kumo-relational` model; no external model mount or runtime model download is required.

**Port Configuration:**
*   The NIM listens on internal port **8000** by default.
*   Set `NIM_HTTP_API_PORT` only when intentionally changing the container listen port.
*   Ensure the Docker port mapping matches any changes made to `NIM_HTTP_API_PORT`.

**Command:**
```bash
# Replace <YOUR_API_KEY> with the key generated in Step 1
docker run -d \
  --name kumo-relational \
  -p 8000:8000 \
  -e NVIDIA_API_KEY=<YOUR_API_KEY> \
  nvcr.io/nim/kumo/kumo-relational:latest
```

## Step 3: Test the NIM
You can now make a local API call using this `curl` command to verify the service is running:

```bash
curl -X 'POST' \
  'http://localhost:8000/v1/predictions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "input": "Your query here"
}'
```
___
