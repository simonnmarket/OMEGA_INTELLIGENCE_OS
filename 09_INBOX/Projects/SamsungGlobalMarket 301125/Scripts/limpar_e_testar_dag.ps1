# Limpar DAG run existente e testar novamente
Write-Host "=== Limpar e Testar DAG ===" -ForegroundColor Cyan

$dagId = "prometheus_mt5_executor"

Write-Host "1. Verificando runs existentes..." -ForegroundColor Yellow
$runs = docker exec docker-airflow-scheduler-1 airflow dags list-runs -d $dagId --output json 2>&1
Write-Host $runs

Write-Host "`n2. Limpar runs com falha..." -ForegroundColor Yellow
docker exec docker-airflow-scheduler-1 airflow dags clear $dagId --yes 2>&1 | Out-Null

Write-Host "`n3. Teste manual via UI ou aguarde proxima execucao agendada" -ForegroundColor Yellow
Write-Host "   Vá em: http://localhost:8080 > DAGs > $dagId > Trigger DAG" -ForegroundColor Cyan

