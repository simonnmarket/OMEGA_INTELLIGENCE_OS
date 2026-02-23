import pandas as pd

def analyze():
    print("Analise da Telemetria CTI (Night Watch)...")
    try:
        df = pd.read_csv("01_CORE/orbit_telemetry.csv")
        print(f"Total de amostras CTI: {len(df)}")
        print(f"Ativos monitorados: {df['Symbol'].unique()}")
        print(f"Primeiro registro: {df['Timestamp'].min()}")
        print(f"Ultimo registro: {df['Timestamp'].max()}")
        print("\n=== Resumo por Ativo ===")
        for symbol in df['Symbol'].unique():
            sdf = df[df['Symbol'] == symbol]
            print(f"- {symbol}: {len(sdf)} leituras")
            print(f"  Volatilidade Media: {sdf['Volatility'].mean():.2f} pts")
            print(f"  Absorcao Registrada: {len(sdf[sdf['Absorption'] == 'Detected'])} eventos de Red-Alert")
            print(f"  Dominancia de Fluxo: {sdf['Order_Flow'].mode()[0]}")
    except Exception as e:
        print(f"Erro na analise: {e}")

if __name__ == "__main__":
    analyze()
