import time
import random
import os
import requests
import numpy as np

TARGET_URL = os.getenv("TARGET_URL", "http://cache-manager:5000/query")
DISTRIBUTION = os.getenv("DISTRIBUTION", "zipf") # uniform o zipf

# Equipos de ejemplo de la Liga de Primera de Chile para las consultas
equipos = ["Colo-Colo", "Universidad de Chile", "Universidad Católica", "Cobreloa", "Audax Italiano", "Everton"]
query_types = ["Q1", "Q2", "Q3", "Q4", "Q5"]

print(f"Iniciando generador de tráfico con distribución: {DISTRIBUTION}")
time.sleep(5)  # Esperar a que levanten los demás servicios

while True:
    try:
        q_type = random.choice(query_types)

        # Simular selección de equipos según la distribución elegida
        if DISTRIBUTION == "zipf":
            # La distribución de Zipf concentra los índices bajos (ej. Colo-Colo o U de Chile se piden harto)
            index = min(int(np.random.zipf(1.5)) - 1, len(equipos) - 1)
            team = equipos[index]
        else:
            # Distribución Uniforme
            team = random.choice(equipos)

        payload = {
            "type": q_type,
            "params": {"team": team}
        }

        requests.post(TARGET_URL, json=payload, timeout=5)

        # Pausa breve entre peticiones (ajustable para generar mayor throughput)
        time.sleep(0.1)
    except Exception as e:
        print(f"Error generando tráfico: {e}")
        time.sleep(1)