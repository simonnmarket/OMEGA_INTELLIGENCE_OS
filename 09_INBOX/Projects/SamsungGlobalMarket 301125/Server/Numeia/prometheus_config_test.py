# ==============================================================================
# CONFIGURAÇÃO DE TESTE - PROMETHEUS V2.3
# ==============================================================================
# 
# INSTRUÇÕES:
# 
# MODO TESTE (apenas símbolos específicos):
#   - Defina TEST_MODE = True
#   - Defina TEST_SYMBOLS com os símbolos desejados
#
# MODO NORMAL (todos os ativos do Market Watch):
#   - Defina TEST_MODE = False
#   - TEST_SYMBOLS será ignorado
#
# ==============================================================================

# ==============================================================================
# CONFIGURAÇÃO ATUAL - MODO TESTE
# ==============================================================================
TEST_MODE = True  # True = Modo Teste | False = Modo Normal (todos os ativos)

# Símbolos para teste (usado apenas quando TEST_MODE = True)
TEST_SYMBOLS = [
    "XAGUSD",
    "XAGAUD", 
    "XAGEUR",
    "XAGGBP"
]

# ==============================================================================
# PARA VOLTAR AO MODO NORMAL:
# ==============================================================================
# Altere TEST_MODE = False acima
# ==============================================================================

