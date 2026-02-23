# ==============================================================================
# SCRIPT PARA VERIFICAR HISTÓRICO DE ORDENS DO MT5
# ==============================================================================
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json

print("🔍 VERIFICANDO ACESSO AO HISTÓRICO DE ORDENS DO MT5")
print("="*60)

# Conectar ao MT5
if not mt5.initialize():
    print(f"❌ Erro ao conectar ao MT5: {mt5.last_error()}")
    exit()

account_info = mt5.account_info()
if account_info:
    print(f"✅ Conectado à conta: {account_info.login}")
    print(f"   Balance: ${account_info.balance:.2f}")
    print()

# 1. Verificar posições abertas
print("📊 POSIÇÕES ABERTAS:")
print("-"*60)
positions = mt5.positions_get()
if positions:
    print(f"Total de posições abertas: {len(positions)}")
    for pos in positions:
        print(f"  Ticket: {pos.ticket} | {pos.symbol} | Tipo: {'BUY' if pos.type == 0 else 'SELL'} | Volume: {pos.volume} | PnL: ${pos.profit:.2f}")
else:
    print("Nenhuma posição aberta no momento.")
print()

# 2. Verificar histórico de ordens (últimas 24 horas)
print("📜 HISTÓRICO DE ORDENS (Últimas 24 horas):")
print("-"*60)
date_from = datetime.now() - timedelta(days=1)
date_to = datetime.now()

# Buscar ordens de histórico
history_orders = mt5.history_orders_get(date_from, date_to)
if history_orders:
    print(f"Total de ordens no histórico: {len(history_orders)}")
    print()
    print(f"{'Ticket':<10} {'Símbolo':<12} {'Tipo':<8} {'Volume':<10} {'Preço':<12} {'Lucro':<12} {'Data':<20}")
    print("-"*90)
    for order in history_orders[:20]:  # Mostrar últimas 20
        order_type = "BUY" if order.type == 0 else "SELL"
        order_time = datetime.fromtimestamp(order.time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{order.ticket:<10} {order.symbol:<12} {order_type:<8} {order.volume_initial:<10} ${order.price_open:<11.5f} ${order.profit:<11.2f} {order_time}")
    if len(history_orders) > 20:
        print(f"\n... e mais {len(history_orders) - 20} ordens")
else:
    print("Nenhuma ordem encontrada no histórico das últimas 24 horas.")
print()

# 3. Verificar histórico de deals (execuções)
print("💰 HISTÓRICO DE DEALS (Execuções - Últimas 24 horas):")
print("-"*60)
deals = mt5.history_deals_get(date_from, date_to)
if deals:
    print(f"Total de deals no histórico: {len(deals)}")
    print()
    print(f"{'Ticket':<10} {'Símbolo':<12} {'Tipo':<8} {'Volume':<10} {'Preço':<12} {'Lucro':<12} {'Data':<20}")
    print("-"*90)
    for deal in deals[:20]:  # Mostrar últimas 20
        deal_type = "BUY" if deal.type == 0 else "SELL"
        deal_time = datetime.fromtimestamp(deal.time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{deal.deal:<10} {deal.symbol:<12} {deal_type:<8} {deal.volume:<10} ${deal.price:<11.5f} ${deal.profit:<11.2f} {deal_time}")
    if len(deals) > 20:
        print(f"\n... e mais {len(deals) - 20} deals")
else:
    print("Nenhum deal encontrado no histórico das últimas 24 horas.")
print()

# 4. Verificar ordens do Prometheus (pelo Magic Number)
print("🤖 ORDENS DO PROMETHEUS (Magic: 99991):")
print("-"*60)
prometheus_orders = [o for o in (history_orders or []) if o.magic == 99991]
prometheus_deals = [d for d in (deals or []) if d.magic == 99991]

if prometheus_orders:
    print(f"Total de ordens do Prometheus: {len(prometheus_orders)}")
    for order in prometheus_orders[:10]:
        print(f"  Ticket: {order.ticket} | {order.symbol} | Volume: {order.volume_initial} | Preço: ${order.price_open:.5f}")
else:
    print("Nenhuma ordem do Prometheus encontrada no histórico.")

if prometheus_deals:
    print(f"\nTotal de deals do Prometheus: {len(prometheus_deals)}")
    total_pnl = sum(d.profit for d in prometheus_deals)
    print(f"PnL Total dos deals: ${total_pnl:.2f}")
else:
    print("Nenhum deal do Prometheus encontrado no histórico.")
print()

mt5.shutdown()
print("✅ Verificação concluída.")

