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
    print(f"{'Ticket':<12} {'Símbolo':<15} {'Tipo':<8} {'Volume':<10} {'Preço':<12}")
    print("-"*70)
    for order in history_orders[:30]:  # Mostrar últimas 30
        order_type = "BUY" if order.type == 0 else "SELL"
        volume = getattr(order, 'volume_initial', getattr(order, 'volume', 0))
        price = getattr(order, 'price_open', getattr(order, 'price', 0))
        print(f"{order.ticket:<12} {order.symbol:<15} {order_type:<8} {volume:<10} ${price:<11.5f}")
    if len(history_orders) > 30:
        print(f"\n... e mais {len(history_orders) - 30} ordens")
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
    print(f"{'Ticket':<12} {'Símbolo':<15} {'Tipo':<8} {'Volume':<10} {'Preço':<12} {'Lucro':<12}")
    print("-"*75)
    total_pnl = 0
    for deal in deals[:30]:  # Mostrar últimas 30
        deal_type = "BUY" if deal.type == 0 else "SELL"
        deal_time = datetime.fromtimestamp(deal.time).strftime("%Y-%m-%d %H:%M:%S") if hasattr(deal, 'time') and deal.time > 0 else "N/A"
        profit = getattr(deal, 'profit', 0)
        total_pnl += profit
        print(f"{deal.ticket:<12} {deal.symbol:<15} {deal_type:<8} {deal.volume:<10} ${deal.price:<11.5f} ${profit:<11.2f}")
    if len(deals) > 30:
        print(f"\n... e mais {len(deals) - 30} deals")
    print(f"\n💰 PnL Total dos deals mostrados: ${total_pnl:.2f}")
else:
    print("Nenhum deal encontrado no histórico das últimas 24 horas.")
print()

# 4. Verificar ordens do Prometheus (pelo Magic Number)
print("🤖 ORDENS DO PROMETHEUS (Magic: 99991):")
print("-"*60)
prometheus_orders = [o for o in (history_orders or []) if getattr(o, 'magic', 0) == 99991]
prometheus_deals = [d for d in (deals or []) if getattr(d, 'magic', 0) == 99991]

if prometheus_orders:
    print(f"Total de ordens do Prometheus: {len(prometheus_orders)}")
    for order in prometheus_orders[:15]:
        volume = getattr(order, 'volume_initial', getattr(order, 'volume', 0))
        price = getattr(order, 'price_open', getattr(order, 'price', 0))
        print(f"  Ticket: {order.ticket} | {order.symbol} | Volume: {volume} | Preço: ${price:.5f}")
else:
    print("Nenhuma ordem do Prometheus encontrada no histórico.")

if prometheus_deals:
    print(f"\nTotal de deals do Prometheus: {len(prometheus_deals)}")
    total_pnl = sum(getattr(d, 'profit', 0) for d in prometheus_deals)
    print(f"PnL Total dos deals: ${total_pnl:.2f}")
    print()
    print("Últimos 10 deals do Prometheus:")
    for deal in prometheus_deals[-10:]:
        deal_type = "BUY" if deal.type == 0 else "SELL"
        profit = getattr(deal, 'profit', 0)
        print(f"  {deal.ticket} | {deal.symbol} | {deal_type} | Volume: {deal.volume} | PnL: ${profit:.2f}")
else:
    print("Nenhum deal do Prometheus encontrado no histórico.")
print()

mt5.shutdown()
print("✅ Verificação concluída.")

