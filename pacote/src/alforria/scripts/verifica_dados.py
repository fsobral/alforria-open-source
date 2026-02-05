#!/usr/bin/python3
# coding=utf8

import alforria.funcoes_leitura as leitura
import alforria.funcoes_escrita as escrita
from alforria import check
import argparse
import logging

from datetime import date

# Carrega os argumentos

parser = argparse.ArgumentParser(
    description='Verifica os dados e gera preferencias')
parser.add_argument('-p', help='Gera um arquivo .tex com as preferencias' +
                    'no diretorio RELDIR definido em alforria.cnf',
                    action='store_true')
parser.add_argument('-s', help='Gera um arquivo .tex apenas com as' +
                    'atribuicoes no diretorio RELDIR definido em alforria.cnf',
                    action='store_true')
parser.add_argument('-d', help='Gera um arquivo CSV com as disciplinas e ' +
                    'professor que ira ministra-la', action='store_true')
parser.add_argument('-a', help='Gera um arquivo CSV com as atribuicoes de ' +
                    'cada professor', action='store_true')
parser.add_argument('-v', help='Nivel de saida desejado. Quanto mais v\'s ' +
                    'maior a quantidade de informacao.', action='count')
parser.add_argument('-f', help='Versao final', action='store_true')
parser.add_argument('-g', help='Verifica grupos (necessita -v)',
                    action='store_true')

args = parser.parse_args()


# Configura nivel de saida

logger = logging.getLogger('alforria')

logger.addHandler(logging.StreamHandler())

def verifica():

    if args.v is None or args.v == 0:

        logger.setLevel(logging.ERROR)

    elif args.v == 1:

        logger.setLevel(logging.INFO)

    else:

        logger.setLevel(logging.DEBUG)


    # Le os caminhos onde se encontram os arquivos de dados

    paths = leitura.ler_conf('../config/paths.cnf')

    GRUPOSPATH = paths['GRUPOSPATH']
    PREFPATH = paths['PREFPATH']
    SARPATH = paths['SARPATH']
    ATRIBPATH = paths['ATRIBPATH']
    FANTPATH = paths['FANTPATH']
    DATPATH = paths['DATPATH']
    SOLPATH = paths['SOLPATH']

    # Carrega o arquivo de configuracoes do programa. Nesse caso pega o
    # numero maximo de impedimentos que estao no programa e o nome do
    # diretorio de criacao dos relatorios.

    configuracoes = leitura.ler_conf('../config/alforria.cnf')

    MAXIMPEDIMENTOS = int(configuracoes['MAXIMPEDIMENTOS'])
    RELDIR = configuracoes['RELDIR']
    S1INI = date.fromisoformat(configuracoes['SEM1_INI'])
    S2INI = date.fromisoformat(configuracoes['SEM2_INI'])

    # Carrega os grupos de disciplinas
    grupos = leitura.ler_grupos(GRUPOSPATH)

    # Carrega os professores e suas preferencias e ajusta os valores dados
    # às preferências para que fiquem entre 0 e 10.
    professores = leitura.ler_pref(PREFPATH, grupos, MAXIMPEDIMENTOS)
    for p in professores:
        p.ajustar()

    # Carrega as turmas de disciplinas do ano e elimina as disciplinas
    # fantasmas (turmas com números diferentes que são, na verdade, a
    # mesma turma)

    turmas = leitura.ler_sar_csv(SARPATH, grupos)

    if args.g:

        check.check_g(turmas)
        
    turmas = leitura.caca_fantasmas(FANTPATH, turmas)

    # Carrega o arquivo de disciplinas pre-atribuidas
    pre_atribuidas = leitura.ler_pre_atribuidas(ATRIBPATH, FANTPATH,
                                                professores, turmas)

    chtotal = 0

    for t in turmas:
        chtotal += t.carga_horaria()

    # Verifica inconsistencias, elimina professores com carga horaria
    # completamente atribuida, da avisos de possiveis problemas,
    # etc. Guarda os professores que sao automaticamente removidos.
    p_fantasmas = check.checkdata(professores, turmas, pre_atribuidas, S1INI, S2INI,
                                FANTPATH)

    professores.extend(p_fantasmas)

    # Adiciona as pre atribuidas para o relatorio
    for (p, t) in pre_atribuidas:

        t.add_professor(p)
        p.add_course(t)

    prof_ord = sorted(professores, key=lambda x: x.nome())

    ch_1 = 0
    ch_2 = 0

    for p in prof_ord:

        for t in p.turmas_a_lecionar:

            if t.semestralidade == 1:

                ch_1 += t.carga_horaria()

            else:

                ch_2 += t.carga_horaria()

        for t in p.turmas_a_lecionar:

            t.professor = p

    if args.f:

        check.check_nao_atribuidas(turmas)

    logger.info("\nCarga horaria total graduacao (sem fantasmas): " + str(chtotal))
    logger.info("\tAtribuida 1Sem: " + str(ch_1))
    logger.info("\tAtribuida 2Sem: " + str(ch_2))
    logger.info("\tDeficit: " + str(chtotal - ch_1 - ch_2))

    # Gera o arquivo de preferencias, caso tal opcao tenha sido solicitada

    if args.p:

        escrita.cria_relatorio_geral(prof_ord, RELDIR)

    if args.s:

        for p in prof_ord:
        
            escrita.cria_relatorio(p, RELDIR)
        
    if args.d:

        # Reconstroi as turmas removidas no check

        for p in p_fantasmas:

            turmas.extend(p.turmas_a_lecionar)

        escrita.escreve_disciplinas(prof_ord, turmas, RELDIR + 'disciplinas.csv')

    if args.a:

        escrita.escreve_atribuicoes(prof_ord, turmas,
                                    RELDIR + 'atribuicoes.csv')
