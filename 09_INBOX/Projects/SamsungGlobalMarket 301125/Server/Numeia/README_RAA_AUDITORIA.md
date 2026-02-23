# GUIA DE USO: SCRIPT DE AUDITORIA RÁPIDA (RAA)

## 📋 Descrição

O script `raa_auditoria_rapida.py` executa uma auditoria automática para **PROVAR** que o Bloqueio Estratégico de SELL no Prometheus v6.0 está funcionando corretamente, conforme exigido pela Diretiva do CEO-Cientista-Chefe.

## 🔧 Pré-requisitos

### Opção 1: Com API do Gemini (Recomendado)
```bash
pip install google-generativeai
```

Depois, configure a API Key:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "sua-chave-api-aqui"

# Linux/Mac
export GEMINI_API_KEY="sua-chave-api-aqui"
```

### Opção 2: Modo Local (Sem API)
O script funciona sem a API do Gemini, usando análise local do código.

## 📁 Arquivos Necessários

1. **`prompt_ceo_cientista_final.txt`** - Diretriz do CEO (gerado pelo `GerenciadorPromptsCientista`)
2. **`prometheus_master_control_v6.0.py`** - Código do Prometheus para análise

## 🚀 Como Executar

### Passo 1: Gerar o Prompt do CEO (se ainda não foi gerado)
```bash
python gerenciador_prompts_cientista.py
```

### Passo 2: Executar a Auditoria
```bash
python raa_auditoria_rapida.py
```

## 📊 Saída do Script

O script gera:

1. **Relatório no Console:**
   - Status da verificação (SUCESSO/FALHA)
   - Tendência H4 detectada
   - Análise do filtro estratégico
   - Conclusão final do CEO

2. **Arquivo JSON:** `raa_audit_report.json`
   - Relatório completo em formato JSON
   - Pode ser usado para integração com outros sistemas

## 🔍 O Que o Script Valida

1. ✅ **Presença do Bloqueio Estratégico:**
   - Verifica se `primary_trend == "SELL"` está sendo checado
   - Confirma que `return None` é executado quando SELL é detectado
   - Valida que o evento `strategic_block_sell` está sendo logado

2. ✅ **Comportamento Esperado:**
   - Se tendência H4 = SELL → Sistema deve BLOQUEAR (retornar None)
   - Se tendência H4 = BUY → Sistema deve PERMITIR (se outros filtros passarem)

3. ✅ **Integridade do Código:**
   - Verifica se o código do Prometheus está presente
   - Confirma que a lógica de bloqueio está implementada corretamente

## 📝 Exemplo de Saída

```
================================================================================
✅ INICIANDO AUDITORIA RÁPIDA (RAA) - PROVA DA CORREÇÃO ESTRATÉGICA
================================================================================

✅ Diretriz carregada de: prompt_ceo_cientista_final.txt
   Tamanho: 1234 caracteres

⚠️  API Key do Gemini não encontrada ou biblioteca não disponível.
   Usando análise local do código...

================================================================================
📊 RELATÓRIO DE PROVA (JSON) GERADO PELO RAA
================================================================================
{
    "status_verificacao": "SUCESSO",
    "diretiva_aplicada": "BLOQUEIO_SELL_ATIVO_V1.1",
    "tendencia_h4_detectada": "BUY",
    "analise_filtro_estrategico": "O filtro estratégico está implementado corretamente...",
    "conclusao_final_ceo": "✅ BLOQUEIO ESTRATÉGICO ATIVO: O sistema está bloqueando corretamente todos os sinais SELL."
}
================================================================================

✅ Relatório salvo em: raa_audit_report.json

================================================================================
📋 RESUMO EXECUTIVO
================================================================================
Status: SUCESSO
Diretiva: BLOQUEIO_SELL_ATIVO_V1.1
Tendência H4 Detectada: BUY

Análise do Filtro:
  O filtro estratégico está implementado corretamente...

Conclusão Final (CEO):
  ✅ BLOQUEIO ESTRATÉGICO ATIVO: O sistema está bloqueando corretamente todos os sinais SELL.
================================================================================
```

## ⚠️ Troubleshooting

### Erro: "Arquivo de prompt não encontrado"
**Solução:** Execute primeiro o `gerenciador_prompts_cientista.py` para gerar o arquivo `prompt_ceo_cientista_final.txt`.

### Erro: "Biblioteca google-generativeai não encontrada"
**Solução:** 
- Instale com `pip install google-generativeai`
- Ou use o modo local (funciona sem a biblioteca)

### Erro: "API Key não encontrada"
**Solução:** 
- Configure a variável de ambiente `GEMINI_API_KEY`
- Ou use o modo local (não requer API Key)

## 📚 Referências

- **Diretiva Original:** `prompt_ceo_cientista_final.txt`
- **Código do Prometheus:** `prometheus_master_control_v6.0.py`
- **Relatório de Correção:** `RELATORIO_CORRECAO_BLOQUEIO_ESTRATEGICO.md`

---

**Última Atualização:** 25 de Novembro de 2025

