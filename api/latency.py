import json
import statistics
import numpy as np

def handler(request):
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        }

    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    data = request.json()
    regions = data["regions"]
    threshold = data["threshold_ms"]

    with open("q-vercel-latency.json") as f:
        telemetry = json.load(f)

    result = {}

    for region in regions:
        records = [r for r in telemetry if r["region"] == region]

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]

        if not records:
            continue

        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": statistics.mean(uptimes),
            "breaches": sum(1 for l in latencies if l > threshold)
        }

    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json"
        },
        "body": json.dumps(result)
    }
