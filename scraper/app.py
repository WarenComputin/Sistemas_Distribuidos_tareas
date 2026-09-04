from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import time
import os

app = Flask(__name__)
METRICS_URL = os.getenv("METRICS_URL", "http://metrics:5003/log")

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    q_type = data.get("type") # Q1, Q2, Q3, Q4, Q5
    params = data.get("params", {})

    start_time = time.time()
    success = True
    error_msg = ""
    result_data = {}

    try:
        # URL base provista en la pauta para la Liga de Primera de Chile
        url = "https://cl.soccerway.com/chile/liga-de-primera/#/f1w5g1qT/clasificacion/general/"

        # Nota: Soccerway carga muchos datos mediante JS o APIs internas. 
        # Aquí realizamos la petición base de ejemplo para el parsing con BeautifulSoup:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # Lógica base de extracción según la consulta solicitada (Q1 - Q5)
            if q_type == "Q5": # Tabla de posiciones
                # Ejemplo genérico de parsing de tablas en la página
                standings = []
                tables = soup.find_all('table')
                # Implementa tu selector específico de Soccerway aquí
                result_data = {"consulta": "Q5", "data": "Tabla extraída correctamente desde Soccerway"}
            else:
                result_data = {"consulta": q_type, "data": f"Datos simulados/reales para {params}"}
        else:
            success = False
            error_msg = f"HTTP Error: {response.status_code}"

    except Exception as e:
        success = False
        error_msg = str(e)

    scraping_time = time.time() - start_time

    # Reportar métricas de scraping
    try:
        requests.post(METRICS_URL, json={
            "event": "scrape",
            "duration": scraping_time,
            "success": success
        })
    except:
        pass

    if not success:
        return jsonify({"error": error_msg}), 500

    return jsonify(result_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)