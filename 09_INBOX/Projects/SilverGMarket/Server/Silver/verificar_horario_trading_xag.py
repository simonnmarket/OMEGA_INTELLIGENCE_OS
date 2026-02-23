# ==============================================================================
# VERIFICADOR DE HORÁRIO DE TRADING - PRATA (XAG)
# Projeto: SilverGMarket (Independente)
# Adaptado para Berlim (CET/CEST)
# ==============================================================================
from datetime import datetime
import pytz

# Fusos horários
CET = pytz.timezone('Europe/Berlin')
NY = pytz.timezone('America/New_York')
LONDON = pytz.timezone('Europe/London')

def verificar_horario_trading():
    """Verifica se é um bom horário para operar prata em Berlim."""
    
    # Hora atual em Berlim
    agora_berlim = datetime.now(CET)
    hora_berlim = agora_berlim.hour
    dia_semana = agora_berlim.weekday()  # 0=Segunda, 6=Domingo
    
    # Hora em Nova York
    agora_ny = datetime.now(NY)
    hora_ny = agora_ny.hour
    
    print("="*70)
    print("VERIFICAÇÃO DE HORÁRIO DE TRADING - PRATA (XAG)")
    print("Projeto: SilverGMarket (Independente)")
    print("Fuso: Berlim (CET/CEST)")
    print("="*70)
    print()
    print(f"📅 Data/Hora em Berlim: {agora_berlim.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"📅 Data/Hora em NY: {agora_ny.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Verificar dia da semana
    dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    dia_nome = dias[dia_semana]
    print(f"📆 Dia da Semana: {dia_nome}")
    print()
    
    # Verificar se mercado está aberto
    mercado_aberto = True
    motivo = ""
    
    if dia_semana == 5:  # Sábado
        mercado_aberto = False
        motivo = "Sábado - Mercado fechado"
    elif dia_semana == 6:  # Domingo
        # Domingo abre às 23:00 CET (00:00 CEST)
        if hora_berlim < 23:
            mercado_aberto = False
            motivo = "Domingo - Mercado ainda fechado (abre às 23:00 CET)"
        else:
            mercado_aberto = True
            motivo = "Domingo - Mercado aberto (abriu às 23:00 CET)"
    elif dia_semana == 4:  # Sexta
        # Sexta fecha às 23:00 CET
        if hora_berlim >= 23:
            mercado_aberto = False
            motivo = "Sexta - Mercado fechou às 23:00 CET"
        else:
            mercado_aberto = True
            motivo = "Sexta - Mercado aberto (fecha às 23:00 CET)"
    else:
        # Segunda a Quinta - 24 horas
        mercado_aberto = True
        motivo = "Mercado aberto 24 horas"
    
    # Verificar pausa técnica diária (22:59-23:01 NY = 23:59-00:01 CET ou 00:59-01:01 CEST)
    pausa_tecnica = False
    if 22 <= hora_ny <= 23 or hora_ny == 0:
        pausa_tecnica = True
    
    # Classificar janela de trading
    janela = ""
    qualidade = ""
    recomendacao = ""
    
    if mercado_aberto:
        if 9 <= hora_berlim < 12:
            janela = "09:00-12:00 CET"
            qualidade = "⭐ EXCELENTE"
            recomendacao = "Abertura de Londres - Melhor janela do dia para prata"
        elif 14 <= hora_berlim < 17:
            janela = "14:00-17:00 CET"
            qualidade = "⭐⭐ IDEAL"
            recomendacao = "Sobreposição Londres-NY - Maior volume e movimentos limpos"
        elif 17 <= hora_berlim < 19:
            janela = "17:00-19:00 CET"
            qualidade = "⭐ BOM"
            recomendacao = "Continuação NY - Ainda muito bom, especialmente com notícias"
        elif 20 <= hora_berlim < 23:
            janela = "20:00-23:00 CET"
            qualidade = "⚠️ CUIDADO"
            recomendacao = "Final da sessão NY - Cuidado com whipsaws"
        elif 23 <= hora_berlim or hora_berlim < 9:
            janela = "23:00-09:00 CET"
            qualidade = "❌ EVITAR"
            recomendacao = "Sessão Asiática - Baixa liquidez, evite operar"
        else:
            janela = "12:00-14:00 CET"
            qualidade = "✅ BOM"
            recomendacao = "Meio-dia - Boa liquidez"
    else:
        janela = "FECHADO"
        qualidade = "❌ FECHADO"
        recomendacao = motivo
    
    # Resultado
    print("="*70)
    print("STATUS DO MERCADO")
    print("="*70)
    print(f"Status: {'✅ ABERTO' if mercado_aberto else '❌ FECHADO'}")
    print(f"Motivo: {motivo}")
    if pausa_tecnica:
        print(f"⚠️ Pausa Técnica Diária: Pode haver interrupção breve")
    print()
    
    print("="*70)
    print("JANELA DE TRADING ATUAL")
    print("="*70)
    print(f"Janela: {janela}")
    print(f"Qualidade: {qualidade}")
    print(f"Recomendação: {recomendacao}")
    print()
    
    # Recomendação final
    print("="*70)
    print("RECOMENDAÇÃO FINAL")
    print("="*70)
    
    if not mercado_aberto:
        print("❌ NÃO OPERAR - Mercado fechado")
        print(f"   {motivo}")
    elif pausa_tecnica:
        print("⚠️ AGUARDAR - Pausa técnica em andamento")
        print("   Aguarde alguns minutos antes de operar")
    elif "EXCELENTE" in qualidade or "IDEAL" in qualidade:
        print("✅ OPERAR - Excelente janela de trading")
        print(f"   {recomendacao}")
    elif "BOM" in qualidade:
        print("✅ OPERAR - Boa janela de trading")
        print(f"   {recomendacao}")
    elif "CUIDADO" in qualidade:
        print("⚠️ CUIDADO - Janela de menor qualidade")
        print(f"   {recomendacao}")
    else:
        print("❌ EVITAR - Janela de baixa qualidade")
        print(f"   {recomendacao}")
    
    print()
    print("="*70)
    
    return mercado_aberto and not pausa_tecnica and ("EXCELENTE" in qualidade or "IDEAL" in qualidade or "BOM" in qualidade)

if __name__ == "__main__":
    try:
        import pytz
    except ImportError:
        print("⚠️ Instalando pytz...")
        import subprocess
        subprocess.check_call(["pip", "install", "pytz"])
        import pytz
    
    verificar_horario_trading()

