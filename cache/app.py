from flask import Flask, request, jsonify
import redis
import requests
import time
import os
import json

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
SCRAPER_URL = os.getenv("SCRAPER_URL", "http://localhost:5001/scrape")
METRICS_URL = os.getenv("METRICS_URL", "http://localhost:5003/log")

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

@app.route('/query', methods=['POST'])
def handle_query():
    start_time = time.time()
    req_data = request.json
    q_type = req_data.get("type")
    key_params = req_data.get("params", {})

    # Construir una llave única para Redis
    cache_key = f"{q_type}:{json.dumps(key_params, sort_keys=True)}"

    hit = False
    response_data = {}

    try:
        cached_value = r.get(cache_key)
        if cached_value:
            hit = True
            response_data = json.loads(cached_value)
        else:
            # Cache Miss -> Llamar al Scraper
            hit = False
            scraper_resp = requests.post(SCRAPER_URL, json=req_data, timeout=10)
            if scraper_resp.status_code == 200:
                response_data = scraper_resp.json()
                # Guardar en caché con TTL de ejemplo (ej. 300 segundos)
                r.setex(cache_key, 300, json.dumps(response_data))
            else:
                return jsonify({"error": "Error al obtener datos del scraper"}), 502
    except redis.exceptions.ResponseError as re:
        # Atrapa error si Redis excede la memoria configurada (Memory limit reached)
        if "OOM" in str(re):
            requests.post(METRICS_URL, json={"event": "eviction"})
        hit = False
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    latency = (time.time() - start_time) * 1000  # en milisegundos

    # Registrar métrica del request
    try:
        requests.post(METRICS_URL, json={
            "event": "query",
            "hit": hit,
            "latency": latency
        })
    except:
        pass

    return jsonify({
        "source": "cache" if hit else "scraper",
        "data": response_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)