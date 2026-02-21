import os
import json
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "..", "q-vercel-latency.json")

with open(JSON_PATH, "r") as f:
    data = json.load(f)

@app.post("/api/latency")
async def latency(payload: dict):
    regions = payload["regions"]
    threshold = payload["threshold_ms"]

    result = {}

    for region in regions:
        rows = [r for r in data if r["region"] == region]
        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": sum(l > threshold for l in latencies),
        }

    return result
