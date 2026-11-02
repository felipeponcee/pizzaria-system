"""Janela principal (por enquanto vazia, só para validar o ambiente)."""
import customtkinter as ctk

from src.app.config import APP_NAME, APP_VERSION


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry("1100x700")
        self.minsize(900, 600)

        label = ctk.CTkLabel(
            self,
            text="Sistema de Gestão para Pizzaria",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        label.pack(expand=True)