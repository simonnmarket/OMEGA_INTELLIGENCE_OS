# MEMORY_ID: TASK_MARKET_SESSION_MANAGER
# TIMESTAMP: 2025-11-09T19:49:00+01:00
# AUTHOR: Cursor_Omega

"""
Gerenciador institucional de sessões de mercado (CET/Berlin).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
from typing import Dict, Iterable, List, Optional
from zoneinfo import ZoneInfo

from .config_market_sessions import (
    ASSET_GROUP_SYMBOLS,
    GROUP_MAX_TICK_AGE_SECONDS,
    MODE_ALLOWED_GROUPS,
    SESSION_WINDOWS,
    SPECIAL_DATE_MODES,
)
from .logger_market_sessions import get_calendar_logger

logger = get_calendar_logger()


class MarketSessionMode(str, Enum):
    """Modos possíveis de operação."""

    FULL = "full"
    FOREX_ONLY = "forex_only"
    CRYPTO_ONLY = "crypto_only"
    CLOSED = "closed"


WEEKDAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


@dataclass(frozen=True)
class SessionWindow:
    """Janela de sessão com início/fim e modo associado."""

    days: Iterable[str]
    start: time
    end: time
    mode: MarketSessionMode

    def matches(self, target: datetime) -> bool:
        day_name = WEEKDAY_NAMES[target.weekday()]
        if day_name not in self.days:
            return False

        current_time = target.time()
        return self.start <= current_time <= self.end


class MarketSessionManager:
    """Controla permissões de negociação por horário e grupo de ativos."""

    def __init__(self) -> None:
        self.timezone = ZoneInfo("Europe/Berlin")
        self.windows: List[SessionWindow] = [
            SessionWindow(
                days=window["days"],
                start=window["start"],
                end=window["end"],
                mode=MarketSessionMode(window["mode"]),
            )
            for window in SESSION_WINDOWS
        ]
        self.symbol_groups: Dict[str, str] = {}
        for group, symbols in ASSET_GROUP_SYMBOLS.items():
            for symbol in symbols:
                self.symbol_groups[symbol] = group

    # ------------------------------------------------------------------ #
    # MODO ATUAL
    # ------------------------------------------------------------------ #
    def get_active_mode(self, current_dt: Optional[datetime] = None) -> MarketSessionMode:
        """Determina o modo ativo conforme calendário CET."""

        current_dt = current_dt.astimezone(self.timezone) if current_dt else datetime.now(self.timezone)
        date_key = current_dt.strftime("%Y-%m-%d")
        special_mode = SPECIAL_DATE_MODES.get(date_key)
        if special_mode:
            logger.info("🗓️ Sessão especial %s → modo %s", date_key, special_mode)
            return MarketSessionMode(special_mode)

        for window in self.windows:
            if window.matches(current_dt):
                return window.mode

        return MarketSessionMode.CRYPTO_ONLY

    # ------------------------------------------------------------------ #
    # FILTROS DE UNIVERSO
    # ------------------------------------------------------------------ #
    def filter_universe(self, symbols: Iterable[str], mode: MarketSessionMode) -> List[str]:
        """Filtra universo baseado em grupos permitidos para o modo."""

        allowed_groups = MODE_ALLOWED_GROUPS.get(mode.value, ())
        filtered = [sym for sym in symbols if self.symbol_groups.get(sym) in allowed_groups]
        return filtered

    def is_symbol_allowed(self, symbol: str, mode: MarketSessionMode) -> bool:
        """Verifica se símbolo pertence a grupo habilitado no modo atual."""

        group = self.symbol_groups.get(symbol)
        if group is None:
            return False
        allowed_groups = MODE_ALLOWED_GROUPS.get(mode.value, ())
        return group in allowed_groups

    # ------------------------------------------------------------------ #
    # MAX TICK AGE
    # ------------------------------------------------------------------ #
    def max_tick_age_for(self, symbol: str, mode: MarketSessionMode) -> int:
        """Retorna limite de idade de tick adequado ao símbolo e modo."""

        if mode is MarketSessionMode.CLOSED:
            return 0

        group = self.symbol_groups.get(symbol)
        if group is None:
            return 0

        default_age = GROUP_MAX_TICK_AGE_SECONDS.get(group, 1800)
        if mode is MarketSessionMode.CRYPTO_ONLY and group == "crypto":
            return GROUP_MAX_TICK_AGE_SECONDS.get("crypto", default_age)

        if mode is MarketSessionMode.FOREX_ONLY and group == "forex":
            return GROUP_MAX_TICK_AGE_SECONDS.get("forex", default_age)

        return default_age

    # ------------------------------------------------------------------ #
    # UTILITÁRIOS
    # ------------------------------------------------------------------ #
    def classify_symbol(self, symbol: str) -> Optional[str]:
        """Retorna o grupo de um símbolo, caso mapeado."""

        return self.symbol_groups.get(symbol)

    def describe_mode(self, mode: MarketSessionMode) -> str:
        """Retorna descrição legível do modo."""

        allowed = MODE_ALLOWED_GROUPS.get(mode.value, ())
        return f"{mode.value} (grupos permitidos: {', '.join(allowed) if allowed else 'nenhum'})"

