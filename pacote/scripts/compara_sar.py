#!/usr/bin/python3
#coding=utf8

import funcoes_leitura as leitura
import funcoes_escrita as escrita
import check
import argparse

parser = argparse.ArgumentParser(description = \
                                 'Compara dois SARs de anos distintos')
parser.add_argument('files', help = 'Caminho completo para cada um dos ' \
                    'SARs em formato txt', nargs = 2)

args = parser.parse_args()

# Le os caminhos onde se encontram os arquivos de dados

turmas1 = leitura.ler_sar_csv(args.files[0], [])

turmas2 = leitura.ler_sar_csv(args.files[1], [])

# Compara dois ensalamentos

for t1 in turmas1:
    existe = False
    for t2 in turmas2:
        if t1.id() == t2.id():
            existe = True
            if len( [(d,h) for (d,h) in t1.horarios \
                     if (d,h) not in t2.horarios] ) > 0:
                print(t1.id() + " " + t1.nome + \
                      " com horarios diferentes nos SARs.")
                print("\t" + str(t1))
                print("\t" + str(t2))
            elif t1.carga_horaria() != t2.carga_horaria():
                print(t1.id() + " " + t1.nome + \
                      " com cargas horárias diferentes nos SARs.")
                print("\t" + str(t1))
                print("\t" + str(t2))

    if not existe:
        print(t1.id() + " " + t1.nome + " nao encontrada no segundo SAR.")
