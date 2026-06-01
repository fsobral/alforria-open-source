"""
construtor.py — Cria a estrutura de diretórios e arquivos de configuração
de um projeto Alforria caso ainda não existam.
"""
import argparse
import sys
import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Conteúdo padrão dos arquivos de configuração
# ---------------------------------------------------------------------------

_CONF = """\
[path]
root = "."
relatorio = "./relatorios/"
GRUPOSPATH = "./dados/grupos.txt"
PREFPATH = "./dados/preferencias.tsv"
SARPATH  = "./dados/ensalamento.csv"
cursos = "./dados/sar097.txt"
ATRIBPATH = "./dados/pre_atribuidas.tsv"
FANTPATH = "./dados/fantasmas.csv"
DATPATH = "./dados/alforria.dat"
dat2 = "./lp/alforria2.dat"
SOLPATH = "./lp/alforria.sol"

# configurações do programa
[alforria]
# Numero maximo de impedimentos no formulario
MAXIMPEDIMENTOS =  5

# Início e fim do semestre AAAA-MM-DD
SEM1_INI = 2025-03-31
SEM2_INI = 2025-08-18

reldir = "./relatorios/"

[constantes]
chmax_efetivo_anual = 18
chmax_efetivo_semestral = 12
chmax_temporario_anual = 38
chmax_temporario_semestral = 20
chmin_efetivo_anual = 16
chmin_temporario_anual = 36
chmin_graduacao = 8

chesp_efetivo_anual =  18
chesp_temporario_anual = 36
"""

_GITIGNORE = """\
# Arquivos de dados sensíveis — não versionar
dados/
relatorios/

# Arquivos de solução do solver
*.sol

# Python
__pycache__/
*.pyc
"""

# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def criar_projeto(nome_projeto: str = ".") -> None:
    """Cria a estrutura de diretórios e arquivos de configuração de um projeto
    Alforria.  Se *nome_projeto* for omitido, utiliza o diretório atual.

    A função é idempotente: arquivos e diretórios já existentes não são
    sobrescritos.
    """

    raiz = Path(nome_projeto)

    # Diretórios a criar
    diretorios = [
        raiz / "dados",
        raiz / "relatorios",
    ]

    # Arquivos a criar: (caminho, conteúdo)
    arquivos = [
        (raiz / "config.toml",      _CONF),
        (raiz / ".gitignore",                _GITIGNORE),
    ]

    criados = []
    existentes = []

    # Cria o diretório raiz (se for um nome de projeto novo)
    if nome_projeto != "." and not raiz.exists():
        raiz.mkdir(parents=True)
        criados.append(str(raiz) + os.sep)

    # Cria subdiretórios
    for d in diretorios:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            criados.append(str(d) + os.sep)
        else:
            existentes.append(str(d) + os.sep)

    # Cria arquivos de configuração
    for caminho, conteudo in arquivos:
        if not caminho.exists():
            caminho.write_text(conteudo, encoding="utf-8")
            criados.append(str(caminho))
        else:
            existentes.append(str(caminho))

    # Relatório
    if criados:
        print("\nCriado:")
        for item in criados:
            print(f"  ✅ {item}")

    if existentes:
        print("\nJá existia (não modificado):")
        for item in existentes:
            print(f"  ⚠️  {item}")

    if not criados:
        print("\nNenhuma alteração necessária — projeto já estava configurado.")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="alforria_init", description="Cria projeto Alforria")
    parser.add_argument("nome_projeto", nargs="?", default=".")
    args = parser.parse_args(argv)
    criar_projeto(args.nome_projeto)

if __name__ == "__main__":
    main(sys.argv[1:])