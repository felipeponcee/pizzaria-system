"""Padrão visual do sistema: cores, tipografia, espaçamentos e status.

Cores no formato (claro, escuro) são trocadas automaticamente pelo
CustomTkinter quando o tema muda.
"""
import customtkinter as ctk

# Marca
PRIMARY = "#D9480F"
PRIMARY_HOVER = "#B83B0B"

# Fundos e textos
BACKGROUND = ("#F3F4F6", "#0F172A")
SURFACE = ("#FFFFFF", "#1E293B")
BORDER = ("#E5E7EB", "#334155")
TEXT = ("#111827", "#F1F5F9")
TEXT_MUTED = ("#6B7280", "#94A3B8")

# Menu lateral (escuro nos dois temas)
SIDEBAR_BG = ("#1F2937", "#111827")
SIDEBAR_TEXT = "#E5E7EB"
SIDEBAR_HOVER = ("#374151", "#1F2937")
SIDEBAR_WIDTH = 220

# Feedback
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"
INFO = "#2563EB"
NEUTRAL = "#6B7280"

# Status de pedido (chaves iguais às do banco)
STATUS_LABELS = {
    "received": "Recebido",
    "preparing": "Em preparação",
    "ready": "Pronto",
    "delivered": "Entregue",
    "canceled": "Cancelado",
}
STATUS_COLORS = {
    "received": INFO,
    "preparing": WARNING,
    "ready": SUCCESS,
    "delivered": NEUTRAL,
    "canceled": DANGER,
}

# Espaçamentos e formas
PAD_S = 8
PAD_M = 12
PAD_L = 20
RADIUS = 12

FONT_FAMILY = "Segoe UI"


def font(size: int = 14, weight: str = "normal") -> ctk.CTkFont:
    """Cria uma fonte padrão. Só chamar depois que a janela principal existir."""
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)
