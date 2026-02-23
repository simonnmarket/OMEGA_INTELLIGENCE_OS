# Solução: Provider SSH Ausente no Airflow

**Problema:** Ao tentar criar conexão SSH no Airflow UI, aparece:
```
"Tipo de conexão faltando? Certifique-se de ter instalado o pacote do provider correspondente ao Airflow."
```

**Causa:** O provider SSH (`apache-airflow-providers-ssh`) não está instalado nos containers do Airflow.

---

## ✅ Solução: Instalar Provider SSH Manualmente

O Airflow 3.1.2 **deveria** incluir o provider SSH por padrão, mas se não estiver disponível, precisamos instalá-lo manualmente.

### Método 1: Via Docker Exec (Rápido - Não Persiste Após Reinício)

**No PowerShell (Windows):**

```powershell
# Instalar no worker
docker exec -u root docker-airflow-worker-1 pip install apache-airflow-providers-ssh

# Instalar no scheduler
docker exec -u root docker-airflow-scheduler-1 pip install apache-airflow-providers-ssh

# Instalar no apiserver
docker exec -u root docker-airflow-apiserver-1 pip install apache-airflow-providers-ssh

# Instalar no dag-processor
docker exec -u root docker-airflow-dag-processor-1 pip install apache-airflow-providers-ssh

# Instalar no triggerer
docker exec -u root docker-airflow-triggerer-1 pip install apache-airflow-providers-ssh
```

**Depois, reinicie os containers:**

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Orchestration\Airflow\docker
docker compose -f docker-compose.yaml restart
```

**⚠️ Limitação:** Esta instalação será perdida se os containers forem reconstruídos (rebuild).

---

### Método 2: Dockerfile Customizado (Recomendado - Persiste)

1. **Criar arquivo `Dockerfile`** em `Orchestration/Airflow/docker/`:

```dockerfile
FROM apache/airflow:3.1.2
USER root
RUN pip install --no-cache-dir apache-airflow-providers-ssh
USER airflow
```

2. **Atualizar `docker-compose.yaml`** para usar o Dockerfile:

```yaml
x-airflow-common:
  &airflow-common
  build:
    context: .
    dockerfile: Dockerfile
  # Remova ou comente a linha: image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:3.1.2}
```

3. **Reconstruir os containers:**

```powershell
cd C:\Users\Lenovo\.cursor\SamsungGlobalMarket\Orchestration\Airflow\docker
docker compose -f docker-compose.yaml down
docker compose -f docker-compose.yaml build
docker compose -f docker-compose.yaml up -d
```

---

### Método 3: Verificar se Já Está Disponível (Airflow 3.1.2)

O Airflow 3.1.2 **já deve incluir** o provider SSH. Pode ser apenas necessário:

1. **Recarregar a página** do Airflow UI (F5)
2. **Limpar cache do navegador** (Ctrl+Shift+Delete)
3. **Verificar Connection Type novamente** após recarregar

---

## ✅ Validação

Após instalar:

1. **Recarregue a página** do Airflow UI (`http://localhost:8080`)
2. **Vá em Admin → Connections**
3. **Clique em "+ Add a new record"**
4. **Verifique Connection Type:**
   - ✅ Se `SSH` aparecer no dropdown → **SUCESSO!**
   - ❌ Se ainda não aparecer → Execute Método 1 ou 2 acima

---

**Status:** ⏳ Aguardando instalação do provider SSH  
**Data:** 2025-11-16 (CET/Berlin)

