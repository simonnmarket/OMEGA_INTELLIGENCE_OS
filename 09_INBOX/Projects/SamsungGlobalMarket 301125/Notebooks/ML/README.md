# MEMORY_ID: TASK_ML_SETUP
# TIMESTAMP: 09-11-2025 21:40 CET
# AUTHOR: Cursor_Omega

## Notebooks de Exploração de Séries Temporais
1. `TimeSeriesExploration.ipynb` (criar a partir deste guia):
   - Carregar dados com `from Core.Analytics.MLDataPipeline import export_timeseries`
   - Visualizar `close` e calcular retornos.
   - Separar treino/validação (ex.: 80/20) e avaliar modelos base (ARIMA, Prophet, LSTM).
2. `FeatureEngineering.ipynb`:
   - Construir features (retorno log, volatilidade, médias móveis).
   - Exportar dataset pronto para treino (`save_timeseries_csv`).

### Passos Rápidos
```python
from Core.Analytics.MLDataPipeline import export_timeseries
df_gold = export_timeseries("gold")
df_gold.tail()
```

Salvar dataset:
```python
from Core.Analytics.MLDataPipeline import save_timeseries_csv
save_timeseries_csv("gold", "data/ml/gold_timeseries.csv")
```

> Utilize estes notebooks como base para o pipeline ML aprovado pelo conselho.

