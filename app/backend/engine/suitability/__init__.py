"""Pure scoring policy; no economics, network or engine imports."""
from .suitability import evaluar, etiqueta_ambiental

__all__ = ['evaluar', 'etiqueta_ambiental']
