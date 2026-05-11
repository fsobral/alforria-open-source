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
