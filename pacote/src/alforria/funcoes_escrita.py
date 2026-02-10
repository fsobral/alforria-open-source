import datetime
import os
import logging
import re

import pandas as pd

from . import funcoes_leitura as leitura

logger = logging.getLogger('alforria')

def gera_declaracao_ch_semestre(
    listah, s, dirh="/home/fsobral/GoogleDrive/Alforria/2024/horarios"
):
    """Assume que `s` é 'S1' ou 'S2' e `listah` é uma lista de inteiros que representam datas na forma YYYYMMDD, e que contem o primeiro dia de aula do semestre e o ultimo. Faz mais sentido arrendondar por semanas e sempre iniciar na segunda e terminar na segunda, para facilitar a vida. Lembrando que o número de semanas tem que dar 17

    Exemplo:

        listah([20240514, 20240527, 20240610, 20240708, 20240722, 20240805, 20240826, 20240909], 'S1')

    """

    # Calcula a quantidade de semanas entre cada data
    datas = sorted(listah)

    ch = [
        (
            (
                datetime.date.fromisoformat(str(datas[i + 1]))
                - datetime.date.fromisoformat(str(datas[i]))
            ).days
            + 1
        )
        // 7
        for i in range(0, len(datas) - 1)
    ]

    print("Numero de semanas total:", sum(ch))

    # Nao deveria existir pasta com a ultima semana
    v = datas[0:-1]

    # Junta todas as disciplinas que foram ministradas no intervalo dado
    dfdisc = (
        pd.concat(
            [
                pd.read_csv(
                    "{1:s}/{0:d}/atribuicoes.csv".format(d, dirh), sep=",", header=None
                )
                for d in v
            ]
        )
        .groupby([1, 2, 3, 6])
        .agg({4: "first"})
    )

    # Calcula a carga horária total

    soma_ch = pd.concat(
        [
            pd.read_csv(
                "{1:s}/{0:d}/atribuicoes.csv".format(d, dirh), sep=",", header=None
            ).set_index([1, 2, 3, 6])[5]
            * c
            for d, c in zip(v, ch)
        ],
        axis=1,
    )

    dfdisc.loc[:, "CH_MINISTRADA"] = soma_ch.sum(axis=1)

    return dfdisc.loc[:, :, :, s]


def sar_to_csv(turmas, outfile):
    """
    Converte a planilha SAR para um CSV.
    """

    with open(outfile, "w") as fp:
        for t in turmas:
            for h in t.horarios:
                fp.write(
                    "{cod:s},{turma:s},{nome:s},T,99,9,{horario[0]:d},{horario[1]:d},9,CAMPUS,BLOCO,9,{ch:.1f},{cht:.1f},S{semestre:d},{ini:%Y-%m-%d},{fim:%Y-%m-%d},{curso:s}\n".format(
                        cod=t.codigo,
                        turma=t.turma,
                        nome=t.nome,
                        horario=h,
                        ch=t.ch,
                        cht=(t.ch * 17),
                        semestre=t.semestralidade,
                        ini=t.dini,
                        fim=t.dend,
                        curso=t.curso,
                    )
                )


def write_ch_table(professor, diretorio, csv_name="ch_table.csv"):
    """
    Create a .csv file with the teaching hours in each semester for each professor.
    """

    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    with open(diretorio + csv_name, "w") as fp:
        for p in professor:
            fp.write(
                "{0:s},{1:d},{2:d}\n".format(
                    p.nome(), p._carga_horaria_s(1), p._carga_horaria_s(2)
                )
            )


def cria_relatorio(professor, diretorio):
    """
    Recebe um professor e cria um arquivo .tex com o seu relatorio.
    """

    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    with open("../config/base.tex", "r") as padrao:
        with open(diretorio + "relatorio_" + professor.nome() + ".tex", "w") as saida:
            professor.att_totex(diretorio + professor.nome() + ".tex")
            for l in padrao:
                saida.write(l)
            saida.write("\\include{" + professor.nome() + "}")
            saida.write("\\end{document}")


