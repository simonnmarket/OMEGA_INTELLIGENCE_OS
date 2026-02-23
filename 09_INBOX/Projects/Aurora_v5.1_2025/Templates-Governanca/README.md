# 📋 TEMPLATES DE GOVERNANÇA - AURORA v5.1

Esta pasta contém templates e ferramentas para planejamento e execução de ações no sistema Aurora seguindo o protocolo de governança institucional.

---

## 📁 ARQUIVOS

### Templates

- **`TEMPLATE_PLANO_ACAO.yaml`** - Template base (vazio, pronto para preencher)
- **`EXEMPLO_TEMPLATE_PREENCHIDO.yaml`** - Exemplo completo preenchido

### Processadores

- **`PROCESSAR_TEMPLATE_YAML.py`** - Processador automático de templates YAML

### Documentação

- **`README_TEMPLATE_YAML.md`** - Guia completo de uso

---

## 🚀 INÍCIO RÁPIDO

### 1. Copiar Template

```bash
cp TEMPLATE_PLANO_ACAO.yaml ../PLANO_[NOME]_[DATA].yaml
```

### 2. Preencher Template

Edite o arquivo YAML com suas informações.

### 3. Processar

```bash
# Validar (dry-run)
python PROCESSAR_TEMPLATE_YAML.py ../PLANO_[NOME]_[DATA].yaml --dry-run

# Executar
python PROCESSAR_TEMPLATE_YAML.py ../PLANO_[NOME]_[DATA].yaml
```

---

## 📚 DOCUMENTAÇÃO

Consulte `README_TEMPLATE_YAML.md` para guia completo de uso.

---

**Última atualização:** 2025-12-25

