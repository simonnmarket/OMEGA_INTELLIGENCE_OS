# Configuração SSH Airflow - FINAL

**Status:** ✅ SSH funcionando  
**Data:** 2025-11-16 (CET/Berlin)

---

## ✅ Configuração Correta no Airflow UI

**Vá em:** http://localhost:8080 > Admin > Connections

**Edite ou crie:** `prometheus_executor_host`

**Preencha:**

- **Connection Id:** `prometheus_executor_host`
- **Connection Type:** `SSH`
- **Host:** `host.docker.internal`
- **Login:** `Lenovo`
- **Password:** (deixe **VAZIO**)
- **Port:** `22`
- **Extra:**
  ```json
  {"key_file": "/tmp/ssh_keys/airflow_ssh_key", "no_host_key_check": true}
  ```

**Clique em:** Save

---

## ✅ Verificação

Após configurar, teste a DAG:

1. Vá em **DAGs → `prometheus_mt5_executor`**
2. Clique em **Trigger DAG**
3. Verifique se `run_mt5_executor` fica **verde** (sucesso)

---

## 🔧 Se o Erro Persistir

Se ainda der erro `FileNotFoundError: '/tmp/ssh_keys/airflow_ssh_key'`, execute:

```bash
docker exec docker-airflow-worker-1 bash -c "mkdir -p /tmp/ssh_keys && cp /tmp/airflow_ssh_key /tmp/ssh_keys/ && chmod 600 /tmp/ssh_keys/airflow_ssh_key"
```

Isso garante que a chave existe no caminho correto.

---

**Próxima ação:** Configure no Airflow UI com os valores acima e teste a DAG.

