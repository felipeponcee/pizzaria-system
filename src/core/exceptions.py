"""Exceções da aplicação. A mensagem de cada uma pode ser exibida ao usuário."""


class AppError(Exception):
    """Erro esperado, com mensagem amigável em português."""


class ValidationError(AppError):
    """Dado de entrada inválido."""


class NotFoundError(AppError):
    """Registro não encontrado."""


class BusinessRuleError(AppError):
    """Operação não permitida pelas regras do negócio."""
