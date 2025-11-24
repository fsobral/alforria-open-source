#!/usr/bin/python
#coding=utf8

"""

Este script simplesmente le todos os arquivos necessarios e gera o
relatorio com as preferencias e disciplinas pre-atribuidas

"""

import funcoes_leitura as leitura
import funcoes_escrita as escrita
import check

paths = leitura.ler_conf('../config/paths.cnf')

GRUPOSPATH = paths['GRUPOSPATH']
PREFPATH = paths['PREFPATH']
SARPATH = paths['SARPATH']
ATRIBPATH = paths['ATRIBPATH']
FANTPATH = paths['FANTPATH']

configuracoes = leitura.ler_conf('../config/alforria.cnf')

MAXIMPEDIMENTOS = int(configuracoes['MAXIMPEDIMENTOS'])
RELDIR = configuracoes['RELDIR']

grupos = leitura.ler_grupos(GRUPOSPATH)

professores = leitura.ler_pref(PREFPATH,grupos,MAXIMPEDIMENTOS)
for p in professores:
    p.ajustar()

turmas = leitura.ler_sar(SARPATH,grupos)

turmas = leitura.caca_fantasmas(FANTPATH,turmas)

pre_atribuidas = leitura.ler_pre_atribuidas(ATRIBPATH,FANTPATH,professores,turmas)

pre_atribuidas = leitura.ler_pre_atribuidas(ATRIBPATH,FANTPATH,professores,turmas)

# Remove algumas inconsistencias
p_fantasmas = check.checkdata(professores,turmas,pre_atribuidas,FANTPATH)

# Atribui as pre-atribuidas aos seus respectivos professores
for p in professores:
    p.carga_horaria = p.chprevia1 + p.chprevia2
    for (p1,t1) in [(p2,t2) for (p2,t2) in pre_atribuidas if p2 == p]:
        p.turmas_a_lecionar.append(t1)
        p.carga_horaria += t1.carga_horaria()

professores.extend(p_fantasmas)

professores.sort(key = lambda x: x.nome())

check.estatisticas(professores,turmas)

escrita.cria_relatorio_geral(professores,RELDIR)
