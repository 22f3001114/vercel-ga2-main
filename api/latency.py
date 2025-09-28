import json
import numpy as np

def handler(request):
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        body = json.loads(request.body)
        regions = body.get("regions", [])
        threshold = body.get("threshold_ms", 180)

        with open("data/telemetry.json") as f:
            telemetry = json.load(f)

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

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST",
                "Access-Control-Allow-Headers": "*"
            },
            "body": json.dumps(result)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }