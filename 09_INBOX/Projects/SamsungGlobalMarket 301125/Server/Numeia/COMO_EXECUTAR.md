# Como Executar o Numeia v2.0

## Opção 1: Usando o Script Batch (Mais Fácil)

### Windows (CMD/PowerShell):
```bash
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
iniciar_numeia_v2.bat
```

OU simplesmente dê **duplo clique** no arquivo `iniciar_numeia_v2.bat` na pasta `SamsungGlobalMarket`.

---

## Opção 2: Usando o Script PowerShell

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket
.\iniciar_numeia_v2.ps1
```

---

## Opção 3: Comando Manual Direto

### Navegar até o diretório:
```bash
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia
```

### Executar:
```bash
python numeia_executor_v2.py
```

---

## Opção 4: De Qualquer Lugar (Caminho Absoluto)

```bash
python C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Server\Numeia\numeia_executor_v2.py
```

---

## Verificações Antes de Executar

### 1. MetaTrader 5 deve estar:
- ✅ Instalado
- ✅ Aberto e conectado à sua conta
- ✅ API habilitada (Configurações → Expert Advisors → Permitir trading algorítmico)

### 2. Arquivos necessários:
- ✅ `config.json` na pasta `SamsungGlobalMarket/`
- ✅ `numeia_executor_v2.py` na pasta `Server/Numeia/`

### 3. Dependências Python:
```bash
pip install MetaTrader5 pydantic prometheus-client requests numpy pandas
```

---

## Logs e Monitoramento

### Logs JSON:
- Arquivo: `Server/Numeia/numeia_execution.jsonl`
- Formato: JSON estruturado para análise forense

### Prometheus Metrics:
- Porta: `8000` (padrão)
- URL: `http://localhost:8000/metrics`

### Para parar o sistema:
- Pressione `Ctrl+C` no terminal

---

## Troubleshooting

### Erro: "Configuration file not found"
- Verifique se `config.json` está em `SamsungGlobalMarket/config.json`
- Verifique os caminhos relativos estão corretos

### Erro: "MT5 connection failed"
- Verifique se MetaTrader 5 está aberto e conectado
- Verifique se a API está habilitada nas configurações

### Erro: "Module not found"
- Execute: `pip install -r requirements.txt` (se existir)
- Ou instale manualmente: `pip install MetaTrader5 pydantic prometheus-client requests numpy pandas`

---

## Status da Validação

✅ Todos os testes passaram:
- Sintaxe Python: ✅
- Imports: ✅ (16 módulos)
- Configuração: ✅
- Testes Unitários: ✅ (3/3)

**Sistema pronto para execução!**

