#!/usr/bin/python
#coding=utf8

""".

ANTES.PY

Este script e' rodado antes do problema de otimizacao. Sua funcao e'
ler todos os dados, limpa-los e construir o arquivo .DAT que sera
usado no modelo de otimizacao.

Utiliza alguns arquivos e configuracoes. Caso modifique alguma coisa,
mexa nas variaveis abaixo

"""

from .. import funcoes_leitura, funcoes_escrita, check

import logging
import argparse

from datetime import date

# Carrega os argumentos

parser = argparse.ArgumentParser(
    description='Script para ser rodado antes da otimização.')
parser.add_argument('tipo', help='Tipo de modelo a ser gerado: MathProg (.mod) ou JuMP (.jl)',
                    choices=['mod', 'jl'])

args = parser.parse_args()


def antes():

    logger = logging.getLogger('alforria')

    logger.setLevel(logging.ERROR)

    # Caminho para o arquivo de configuracao dos caminhos de dados
    PATHS_PATH = '../config/paths.cnf'

    # A partir daqui, mudancas podem ocasionar problemas!

    # Le os caminhos onde se encontram os arquivos de dados

    paths = funcoes_leitura.ler_conf(PATHS_PATH)

    GRUPOSPATH = paths['GRUPOSPATH']
    PREFPATH = paths['PREFPATH']
    SARPATH = paths['SARPATH']
    ATRIBPATH = paths['ATRIBPATH']
    FANTPATH = paths['FANTPATH']
    DATPATH = paths['DATPATH']
    SOLPATH = paths['SOLPATH']

    # Carrega o arquivo de configuracoes do programa. Nesse caso pega
    # apenas o numero maximo de impedimentos que estao no programa.

    configuracoes = funcoes_leitura.ler_conf('../config/alforria.cnf')

    MAXIMPEDIMENTOS = int(configuracoes['MAXIMPEDIMENTOS'])
    S1INI = date.fromisoformat(configuracoes['SEM1_INI'])
    S2INI = date.fromisoformat(configuracoes['SEM2_INI'])

    # Carrega os grupos de disciplinas
    grupos = funcoes_leitura.ler_grupos(GRUPOSPATH)

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

    # Verifica inconsistencias, elimina professores com carga horaria
    # completamente atribuida, da avisos de possiveis problemas, etc.
    check.checkdata(professores,turmas,pre_atribuidas,S1INI,S2INI,FANTPATH)

    # Gera o arquivo .DAT, necessario para o modelo de otimizacao
    if args.tipo == 'mod':

        funcoes_escrita.escreve_dat(professores,turmas,grupos,pre_atribuidas,DATPATH + '.dat')

    elif args.tipo == 'jl':

        funcoes_escrita.escreve_jl(professores,turmas,grupos,pre_atribuidas,DATPATH + '.jl')

    # Estatisticas finais
    check.estatisticas(professores,turmas)
