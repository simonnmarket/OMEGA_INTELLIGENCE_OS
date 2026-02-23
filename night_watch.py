import requests
import json
import time
import os
from datetime import datetime

CSV_FILE = "01_CORE/orbit_telemetry.csv"

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", encoding="utf-8") as f:
            f.write("Timestamp,Symbol,Price,Volume_Delta,Order_Flow,Trend,Volatility,Absorption\n")

def log_orbit_data():
    try:
        response = requests.get("http://127.0.0.1:5000/api/scan/crypto", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(CSV_FILE, "a", encoding="utf-8") as f:
                for symbol, metrics in data.items():
                    if metrics.get('price', 0) > 0:
                        f.write(f"{timestamp},{symbol},{metrics['price']},{metrics['volume_delta']},{metrics['order_flow']},{metrics['trend']},{metrics['volatility']},{metrics['absorption']}\n")
            
            print(f"[{timestamp}] Telemetria CTI gravada com sucesso. ({len(data)} ativos)")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Erro na API: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("FALHA DE CONEXAO: API Bridge offline. Retentando no proximo ciclo...")
    except Exception as e:
        print(f"Erro no coletor noturno: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🌙 OMEGA OS - NIGHT WATCH MODO AUTONOMO")
    print("="*60)
    print("Iniciando coleta autonoma de Big Data CTI para validacao (Fim de Semana).")
    print(f"Arquivo alvo: {CSV_FILE}")
    print("Pressione Ctrl+C para encerrar pelos loggers do Windows.")
    
    init_csv()
    
    try:
        while True:
            log_orbit_data()
            # Coleta Big Data e CTI a cada 5 minutos (300 segs) para analise de domingo a noite
            time.sleep(300) 
    except KeyboardInterrupt:
        print("\n[!] Night Watch encerrado. Bom descanso.")
