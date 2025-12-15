#!/usr/bin/python
# coding=utf8

import funcoes_leitura as leitura
import funcoes_escrita as escrita
import check
import argparse
import logging


# Carrega os argumentos

parser = argparse.ArgumentParser(
    description='Verifica os dados e gera preferencias')
parser.add_argument('-p', help='Gera um arquivo .tex com as preferencias' +
                    'no diretorio RELDIR definido em alforria.cnf',
                    action='store_true')
parser.add_argument('-d', help='Gera um arquivo CSV com as disciplinas e ' +
                    'professor que ira ministra-la', action='store_true')
parser.add_argument('-a', help='Gera um arquivo CSV com as atribuicoes de ' +
                    'cada professor', action='store_true')
parser.add_argument('-v', help='Nivel de saida desejado. Quanto mais v\'s ' +
                    'maior a quantidade de informacao.', action='count')
parser.add_argument('-f', help='Versao final', action='store_true')

parser.add_argument('dir', help="Caminhos para arquivos de configuracao.",
                    nargs=2)

args = parser.parse_args()


# Configura nivel de saida

logger = logging.getLogger('alforria')

logger.addHandler(logging.StreamHandler())

if args.v is None or args.v == 0:

    logger.setLevel(logging.ERROR)

elif args.v is 1:

    logger.setLevel(logging.INFO)

else:

    logger.setLevel(logging.DEBUG)


l_prof = []
l_turm = []

for d in args.dir:

    paths = leitura.ler_conf(d)

    GRUPOSPATH = paths['GRUPOSPATH']
    PREFPATH = paths['PREFPATH']
    SARPATH = paths['SARPATH']
    ATRIBPATH = paths['ATRIBPATH']
    FANTPATH = paths['FANTPATH']
    DATPATH = paths['DATPATH']
    SOLPATH = paths['SOLPATH']

    configuracoes = leitura.ler_conf('../config/alforria.cnf')

    MAXIMPEDIMENTOS = int(configuracoes['MAXIMPEDIMENTOS'])
    RELDIR = configuracoes['RELDIR']

    # Carrega os grupos de disciplinas
    grupos = leitura.ler_grupos(GRUPOSPATH)

    # Carrega os professores e suas preferencias
    professores = leitura.ler_pref(PREFPATH, grupos, MAXIMPEDIMENTOS)
    for p in professores:
        p.ajustar()

    # Carrega as turmas de disciplinas do ano

    turmas = leitura.ler_sar(SARPATH, grupos)

    turmas = leitura.caca_fantasmas(FANTPATH, turmas)

    # Carrega o arquivo de disciplinas pre-atribuidas
    pre_atribuidas = leitura.ler_pre_atribuidas(ATRIBPATH, FANTPATH,
                                                professores, turmas)

    # Adiciona as pre atribuidas para o relatorio
    for (p, t) in pre_atribuidas:

        p.turmas_a_lecionar.append(t)

    l_prof.append(sorted(professores, key=lambda x: x.nome()))


    # Grava disciplinas com seus professores
    set_t = set(turmas)

    for p in professores:

        map(set_t.add, p.turmas_a_lecionar)

    l_turm.append(turmas)
    

# Verifica professor a professor
        
profs1 = l_prof[0]
turma1 = l_turm[0]

profs2 = l_prof[1]
turma2 = l_turm[1]

for p in profs1:

    if p in profs2:

        print("Encontrou professor " + p.nome() + " no outro.")

    else:

        print("Nao encontrou professor " + p.nome() + " no outro.")
