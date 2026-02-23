# INSTRUÇÕES - BLOCO 1: ANÁLISE E IDENTIFICAÇÃO

## 🎯 OBJETIVO

Identificar e analisar todos os executores MT5 no sistema AURORA v5.1

## 📋 PRÉ-REQUISITOS

- Python 3.8+
- Diretório do projeto AURORA acessível
- Permissões de leitura em todos os diretórios

## 🚀 EXECUÇÃO

```bash
# 1. Navegar para diretório do projeto
cd /caminho/do/projeto/aurora

# 2. Executar Bloco 1
python bloco1_analise_identificacao.py

# 3. Confirmar quando solicitado
#    Digite 's' ou 'sim' para prosseguir
```

## 📊 SAÍDA ESPERADA

```
[2025-12-26 14:30:22.123] [INFO] [IDENTIFICACAO] Buscando em: .
[2025-12-26 14:30:22.456] [SUCCESS] [IDENTIFICACAO] Encontrado: ./mt5_executor.py (15384 bytes)
[2025-12-26 14:30:23.789] [INFO] [ANALISE_FUNCIONAL] Análise concluída: ./mt5_executor.py (score: 18/20)

✅ BLOCO 1 CONCLUÍDO - Pronto para BLOCO 2
📄 Checkpoint: checkpoint_analise_20251226_143022.json
```

## 📁 ARQUIVOS GERADOS

- `checkpoint_analise_YYYYMMDD_HHMMSS.json` - Resultados completos da análise
- `logs_arch001_bloco1/analise_YYYYMMDD_HHMMSS.log` - Logs detalhados

## 🔍 CONTEÚDO DO CHECKPOINT

O checkpoint contém:

```json
{
  "metadata": { ... },
  "fase_analise": {
    "executores_encontrados": [
      {
        "arquivo": "caminho/do/executor.py",
        "nome": "mt5_executor.py",
        "tamanho_bytes": 15384,
        "linhas": 450,
        "hash_md5": "abc123...",
        "score_funcional": 18
      }
    ],
    "analise_funcional": { ... },
    "recomendacoes_analise": [
      "Consolidar X executores em um único",
      "Manter como principal: caminho/do/executor.py"
    ]
  }
}
```

## 🧪 TESTES PÓS-EXECUÇÃO

```bash
# Verificar se checkpoint foi criado
ls -la checkpoint_analise_*.json

# Verificar conteúdo do checkpoint
python -c "import json; data=json.load(open('checkpoint_analise_*.json')); print(f'Executores: {data['fase_analise']['total_encontrados']}')"

# Verificar logs
tail -20 logs_arch001_bloco1/analise_*.log
```

## ⚠️ POSSÍVEIS PROBLEMAS

### "Nenhum executor encontrado"
- Verifique se está no diretório correto
- Execute busca manual: `find . -name "*mt5*executor*.py"`

### Erro de permissão
```bash
chmod +x bloco1_analise_identificacao.py
chmod -R 755 .
```

### Python não encontrado
```bash
python3 bloco1_analise_identificacao.py
```

## 🎯 CRITÉRIOS DE SUCESSO

✅ Checkpoint gerado com extensão .json  
✅ Logs criados na pasta logs_arch001_bloco1/  
✅ Lista de executores identificados  
✅ Análise funcional completa  

## ➡️ PRÓXIMO PASSO

**BLOCO 2:** Backup e Seleção - Usará o checkpoint gerado como entrada.

## 📞 SUPORTE

- Documentação: Este arquivo
- Logs: logs_arch001_bloco1/
- Checkpoint: checkpoint_analise_*.json

