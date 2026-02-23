# MEMORY_ID: TASK_CORE_SETUP
# TIMESTAMP: 2025-11-09T21:27:30+01:00
# AUTHOR: Cursor_Omega

"""
Ponto de entrada para execução do Core Prometheus.
"""

from __future__ import annotations

from Core.Config import load_config
from Core.Database import init_engine
from Core.Logger import get_logger
from Core.Orchestrator import Orchestrator
from Modules.Metals.MetalsClient import MetalsClient
from Modules.Crypto import CryptoClient
from Modules.Forex import ForexClient

logger = get_logger("prometheus.main")


def main() -> None:
    config = load_config()
    init_engine(config.get("database", {}).get("connection_string"))

    orchestrator = Orchestrator(config)

    metals_config = config.get("modules", {}).get("metals", {})
    metals_client = MetalsClient(metals_config)
    orchestrator.registrar_submodulo("metals", metals_client)

    crypto_config = config.get("modules", {}).get("crypto", {})
    if crypto_config:
        crypto_client = CryptoClient(crypto_config)
        orchestrator.registrar_submodulo("crypto", crypto_client)

    forex_config = config.get("modules", {}).get("forex", {})
    if forex_config:
        forex_client = ForexClient(forex_config)
        orchestrator.registrar_submodulo("forex", forex_client)

    orchestrator.executar_coleta()


if __name__ == "__main__":
    main()

