from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Almacenamiento en memoria para las métricas de la ejecución
metrics_data = {
    "hits": 0,
    "misses": 0,
    "latencies": [],
    "scrape_times": [],
    "errors": 0,
    "evictions": 0
}

@app.route('/log', methods=['POST'])
def log_event():
    data = request.json
    event_type = data.get("event")

    if event_type == "query":
        if data.get("hit"):
            metrics_data["hits"] += 1
        else:
            metrics_data["misses"] += 1

        lat = data.get("latency")
        if lat is not None:
            metrics_data["latencies"].append(lat)

    elif event_type == "scrape":
        if not data.get("success", True):
            metrics_data["errors"] += 1
        duration = data.get("duration")
        if duration is not None:
            metrics_data["scrape_times"].append(duration)

    elif event_type == "eviction":
        metrics_data["evictions"] += 1

    return jsonify({"status": "logged"}), 200

@app.route('/metrics', methods=['GET'])
def get_metrics():
    latencies = metrics_data["latencies"]
    p50 = np.percentile(latencies, 50) if latencies else 0
    p95 = np.percentile(latencies, 95) if latencies else 0
    total_queries = metrics_data["hits"] + metrics_data["misses"]
    hit_rate = (metrics_data["hits"] / total_queries) if total_queries > 0 else 0

    summary = {
        "hits": metrics_data["hits"],
        "misses": metrics_data["misses"],
        "hit_rate": hit_rate,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "errors": metrics_data["errors"],
        "evictions": metrics_data["evictions"]
    }
    return jsonify(summary)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)