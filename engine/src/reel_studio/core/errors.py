class ReelError(Exception):
    """Erro esperado, com mensagem pronta para o usuário."""


class ContractError(ReelError):
    """JSON fora do contrato definido em contracts/."""