def cria_relatorio_geral(professores, diretorio):
    """
    Recebe uma lista de objetos do tipo Professor e constroi um arquivo .tex
    com todos os relatorios. Utiliza um arquivo chamado 'base.tex' como base
    para carregar os pacotes e similares.
    """

    if not os.path.exists(diretorio):
        os.makedirs(diretorio)

    count = 1
    with open("../config/base.tex", "r") as padrao:
        with open(diretorio + "relatorio_geral.tex", "w") as saida:
            for l in padrao:
                saida.write(l)
            for p in professores:
                p.totex(diretorio + str(count) + ".tex")
                saida.write("\\include{" + str(count) + "}\n")
                count += 1
            saida.write("\\end{document}")


####################################################################################################################
####################                  Funcao              escreve dat                      #########################
####################################################################################################################


def escreve_dat(professores, turmas, grupos, pre_atribuidas, arquivo):
    with open(arquivo, "w") as f:
        constantes = leitura.ler_conf("../config/constantes.cnf")

        for param in constantes:
            f.write("param " + param + " := " + constantes[param] + ";\n\n")

        f.write("set G := ")
        for g in grupos:
            f.write(g.id + " ")
        f.write(";\n\n")

        f.write("set G_CANONICOS := ")
        for g in grupos:
            if g.canonico:
                f.write(g.id + " ")
        f.write(";\n\n")

        f.write("set T := ")
        for t in turmas:
            f.write(t.id() + " ")
        f.write(";\n\n")

        f.write("set T_PRE := ")
        for p, t in pre_atribuidas:
            f.write(t.id() + " ")
        f.write(";\n\n")

        f.write("set P := ")
        for p in professores:
            f.write(p.id() + " ")
        f.write(";\n\n")

        # Vincula as turmas ao grupos
        f.write("param turma_grupo := \n")
        for t in turmas:
            if t.grupo is not None:
                f.write(t.id() + " " + t.grupo.id + " 1\n")
        f.write(";\n\n")

        # Supoe que se uma disciplina eh vinculada, seu vinculo eh a
        # disciplina seguinte
        f.write("param vinculadas := \n")
        vinc = False
        for t in turmas:
            if vinc:
                f.write(t.id() + " 1\n")
                vinc = False
            elif t.vinculada:
                f.write(t.id() + " ")
                vinc = True
        f.write(";\n\n")

        f.write("param c := \n")
        for t in turmas:
            for d, h in t.horarios:
                f.write(
                    t.id()
                    + " "
                    + str(t.semestralidade)
                    + " "
                    + str(d)
                    + " "
                    + str(h)
                    + " 1\n"
                )
        f.write(";\n\n")

        f.write("param ch := \n")
        for t in turmas:
            f.write(t.id() + " " + str(t.carga_horaria()) + "\n")
        f.write(";\n\n")

        f.write("param ch1 := \n")
        for t in turmas:
            f.write(t.id() + " ")
            if t.semestralidade == 1:
                f.write(str(t.carga_horaria()) + "\n")
            else:
                f.write("0\n")
        f.write(";\n\n")

        f.write("param ch2 := \n")
        for t in turmas:
            f.write(t.id() + " ")
            if t.semestralidade == 2:
                f.write(str(t.carga_horaria()) + "\n")
            else:
                f.write("0\n")
        f.write(";\n\n")

        f.write("param temporario := \n")
        for p in professores:
            if p.temporario:
                f.write(p.id() + " 1\n")
        f.write(";\n\n")

        f.write("param inapto := \n")
        for p in professores:
            for g in p.inapto:
                f.write(p.id() + " " + g + " 1\n")
        f.write(";\n\n")

        f.write("param impedimento := \n")
        for p in professores:
            for d in range(2, 8):
                for h in range(1, 17):
                    if p.impedimentos[h][d]:
                        for s in range(1, 3):
                            f.write(
                                p.id()
                                + " "
                                + str(s)
                                + " "
                                + str(d)
                                + " "
                                + str(h)
                                + " 1\n"
                            )
        f.write(";\n\n")

        f.write("param pref_janelas := \n")
        for p in professores:
            if p.pref_janelas:
                f.write(p.id() + " 1\n")
        f.write(";\n\n")

        f.write("param pref_grupo := \n")
        for p in professores:
            for g in p.pref_grupos.keys():
                f.write(p.id() + " " + g + " " + str(p.pref_grupos[g]) + "\n")
        f.write(";\n\n")

        f.write("param pref_hor := \n")
        for p in professores:
            for d in range(2, 8):
                for h in range(1, 17):
                    f.write(
                        p.id()
                        + " "
                        + str(d)
                        + " "
                        + str(h)
                        + " "
                        + str(p.pref_horarios[h, d])
                        + "\n"
                    )
        f.write(";\n\n")

        f.write("param pre_atribuida :=\n")
        for p, t in pre_atribuidas:
            f.write(p.id() + " " + t.id() + " 1\n")
        f.write(";\n\n")

        f.write("param chprevia1 :=\n")
        for p in professores:
            if p.chprevia1 > 0:
                f.write(p.id() + " " + str(p.chprevia1) + "\n")
        f.write(";\n\n")

        f.write("param chprevia2 :=\n")
        for p in professores:
            if p.chprevia2 > 0:
                f.write(p.id() + " " + str(p.chprevia2) + "\n")
        f.write(";\n\n")

        f.write("param licenca :=\n")
        for p in professores:
            if p.licenca1:
                f.write(p.id() + " 1 1\n")
            if p.licenca2:
                f.write(p.id() + " 2 1\n")
        f.write(";\n\n")

        f.write("param peso_disciplinas := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_disciplinas) + "\n")
        f.write(";\n\n")

        f.write("param peso_horario := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_horario) + "\n")
        f.write(";\n\n")

        f.write("param peso_cargahor := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_cargahor) + "\n")
        f.write(";\n\n")

        f.write("param peso_distintas := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_distintas) + "\n")
        f.write(";\n\n")

        f.write("param peso_janelas := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_janelas) + "\n")
        f.write(";\n\n")

        f.write("param peso_numdisc := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_numdisc) + "\n")
        f.write(";\n\n")

        f.write("param peso_manha_noite := \n")
        for p in professores:
            f.write(p.id() + " " + str(p.peso_manha_noite) + "\n")
        f.write(";\n\n")

        f.write("param chmax := \n")
        for p in professores:
            if p.chmax != None:
                f.write(p.id() + " " + str(p.chmax) + "\n")
        f.write(";\n\n")

        f.write("param chmax1 := \n")
        for p in professores:
            if p.chmax1 != None:
                f.write(p.id() + " " + str(p.chmax1) + "\n")
        f.write(";\n\n")

        f.write("param chmax2 := \n")
        for p in professores:
            if p.chmax2 != None:
                f.write(p.id() + " " + str(p.chmax2) + "\n")
        f.write(";\n\nend;\n")


####################################################################################################################
####################                  Funcao              escreve atribuicoes              #########################
####################################################################################################################


def escreve_pre_atribuidas(professores, turmas, arquivo):
    """
    Esta funcao simplesmente salva a atribuicao atual.
    """

    with open(arquivo, "w") as f:
        for p in professores:
            for t in p.turmas_a_lecionar:
                # TODO: trocar p.matricula por p.id()
                sem = "S" + str(t.semestralidade)

                f.write(
                    "{matricula:08d}\t{nome:s}\t{cod:s}\t{turma:s}\t{tnome:s}\t{ch:d}\t{sem:s}\t{curso:s}\n".format(
                        matricula=p.matricula,
                        nome=p.nome(),
                        cod=t.codigo,
                        turma=t.turma,
                        tnome=t.nome,
                        ch=t.carga_horaria(),
                        sem=sem,
                        curso=t.curso,
                    )
                )


def escreve_atribuicoes(professores, turmas, arquivo):
    """This function writes in a CSV file 'arquivo' the relation of
    courses attributed to each professor.

    """

    with open(arquivo, "w") as f:
        for p in professores:
            for t in p.turmas_a_lecionar:
                # TODO: Codigo virar numero e nao texto
                if t.codigo.find("666") == 0:
                    continue

                # TODO: trocar p.matricula por p.id()
                sem = "S" + str(t.semestralidade)
                # Agora permitimos disciplinas anuais desvinculadas
                # if t.vinculada and t.semestralidade == 1:
                #     sem = 'A'
                # if t.vinculada and t.semestralidade == 2:
                #     continue
                f.write(
                    "{matricula:08d},{nome:s},{cod:s},{turma:s},{tnome:s},{ch:d},{sem:s},{curso:s}\n".format(
                        matricula=p.matricula,
                        nome=p.nome(),
                        cod=t.codigo,
                        turma=t.turma,
                        tnome=t.nome,
                        ch=t.carga_horaria(),
                        sem=sem,
                        curso=t.curso,
                    )
                )
                # f.write(str(p.matricula) + '\t' + p.nome() + '\t' + str(t.codigo) + '\t' + \
                #         str(t.turma) + '\t' + t.nome + '\t' + str(t.carga_horaria()) + \
                #         '\t' + sem + '\n')
                # TODO: trocar p.matricula por p.id()
                # for fant in t.turmas_clientes:
                #     f.write(str(p.matricula) + '\t' + p.nome() + '\t' + str(fant.codigo) + '\t' + \
                #             str(fant.turma) + '\t' + fant.nome + '\t' + str(fant.carga_horaria()) + \
                #             '\tS' + str(t.semestralidade) + '\n')


####################################################################################################################
####################                  Funcao              escreve disciplinas              #########################
####################################################################################################################


def escreve_disciplinas(professores, turmas, arquivo):
    with open(arquivo, "w") as f:
        for t in sorted(turmas, key=lambda x: int(x.codigo)):
            f.write(
                "{cod:s},{turma:s},{tnome:s},{nome:s},S{sem:s},{anual:s}\n".format(
                    cod=t.codigo,
                    turma=t.turma,
                    tnome=t.nome,
                    nome="" if t.professor is None else t.professor.nome(),
                    sem=str(t.semestralidade),
                    anual=("*" if t.vinculada else ""),
                )
            )
            # f.write(t.nome + '\t' + str(t.codigo) + '\t' + str(t.turma) + '\t')
            # for p in professores:
            #     if t in p.turmas_a_lecionar:
            #         f.write(p.nome())
            # f.write('\t' + str(t.carga_horaria()) + '\t' + 'S' + str(t.semestralidade))
            # f.write('\n')

            # Removidas as fantasmas
            # for fant in t.turmas_clientes:
            #     f.write(fant.nome + '\t' + str(fant.codigo) + '\t' + str(fant.turma) + '\t')
            #     for p in professores:
            #         if t in p.turmas_a_lecionar:
            #             f.write(p.nome())
            #     f.write('\t' + str(t.carga_horaria()) + '\t' + 'S' + str(t.semestralidade))
            #     f.write('\n')


####################################################################################################################
####################                  Funcao              atualiza dat2                    #########################
####################################################################################################################


def atualiza_dat2(professores, arquivo):
    """
    Esta funcao serve para remover professores e preparar para
    uma nova rodada. A ser incluida na nova versao do alforria
    """

    listap = []

    # Leitura dos professores ja excluidos

    try:

        with open(arquivo, "r") as f:
            l = f.readline().split()

            if len(l) > 3:
                for nome in l[3:]:
                    for p in professores:
                        if p.nome() == nome:
                            listap.append(p)

    except FileNotFoundError:

        logger.debug("\tatualiza_jl: file not found.")

    professores.sort(key=lambda x: x.insatisfacao, reverse=True)

    # Procura o proximo insatisfeito que nao foi excluido

    i = 0
    while (i < len(professores)) and (professores[i] in listap):
        i = i + 1

    maxinsat = -100
    if i < len(professores):
        maxinsat = professores[i].insatisfacao
        listap.append(professores[i])

    # Gera o novo arquivo

    logger.info("Professores retirados da funcao objetivo:")
    for p in listap:
        logger.info("\t{0:50s} insat: {1:10.7f}".format(p.nome(), p.insatisfacao))

    with open(arquivo, "w") as f:
        f.write("set P_OUT :=")
        for p in listap:
            f.write(" " + p.nome())
        f.write(" ;\n\n")

        f.write("param ub_insat :=\n")
        for p in listap:
            f.write(p.nome() + " " + str(max(maxinsat, p.insatisfacao)) + "\n")
        f.write(";\n\n")

    # Antes de sair, ordena os professores por nome
    professores.sort(key=lambda x: x.nome())


def atualiza_jl(professores, arquivo):
    """
    Esta funcao serve para remover professores muito insatisfeitos e preparar para
    uma nova rodada.
    """

    listap = []

    # Leitura dos professores ja excluidos

    # Assume that this file is a single line
    # P_OUT :: Set{String} = Set([ "T1", "T2", ..., "TN"])

    try:

        with open(arquivo, "r") as f:
            l = f.readline()

            nomes = [re.match(r'"([^"]+)"', r)[1] for r in re.findall(r'"[^"]+"', l)]

            logger.debug("\tatualiza_jl: found %d names", len(nomes))

            for nome in nomes:
                for p in professores:
                    if p.nome() == nome:
                        listap.append(p)
                        break
    
    except FileNotFoundError:

        logger.debug("\tatualiza_jl: file not found.")


    professores.sort(key=lambda x: x.insatisfacao, reverse=True)

    # Procura o proximo insatisfeito que nao foi excluido

    i = 0
    while (i < len(professores)) and (professores[i] in listap):
        i = i + 1

    maxinsat = -100
    if i < len(professores):
        maxinsat = professores[i].insatisfacao
        listap.append(professores[i])

    # Gera o novo arquivo

    logger.info("\tProfessores retirados da funcao objetivo:")
    for p in listap:
        logger.info("\t{0:50s} insat: {1:10.7f}".format(p.nome(), p.insatisfacao))

    with open(arquivo, "w") as f:
        f.write("P_OUT :: Set{String}([")

        for p in listap[0:-1]:
            f.write('"{0:s}", '.format(p.nome()))

        f.write('"{0:s}"])\n\n'.format(listap[-1].nome()))

        f.write("ub_insat :: Dict{String, Float64} = Dict(\n")

        for p in listap[0:-1]:

            f.write('\t"{0:s} => {1:3.5f},\n'.format(p.nome(), max(maxinsat, p.insatisfacao)))

        else:

            p = listap[-1]
            f.write('\t"{0:s} => {1:3.5f}\n'.format(p.nome(), max(maxinsat, p.insatisfacao)))

        f.write(")\n")

    # Antes de sair, ordena os professores por nome
    professores.sort(key=lambda x: x.nome())

####################################################################################################################
####################                  Funcao              escreve jl                       #########################
####################################################################################################################


def escreve_jl(professores, turmas, grupos, pre_atribuidas, arquivo):
    with open(arquivo, "w") as f:
        constantes = leitura.ler_conf("../config/constantes.cnf")

        for param in constantes:
            f.write(param + " = " + constantes[param] + "\n\n")

        f.write("G :: Set{String} = Set{String}([\n\n")
        for g in grupos:
            f.write(f'\t"{g.id}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("G_CANONICOS :: Set{String} = Set{String}([")
        for g in grupos:
            if g.canonico:
                f.write(f'\t"{g.id}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("T :: Set{String} = Set{String}([")
        for t in turmas:
            f.write(f'\t"{t.id()}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("T_PRE :: Set{String} = Set{String}([")
        for p, t in pre_atribuidas:
            f.write(f'\t"{t.id()}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("P :: Set{String} = Set{String}([")
        for p in professores:
            f.write(f'\t"{p.id()}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        # Vincula as turmas ao grupos
        f.write("turma_grupo :: Dict{String, String} = Dict(\n")
        for t in turmas:
            if t.grupo is not None:
                f.write(f'\t"{t.id()}" => "{t.grupo.id}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        # Supoe que se uma disciplina eh vinculada, seu vinculo eh a
        # disciplina seguinte
        f.write(
            "vinculadas :: Set{Tuple{String, String}} = Set{Tuple{String,String}}([\n"
        )
        vinc = False
        for t in turmas:
            if vinc:
                f.write(f'"{t.id()}"),\n')
                vinc = False
            elif t.vinculada:
                f.write(f'\t("{t.id()}", ')
                vinc = True
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("c :: Set{Tuple{String, Int64, Int64, Int64}} =\n")
        f.write("Set{Tuple{String, Int64, Int64, Int64}}([")
        for t in turmas:
            for d, h in t.horarios:
                f.write(f'\t("{t.id()}", {t.semestralidade}, {d}, {h}),\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("ch :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for t in turmas:
            f.write(f'\t"{t.id()}" => {t.carga_horaria()},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("ch1 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for t in turmas:
            f.write(f'\t"{t.id()}" => ')
            if t.semestralidade == 1:
                f.write(f"{t.carga_horaria()},\n")
            else:
                f.write("0,\n")
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("ch2 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for t in turmas:
            f.write(f'\t"{t.id()}" => ')
            if t.semestralidade == 2:
                f.write(f"{t.carga_horaria()},\n")
            else:
                f.write("0,\n")
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("temporario :: Set{String} = Set{String}([\n")
        for p in professores:
            if p.temporario:
                f.write(f'\t"{p.id()}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("inapto :: Set{Tuple{String, String}} = Set{Tuple{String, String}}([\n")
        for p in professores:
            for g in p.inapto:
                f.write(f'\t("{p.id()}", "{g}")\n')
        f.seek(f.tell() - 1, 0)
        f.write("\n])\n\n")

        f.write("impedimento :: Set{Tuple{String, Int64, Int64, Int64}} = \n")
        f.write("Set{Tuple{String, Int64, Int64, Int64}}([\n")
        for p in professores:
            for d in range(2, 8):
                for h in range(1, 17):
                    if p.impedimentos[h][d]:
                        for s in range(1, 3):
                            f.write(f'\t("{p.id()}", {s}, {d}, {h})\n')
        f.seek(f.tell() - 1, 0)
        f.write("\n])\n\n")

        f.write("pref_janelas :: Set{String} = Set{String}([\n")
        for p in professores:
            if p.pref_janelas:
                f.write(f'\t"{p.id()}",\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("pref_grupo :: Dict{Tuple{String, String}, Float16} =\n")
        f.write("Dict{Tuple{String, String}, Float16}(\n")
        for p in professores:
            for g in p.pref_grupos.keys():
                f.write(f'\t("{p.id()}", "{g}") => {p.pref_grupos[g]},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("pref_hor :: Dict{Tuple{String, Int64, Int64}, Float16} =\n")
        f.write("Dict{Tuple{String, Int64, Int64}, Float16}(\n")
        for p in professores:
            for d in range(2, 8):
                for h in range(1, 17):
                    f.write(f'\t("{p.id()}", {d}, {h}) => {p.pref_horarios[h, d]},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("pre_atribuida :: Set{Tuple{String, String}} =\n")
        f.write("Set{Tuple{String, String}}([\n")
        for p, t in pre_atribuidas:
            f.write(f'\t("{p.id()}", "{t.id()}"),\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n])\n\n")

        f.write("chprevia1 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for p in professores:
            if p.chprevia1 > 0:
                f.write(f'\t"{p.id()}" => {p.chprevia1},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("chprevia2 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for p in professores:
            if p.chprevia2 > 0:
                f.write(f'\t"{p.id()}" => {p.chprevia2},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("licenca :: Set{Tuple{String, Int64}} = Set{Tuple{String, Int64}}([\n")
        for p in professores:
            if p.licenca1:
                f.write(f'\t("{p.id()}", 1)\n')
            if p.licenca2:
                f.write(f'\t("{p.id()}", 2)\n')
        f.seek(f.tell() - 1, 0)
        f.write("\n])\n\n")

        f.write("peso_disciplinas :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_disciplinas},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_horario  :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_horario},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_cargahor :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_cargahor},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_distintas :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_distintas},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_janelas :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_janelas},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_numdisc :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_numdisc},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("peso_manha_noite :: Dict{String, Float16} = Dict{String, Float16}(\n")
        for p in professores:
            f.write(f'\t"{p.id()}" => {p.peso_manha_noite},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("chmax :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for p in professores:
            if p.chmax != None:
                f.write(f'\t"{p.id()}" => {p.chmax},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("chmax1 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for p in professores:
            if p.chmax1 != None:
                f.write(f'\t"{p.id()}" => {p.chmax1},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")

        f.write("chmax2 :: Dict{String, Int64} = Dict{String, Int64}(\n")
        for p in professores:
            if p.chmax2 != None:
                f.write(f'\t"{p.id()}" => {p.chmax2},\n')
        f.seek(f.tell() - 2, 0)
        f.write("\n)\n\n")
