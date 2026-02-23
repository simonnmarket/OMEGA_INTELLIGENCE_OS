# 🔌 AURORA v5.1 - INTEGRAÇÃO METATRADER 5

## 📋 Visão Geral

A integração MT5 permite que o sistema Aurora envie ordens diretamente para o MetaTrader 5, permitindo visualização e execução em tempo real no terminal.

## ✅ Status da Integração

- ✅ **Módulo MT5 Executor criado** (`04-Infraestrutura/mt5_executor.py`)
- ✅ **Integração com estratégias** (`aurora_strategies_integration.py`)
- ✅ **Script de teste** (`test_mt5_integration.py`)
- ✅ **Dependências atualizadas** (`requirements.txt`)

## 🚀 Instalação

### 1. Instalar MetaTrader 5

Certifique-se de que o MetaTrader 5 está instalado e rodando no seu computador.

### 2. Instalar Dependências Python

```bash
pip install MetaTrader5
```

Ou instalar todas as dependências:

```bash
pip install -r requirements.txt
```

## 🔧 Configuração

### Opção 1: Usar Conta Padrão do MT5

Se você já está logado no MetaTrader 5, o sistema tentará usar a conta padrão:

```python
from aurora_strategies_integration import AuroraStrategiesManager

# Inicializar sem credenciais (usa conta padrão)
manager = AuroraStrategiesManager(mt5_enabled=True)
```

### Opção 2: Especificar Credenciais

```python
from aurora_strategies_integration import AuroraStrategiesManager

# Inicializar com credenciais específicas
manager = AuroraStrategiesManager(
    mt5_enabled=True,
    mt5_login=123456,           # Número da conta
    mt5_password="sua_senha",   # Senha
    mt5_server="SeuBroker-Demo"  # Servidor
)
```

## 🧪 Teste de Integração

Execute o script de teste para validar a conexão:

```bash
# Teste básico (usa conta padrão)
python test_mt5_integration.py

# Teste com credenciais específicas
python test_mt5_integration.py --login 123456 --password senha --server broker

# Teste com símbolo específico
python test_mt5_integration.py --symbol BTCUSD
```

### O que o teste verifica:

1. ✅ **Conexão com MT5** - Verifica se consegue conectar
2. ✅ **Informações da conta** - Mostra saldo, equity, margem
3. ✅ **Informações do símbolo** - Verifica se símbolo está disponível
4. ✅ **Posições abertas** - Lista posições atuais
5. ✅ **Estatísticas** - Mostra estatísticas do executor

## 📊 Como Funciona

### Fluxo de Execução

```
1. Estratégia gera TradeSignal
   ↓
2. AuroraStrategiesManager recebe sinal
   ↓
3. MT5Executor converte sinal para ordem MT5
   ↓
4. Ordem enviada ao MetaTrader 5
   ↓
5. Ordem aparece no terminal MT5
```

### Exemplo de Uso

```python
from aurora_strategies_integration import AuroraStrategiesManager
import asyncio

async def main():
    # Inicializar gerenciador com MT5 habilitado
    manager = AuroraStrategiesManager(mt5_enabled=True)
    
    # Inicializar estratégias
    if manager.initialize_strategies():
        # Analisar símbolo (gera sinais e executa no MT5)
        result = await manager.analyze_with_all_strategies(
            symbol="BTC-USD",
            period="1d",
            interval="15m"
        )
        
        # Verificar execuções MT5
        for strategy_id, strategy_data in result.get("strategies", {}).items():
            mt5_executions = strategy_data.get("mt5_executions", [])
            for execution in mt5_executions:
                if execution.get("success"):
                    print(f"✅ Ordem executada: Ticket {execution['ticket']}")
                else:
                    print(f"❌ Falha: {execution.get('error')}")

asyncio.run(main())
```

## 📈 Monitoramento

### Ver Posições no MT5

As ordens executadas aparecerão automaticamente no terminal MT5:

1. Abra o terminal MT5
2. Vá para a aba **"Trade"**
3. As posições abertas aparecerão com:
   - Símbolo
   - Volume
   - Preço de abertura
   - Stop Loss / Take Profit
   - Lucro/Prejuízo atual

### Ver Estatísticas via Código

```python
# Obter estatísticas do executor MT5
status = manager.get_strategies_status()
mt5_stats = status.get("mt5_statistics", {})

print(f"Ordens enviadas: {mt5_stats.get('orders_sent', 0)}")
print(f"Ordens falhadas: {mt5_stats.get('orders_failed', 0)}")
print(f"Taxa de sucesso: {mt5_stats.get('success_rate', 0):.2f}%")
print(f"Posições abertas: {mt5_stats.get('positions_open', 0)}")
print(f"Lucro total: {mt5_stats.get('total_profit', 0):.2f}")
```

## ⚙️ Configurações Avançadas

### Ajustar Stop Loss e Take Profit

O executor MT5 usa valores padrão:
- **Stop Loss**: 100 pontos
- **Take Profit**: 200 pontos

Para ajustar, modifique o método `convert_signal_to_mt5_order` em `mt5_executor.py`:

```python
request = self.convert_signal_to_mt5_order(
    signal, 
    symbol_info,
    sl_points=150,  # Stop Loss em pontos
    tp_points=300   # Take Profit em pontos
)
```

### Desabilitar MT5 (Modo Simulação)

Para testar estratégias sem executar ordens reais:

```python
manager = AuroraStrategiesManager(mt5_enabled=False)
```

## 🔍 Troubleshooting

### Erro: "MetaTrader5 não disponível"

**Solução:**
```bash
pip install MetaTrader5
```

### Erro: "Falha ao inicializar MT5"

**Possíveis causas:**
1. MetaTrader 5 não está instalado
2. Terminal MT5 não está aberto
3. Caminho do terminal incorreto

**Solução:**
- Abra o MetaTrader 5
- Verifique se o terminal está rodando
- Se necessário, especifique o caminho no código:
  ```python
  executor = MT5Executor(path="C:/Program Files/MetaTrader 5/terminal64.exe")
  ```

### Erro: "Símbolo não disponível"

**Solução:**
- Verifique se o símbolo está disponível no seu broker
- Use símbolos no formato correto (ex: "EURUSD", "BTCUSD")
- Para crypto via yfinance, pode ser necessário mapear para símbolo MT5

### Ordens não aparecem no MT5

**Verificações:**
1. ✅ MT5 está conectado? (`executor.connected`)
2. ✅ Símbolo está disponível? (`executor.get_symbol_info(symbol)`)
3. ✅ Conta tem saldo suficiente?
4. ✅ Verificar logs para erros específicos

## 📝 Logs

Todos os eventos são registrados no logger `AURORA_MT5_EXECUTOR`:

```python
import logging
logging.getLogger("AURORA_MT5_EXECUTOR").setLevel(logging.DEBUG)
```

## 🎯 Próximos Passos

1. ✅ Integração MT5 implementada
2. ⏭️ Executar teste de conexão
3. ⏭️ Iniciar sistema Aurora com MT5 habilitado
4. ⏭️ Monitorar ordens no terminal MT5

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs do sistema
2. Execute `test_mt5_integration.py` para diagnóstico
3. Verifique se o MT5 está funcionando corretamente

---

**Status:** ✅ Integração MT5 completa e pronta para uso

