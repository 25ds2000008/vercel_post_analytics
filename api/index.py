from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, os
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = os.path.join(os.path.dirname(__file__), "../q-vercel-latency.json")
with open(DATA_PATH) as f:
    TELEMETRY = json.load(f)

class Request(BaseModel):
    regions: list[str]
    threshold_ms: float

@app.post("/api/index")
def get_metrics(req: Request):
    result = {}
    for region in req.regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        result[region] = {
            "avg_latency": round(float(np.mean(latencies)), 4),
            "p95_latency": round(float(np.percentile(latencies, 95)), 4),
            "avg_uptime": round(float(np.mean(uptimes)), 4),
            "breaches": int(sum(1 for l in latencies if l > req.threshold_ms))
        }
    return result
```

---

**`requirements.txt`**
```
fastapi
numpy
