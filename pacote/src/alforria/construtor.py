"""
construtor.py — Cria a estrutura de diretórios e arquivos de configuração
de um projeto Alforria caso ainda não existam.
"""

import os
from pathlib import Path


# ---------------------------------------------------------------------------
# Conteúdo padrão dos arquivos de configuração
# ---------------------------------------------------------------------------

_PATHS_CNF = """\
# Caminhos dos arquivos de dados do projeto.
# Edite os valores conforme a localização real de cada arquivo.

# Arquivo CSV com os grupos de disciplinas
GRUPOSPATH      dados/grupos.csv

# Arquivo de preferências dos professores (CSV)
PREFPATH        dados/preferencias.csv

# Arquivo SAR em CSV
SARPATH         dados/sar.csv

# Arquivo de turmas fantasmas (TSV)
FANTPATH        dados/fantasmas.tsv

# Arquivo de disciplinas pré-atribuídas (CSV)
ATRIBPATH       dados/pre_atribuidas.csv
"""

_ALFCFG_CNF = """\
# Configurações gerais do Alforria.

# Número máximo de impedimentos por professor
MAXIMPEDIMENTOS 5

# Diretório onde os relatórios serão salvos (com barra no final)
RELDIR          relatorios/
"""

_CONSTANTES_CNF = """\
# Parâmetros convencionados (limites de carga horária, etc.)
# Altere apenas se houver mudança nas normas do departamento.

chmax_efetivo_anual         20
chmax_efetivo_semestral     12
chmax_temporario_anual      40
chmax_temporario_semestral  22
chmax_diaria                8
chmin_efetivo_anual         16
chmin_temporario_anual      24
chmin_graduacao             8
numdiscmax_temporario       10
chesp_efetivo_anual         20
chesp_temporario_anual      40
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

_README = """\
# Projeto Alforria

Estrutura criada automaticamente pelo comando `alforria init`.

## Diretórios

| Diretório    | Descrição                                              |
|--------------|--------------------------------------------------------|
| `config/`    | Arquivos de configuração do projeto                    |
| `dados/`     | Arquivos de entrada (SAR, preferências, grupos, etc.)  |
| `relatorios/`| Saída gerada pelo Alforria (relatórios, CSV)           |

## Primeiros passos

1. Coloque os arquivos de dados em `dados/` conforme os caminhos em
   `config/paths.cnf`.
2. Ajuste `config/alforria.cnf` e `config/constantes.cnf` se necessário.
3. No diretório raiz do projeto, execute:

```
alforria
```

Dentro do shell interativo, use `load` para carregar os dados e `help` para
listar os comandos disponíveis.
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
        raiz / "config",
        raiz / "dados",
        raiz / "relatorios",
    ]

    # Arquivos a criar: (caminho, conteúdo)
    arquivos = [
        (raiz / "config" / "paths.cnf",      _PATHS_CNF),
        (raiz / "config" / "alforria.cnf",   _ALFCFG_CNF),
        (raiz / "config" / "constantes.cnf", _CONSTANTES_CNF),
        (raiz / ".gitignore",                _GITIGNORE),
        (raiz / "README.md",                 _README),
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