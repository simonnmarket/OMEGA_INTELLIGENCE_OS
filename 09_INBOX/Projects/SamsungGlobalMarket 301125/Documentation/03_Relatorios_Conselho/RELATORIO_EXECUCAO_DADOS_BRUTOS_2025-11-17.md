# RELATÓRIO DE EXECUÇÃO - DADOS BRUTOS

**Data:** 17 de Novembro de 2025 (CET/Berlin)  
**Autor:** Sistema Prometheus  
**Status:** ✅ DADOS BRUTOS COLETADOS

---

## RESULTADO DO SCRIPT: protocolo_refutacao_v1.py

```
METRIC,VALUE,UNIT,DESCRIPTION
BASELINE_SUMMARY,,,
strategy,Mean_Reversion_Bollinger_Bands,,Estratégia de baseline
symbol,EURUSD,,Símbolo testado
timeframe,H1,,Timeframe usado
years_of_data,10,anos,Período de dados históricos
walk_forward_periods,15,períodos,Número de períodos validados
,,,
AGGREGATE_METRICS,,,
total_trades,776,trades,Total de trades executados
win_rate,0.5580,ratio,Taxa de acerto
profit_factor,0.76,ratio,Lucro total / Perda total
total_return,-49209.00,USD,Retorno total acumulado
sharpe_ratio,-1.42,ratio,Sharpe ratio anualizado
max_drawdown,67141.00,USD,Maior queda do equity
max_drawdown_pct,14854.20,%,Max drawdown percentual
expected_value,-63.41,USD,Valor esperado por trade
,,,
WALK_FORWARD_AVERAGES,,,
avg_win_rate,0.5086,ratio,Win rate médio (Walk-Forward)
avg_sharpe_ratio,-77.46,ratio,Sharpe ratio médio (Walk-Forward)
avg_total_return,-2246.60,USD,Retorno total médio (Walk-Forward)
avg_max_drawdown,4897.13,USD,Max drawdown médio (Walk-Forward)
,,,
WALK_FORWARD_PERIODS,,,
period,start_date,end_date,trades,win_rate,total_return,sharpe_ratio,max_drawdown
1,2017-11-23,2018-05-22,55,0.6000,-4196.00,-1.85,5041.00
2,2018-05-22,2018-11-18,53,0.5472,-4285.00,-2.25,7577.00
3,2018-11-18,2019-05-17,57,0.5789,49.00,0.03,6002.00
4,2019-05-17,2019-11-13,55,0.4364,-11645.00,-7.60,11980.00
5,2019-11-13,2020-05-11,22,0.3636,-683.00,-0.45,6762.00
6,2020-05-11,2020-11-07,2,0.0000,-4164.00,-1139.68,2111.00
7,2020-11-07,2021-05-06,2,0.5000,-413.00,-1.77,0.00
9,2021-11-02,2022-05-01,4,0.7500,3504.00,6.94,2409.00
10,2022-05-01,2022-10-28,3,0.3333,-1566.00,-2.97,2781.00
11,2022-10-28,2023-04-26,1,1.0000,2623.00,0.00,0.00
12,2023-04-26,2023-10-23,16,0.1250,-4722.00,-9.03,6063.00
13,2023-10-23,2024-04-20,57,0.4386,-11068.00,-5.16,14091.00
14,2024-04-20,2024-10-17,56,0.7143,1936.00,1.31,1794.00
15,2024-10-17,2025-04-15,58,0.5690,-1653.00,-0.80,4677.00
16,2025-04-15,2025-10-12,55,0.6727,2584.00,1.34,2169.00
```

**FIM DO RESULTADO DO SCRIPT DE BASELINE**

---

## RESULTADO DO SCRIPT: triage_strategies.py

```
classification,file_name,relative_path,category,directory,status,total_return,max_drawdown,sharpe_ratio,win_rate,total_trades,symbol,timeframe,sma_period,stop_loss_pips,take_profit_pips,lot_size,has_backtest_function,has_strategy_class,error
,,,,,,,,,,,,,,,,,,,
SUMMARY,,,,,,,,,,,,,,,,,,,
total_strategies,15,,,,,,,,,,,,,,,,,,,
PROMISSOR,0,,,,,,,,,,,,,,,,,,,
ANÊMICO,0,,,,,,,,,,,,,,,,,,,
MORTO,15,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,,,,,,
DETAILS,,,,,,,,,,,,,,,,,,,
MORTO,CryptoBreakoutStrategy_Scientific.py,Core\Strategies\Crypto\CryptoBreakoutStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,CryptoFundingRateArbitrageStrategy_Scientific.py,Core\Strategies\Crypto\CryptoFundingRateArbitrageStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,CryptoLiquidityMiningStrategy_Scientific.py,Core\Strategies\Crypto\CryptoLiquidityMiningStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,CryptoMeanReversionStrategy_Scientific.py,Core\Strategies\Crypto\CryptoMeanReversionStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,BTC/USDT,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,CryptoMomentumStrategy_Scientific.py,Core\Strategies\Crypto\CryptoMomentumStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,CryptoTriangularArbitrageStrategy_Scientific.py,Core\Strategies\Crypto\CryptoTriangularArbitrageStrategy_Scientific.py,Crypto,Crypto,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,DefenseTechPairsStrategy_Scientific.py,Core\Strategies\Equities\DefenseTechPairsStrategy_Scientific.py,Equities,Equities,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,SectorRotationStrategy_Scientific.py,Core\Strategies\Equities\SectorRotationStrategy_Scientific.py,Equities,Equities,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,VolatilityArbitrageStrategy_Scientific.py,Core\Strategies\Equities\VolatilityArbitrageStrategy_Scientific.py,Equities,Equities,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,ForexCentralBankSentimentStrategy_Scientific.py,Core\Strategies\Forex\ForexCentralBankSentimentStrategy_Scientific.py,Forex,Forex,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,ForexCrossCurrencyArbitrageStrategy_Scientific.py,Core\Strategies\Forex\ForexCrossCurrencyArbitrageStrategy_Scientific.py,Forex,Forex,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,ForexSpreadCaptureStrategy_Scientific.py,Core\Strategies\Forex\ForexSpreadCaptureStrategy_Scientific.py,Forex,Forex,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,SyntheticCalendarSpreadStrategy_Scientific.py,Core\Strategies\Futures\SyntheticCalendarSpreadStrategy_Scientific.py,Futures,Futures,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,SyntheticTermStructureStrategy_Scientific.py,Core\Strategies\Futures\SyntheticTermStructureStrategy_Scientific.py,Futures,Futures,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
MORTO,GoldMacroInflectionStrategy_Scientific.py,Core\Strategies\Gold\GoldMacroInflectionStrategy_Scientific.py,Gold,Gold,NOT_TESTABLE,0.00,0.00,0.00,0.0000,0,,,,,,,False,True,Nenhuma função de backtest encontrada ou executável
```

**FIM DO RESULTADO DO SCRIPT DE TRIAGE**

---

**FIM DO TEMPLATE DE RESPOSTA**

