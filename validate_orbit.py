import requests
import json
import time

def validate_orbit():
    print("="*60)
    print("🚀 OMEGA OS - PROTOCOLO DE ORBITA CRIPTO (VALIDACAO CTI)")
    print("="*60)
    print("Aguardando telemetria da API Bridge (localhost:5000)...")
    
    try:
        # Puxa os dados da mesma API que o Dashboard HTML usa
        response = requests.get("http://127.0.0.1:5000/api/scan/crypto", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            for symbol, metrics in data.items():
                print(f"\n[ ALVO: {symbol} ] " + "-"*40)
                if metrics.get('price', 0) > 0:
                    print(f" -> Preco Atual:    ${metrics['price']:,.2f}")
                    print(f" -> Volume Delta:   {metrics['volume_delta']} (Forca Liquida - ultimos 1000 ticks)")
                    print(f" -> Order Flow:     {metrics['order_flow']}")
                    print(f" -> Tendencia:      {metrics['trend']}")
                    print(f" -> Volatilidade:   {metrics['volatility']} pts")
                    print(f" -> Absorcao Inst.: {metrics['absorption']}")
                else:
                    print(f" -> STATUS: OFFLINE OU SEM LIQUIDEZ NA CORRETORA")
                    
            print("\n" + "="*60)
            print("🟢 VALIDAÇÃO BEM-SUCEDIDA: Os motores CTI estão calculando Big Data.")
            print("="*60)
            
        else:
            print(f"❌ Erro da API: Código {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ FALHA DE CONEXAO: O servidor Flask (api_bridge.py) nao esta rodando.")
        print("Inicie a ponte com: python 08_DASHBOARD/api_bridge.py")
    except Exception as e:
        print(f"❌ Erro Critico: {e}")

if __name__ == "__main__":
    validate_orbit()
