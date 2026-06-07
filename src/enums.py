from __future__ import annotations

from enum import Enum


class ModuleStatus(str, Enum):
    OPERATIONAL = "OPERACIONAL"
    DEGRADED    = "DEGRADADO"
    OFFLINE     = "OFFLINE"

    def __str__(self) -> str:
        return self.value


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
