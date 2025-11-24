import funcoes_leitura
import funcoes_escrita
import check
import logging

from datetime import date

logger = logging.getLogger('alforria')

logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.ERROR)

def carrega_ch_professores(dir, S1INI, S2INI):

    # Caminho para o arquivo de configuracao dos caminhos de dados
    PATHS_PATH = '../config/paths.cnf'

    # A partir daqui, mudancas podem ocasionar problemas!

    # Le os caminhos onde se encontram os arquivos de dados

    GRUPOSPATH = dir
    PREFPATH = dir
    SARPATH = dir
    ATRIBPATH = dir
    FANTPATH = ''

    # Carrega os grupos de disciplinas
    grupos = []

    # Carrega os professores e suas preferencias e ajusta os valores dados
    # às preferências para que fiquem entre 0 e 10.
    professores = funcoes_leitura.ler_pref(PREFPATH,grupos,MAXIMPEDIMENTOS)
    for p in professores:
        p.ajustar()

    # Carrega as turmas de disciplinas do ano e elimina as disciplinas
    # fantasmas (turmas com números diferentes que são, na verdade, a
    # mesma turma)

    turmas = funcoes_leitura.ler_sar_csv(SARPATH,grupos)

    turmas = funcoes_leitura.caca_fantasmas(FANTPATH,turmas)

    # Carrega o arquivo de disciplinas pre-atribuidas
    pre_atribuidas = funcoes_leitura.ler_pre_atribuidas(ATRIBPATH,FANTPATH,professores,turmas)

    # Adiciona as pre atribuidas para o relatorio
    for (p, t) in pre_atribuidas:

        t.add_professor(p)
        p.add_course(t)

    return professores