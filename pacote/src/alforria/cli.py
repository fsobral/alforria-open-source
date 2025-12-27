import typer

from .construtor import criar_projeto

app = typer.Typer()


@app.command()
def init(nome_projeto: str):
    """Cria novo projeto"""
    criar_projeto(nome_projeto)
    print(f"✅ Projeto '{nome_projeto}' criado!")


# Outros comandos...
@app.command()
def run():
    """Executa processamento"""
    pass
