from http.server import BaseHTTPRequestHandler
import json
import numpy as np

# Load telemetry data
with open("q-vercel-latency.json") as f:
    TELEMETRY = json.load(f)

def compute_metrics(regions, threshold_ms):
    result = {}
    for region in regions:
        records = [r for r in TELEMETRY if r["region"] == region]
        if not records:
            continue
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 4),
            "p95_latency": round(float(np.percentile(latencies, 95)), 4),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(1 for l in latencies if l > threshold_ms)
        }
    return result

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        regions = body.get("regions", [])
        threshold_ms = body.get("threshold_ms", 180)

        result = compute_metrics(regions, threshold_ms)

        self.send_response(200)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
