#!/usr/bin/python
#coding=utf8

"""

Este script simplesmente le o SAR23 original e o converte em um arquivo muito mais amigavel e com informacoes mais uteis.

"""

import argparse

import alforria.funcoes_leitura as leitura
import alforria.funcoes_escrita as escrita

parser = argparse.ArgumentParser(
    description='Converte o SAR para csv')
parser.add_argument('-o', help='Arquivo de saida', default='sar.csv')
parser.add_argument('-i', help='Arquivo de entrada', default=None)
args = parser.parse_args()


def sar_to_csv():

    paths = leitura.ler_conf('../config/paths.cnf')

    SARPATH = paths['SARPATH'] if args.i == None else args.i
    GRUPOSPATH = paths['GRUPOSPATH']
    CURSOSPATH = paths['CURSOSPATH']

    grupos = leitura.ler_grupos(GRUPOSPATH)

    cursos = leitura.ler_curso_do_sar097(CURSOSPATH)

    turmas = leitura.ler_sar(SARPATH, grupos, cursos=cursos)

    escrita.sar_to_csv(turmas, args.o)
