import pandas as pd
import numpy as np
import logging
from core_harmonizator import OMEGAHarmonizator, NumeiaPortfolioManager, WhaleAndVolatilityScanner

# Setup basic logging to only show messages
logging.basicConfig(level=logging.CRITICAL)

print("="*60)
print("OMEGA QUANTUM CORE - QUANTITATIVE STRESS TEST MATRIX")
print("="*60)

# SCENARIO 1: THE WHIPSAW (Flash Crash / Choppy Market)
# Alta variação, candles erráticos, picos de volume aleatórios.
print("\n[TEST START] SCENARIO 1: MARKET WHIPSAW (Caos Algoritmico e Pavios Longos)")
np.random.seed(42)
whipsaw_close = np.random.normal(100, 5, 60) # Alta variância
whipsaw_high = whipsaw_close + np.random.uniform(1, 10, 60)
whipsaw_low = whipsaw_close - np.random.uniform(1, 10, 60)
whipsaw_vol = np.random.uniform(10, 500, 60)

df_whipsaw = pd.DataFrame({
    'close': whipsaw_close, 'high': whipsaw_high, 'low': whipsaw_low, 'tick_volume': whipsaw_vol
})

result_whipsaw = OMEGAHarmonizator.execute_global_scan({'ASSET_WHIPSAW': df_whipsaw})
res = result_whipsaw['ASSET_WHIPSAW']
print(f" -> Regime Detectado: {res['regime']}")
print(f" -> Coerencia Sensorial: {res['coherence']*100:.1f}%")
print(f" -> Energia Termal (Apollo): {res['apollo_thermal']}%")

if res['regime'] == "DISSONANT_NOISE":
    print(" [VEREDICTO]: APROVADO. O sistema percebeu a armadilha e bloqueou entradas cegas.")
else:
    print(" [VEREDICTO]: REPROVADO. O sistema foi enganado pelo ruido.")

# SCENARIO 2: INSTITUTIONAL ACCUMULATION (Harmonic Flow)
# Tendência limpa, volume em escala ascendente.
print("\n[TEST START] SCENARIO 2: INSTITUTIONAL ACCUMULATION (Fluxo Direcional Limpo)")
trend_close = np.linspace(100, 120, 60) + np.random.normal(0, 0.2, 60) # Tendência limpa
trend_high = trend_close + np.random.uniform(0.1, 0.5, 60)
trend_low = trend_close - np.random.uniform(0.1, 0.5, 60)
trend_vol = np.linspace(100, 2000, 60) # Instituições adicionando lote

df_trend = pd.DataFrame({
    'close': trend_close, 'high': trend_high, 'low': trend_low, 'tick_volume': trend_vol
})

result_trend = OMEGAHarmonizator.execute_global_scan({'ASSET_TREND': df_trend})
res2 = result_trend['ASSET_TREND']
print(f" -> Regime Detectado: {res2['regime']}")
print(f" -> Coerencia Sensorial: {res2['coherence']*100:.1f}%")
print(f" -> Energia Termal (Apollo): {res2['apollo_thermal']}%")

if res2['regime'] == "HARMONIC_FLOW":
    print(" [VEREDICTO]: APROVADO. O sistema leu a energia institucional e acendeu a luz verde para o ataque.")
else:
    print(" [VEREDICTO]: REPROVADO. O sistema ignorou uma tendencia obvia institucional.")

# SCENARIO 3: NUMEIA KILL SWITCH
print("\n[TEST START] SCENARIO 3: NUMEIA KILL-SWITCH (Crash da Conta / Cisne Negro)")
initial_balance = 100000.0
# O mercado colapsa e o equity cai 31% abaixo do saldo inicial
current_equity = 69000.0 
is_dead = NumeiaPortfolioManager.check_kill_switch(initial_balance, current_equity)

print(f" -> Saldo Inicial: ${initial_balance} | Saldo Atual: ${current_equity} (-31%)")
if is_dead:
    print(" [VEREDICTO]: APROVADO. O Kill-Switch desarmou todo o sistema cortando a alavancagem imediatamente.")
else:
    print(" [VEREDICTO]: REPROVADO. O sistema permitiu a conta continuar sangrando.")

print("\n" + "="*60)
