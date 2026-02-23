# MEMORY_ID: TASK_METALS_KITCO
# TIMESTAMP: 09-11-2025 20:03 CET
# AUTOR: Cursor_Omega

## Objetivo
Integrar o feed público da Kitco ao ecossistema Prometheus para monitorar metais (ouro, prata, platina, paládio), persistir históricos, disparar alertas institucionais e disponibilizar dashboard para análise.

## Estrutura do Módulo
- `Core/Feeds/MetalsKitco/Config.py`: parâmetros centrais e caminho seguro do banco (SQLite).
- `Core/Feeds/MetalsKitco/Logger.py`: logger institucional.
- `Core/Feeds/MetalsKitco/KitcoClient.py`: coleta via `requests` + `BeautifulSoup`.
- `Core/Feeds/MetalsKitco/Repository.py`: ORM com SQLAlchemy, base `metal_prices`.
- `Core/Feeds/MetalsKitco/Alerts.py`: alertas parametrizáveis por limite.
- `Core/Feeds/MetalsKitco/Dashboard.py`: painel Streamlit.
- `Core/Feeds/MetalsKitco/Service.py`: orquestração completa.
- `Server/MetalsKitco_Service.py`: serviço stand-alone (CLI).

## Dependências
```
pip install requests beautifulsoup4 sqlalchemy streamlit pandas
```

## Execução
### Coleta Única
```
python -m SamsungGlobalMarket.Server.MetalsKitco_Service --once
```

### Loop Contínuo (15 min padrão)
```
python -m SamsungGlobalMarket.Server.MetalsKitco_Service
```

### Abrindo Dashboard após cada ciclo
```
python -m SamsungGlobalMarket.Server.MetalsKitco_Service --dashboard --once
```
> O dashboard também pode ser lançado diretamente com:
```
streamlit run SamsungGlobalMarket/Core/Feeds/MetalsKitco/Main.py
```

## Alertas
- Limites padrão:
  - Ouro: 2000
  - Prata: 50
  - Platina: 2000
  - Paládio: 1500
- Ajustes podem ser feitos ao instanciar `MetalsKitcoService(alert_limits=...)`.
- Alertas são registrados no logger `prometheus.kitco.alerts`.

## Integração com Prometheus
- Dados são persistidos em `Core/Feeds/MetalsKitco/Data/metal_prices.db`.
- O serviço respeita o protocolo de logging institucional.
- Pode ser monitorado/acionado pelos scripts PowerShell existentes (extensões futuras).

## Próximos Passos (Opcional)
- Integrar streaming de eventos econômicos para correlação com metais.
- Publicar métricas no watchdog central.
- Replicar base SQLite para data warehouse corporativo.

