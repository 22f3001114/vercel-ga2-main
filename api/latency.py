from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import json
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

with open("data/telemetry.json") as f:
    telemetry = json.load(f)

@app.post("/latency")
async def check_latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        records = telemetry.get(region, [])
        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime"] for r in records]
        breaches = sum(1 for l in latencies if l > threshold)

        result[region] = {
            "avg_latency": round(np.mean(latencies), 2),
            "p95_latency": round(np.percentile(latencies, 95), 2),
            "avg_uptime": round(np.mean(uptimes), 4),
            "breaches": breaches
        }

    return result

handler = Mangum(app)