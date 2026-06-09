from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Inherited from Fase 3 — preserved for cross-phase consistency
# ---------------------------------------------------------------------------


class SystemStatus(str, Enum):
    """System-level operational status. Shared with Fase 3."""
    OPERATIONAL = "OPERACIONAL"
    ALERT       = "EM ALERTA"
    CRITICAL    = "CRÍTICO"
    RECOVERING  = "RECUPERANDO"

    def __str__(self) -> str:
        return self.value


class AlertType(str, Enum):
    """Alert classification. Shared with Fase 3."""
    ENERGY_DEFICIT       = "DÉFICIT ENERGÉTICO"
    PREDICTIVE_WARNING   = "ALERTA PREDITIVO"
    DUST_ACCUMULATION    = "ACÚMULO DE POEIRA"
    EQUIPMENT_FAILURE    = "FALHA DE EQUIPAMENTO"
    SENSOR_ERROR         = "ERRO DE SENSOR"
    MAINTENANCE_REQUIRED = "MANUTENÇÃO NECESSÁRIA"

    def __str__(self) -> str:
        return self.value


class AnomalyType(str, Enum):
    """Anomaly classification. Shared with Fase 3."""
    DUST_STORM        = "TEMPESTADE DE POEIRA"
    EQUIPMENT_FAILURE = "FALHA DE EQUIPAMENTO"
    SENSOR_ERROR      = "ERRO DE SENSOR"

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Module-level status — extended from Fase 3
# ---------------------------------------------------------------------------


class ModuleStatus(str, Enum):
    """
    Module operational state.

    Fase 3 states (preserved): OPERATIONAL, SURVIVAL, SHUTDOWN.
    Fase 4 extension: DEGRADED (intermediate state for graph-scale topology).
    """
    OPERATIONAL = "OPERACIONAL"
    DEGRADED    = "DEGRADADO"    # Fase 4 — partially functional node
    SURVIVAL    = "SOBREVIVÊNCIA"  # Fase 3 — minimum life-critical configuration
    SHUTDOWN    = "DESLIGADO"    # Fase 3 — fully offline

    def __str__(self) -> str:
        return self.value


# ---------------------------------------------------------------------------
# Fase 4 — graph topology
# ---------------------------------------------------------------------------


class EdgeType(str, Enum):
    PRESSURIZED_TUNNEL = "Túnel pressurizado"
    SURFACE_PATH       = "Caminho de superfície"
    WIRELESS           = "Wireless"

    def __str__(self) -> str:
        return self.value


class WeightType(str, Enum):
    DISTANCE = "distância (m)"
    ENERGY   = "energia (kW)"
    LATENCY  = "latência (ms)"

    def __str__(self) -> str:
        return self.value
