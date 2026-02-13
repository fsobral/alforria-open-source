# coding=utf8

import re
from datetime import date

import numpy
import pandas as pd

from . import classes, funcoes_gerais

import logging

logger = logging.getLogger('alforria')

def sar292_to_df(sarfile):
    rx = re.compile(
        r"^[\s]*[\d]{1,3}[\s]*2024[\s]*DMA[\s]*([\d]{3,5})[\s]*([\d]{1,3})[^\d]+([\d]{1,3})"
    )

    with open(sarfile, "r") as fp:
        for l in fp:
            m = rx.match(l)

            if m != None:
                entries.append([])

    return pd.DataFrame(
        entries, columns=["curso", "codigo", "turma", "matriculados", "professor"]
    )


def ler_curso_do_sar097(sarfile):
    """
    Le um arquivo txt convertido de um SAR097 e devolve um dicionario codigo -> curso.
    """

    rx = re.compile(r"^[\s]*([\d]{3,5}) ([\d]{3})")
    rxc = re.compile(r" [\d]{1,2} ([^\d]+)")

    d = {}

    with open(sarfile, "r") as fp:
        for l in fp:
            m = rx.match(l)

            if m != None:
                c = m[1]
                t = m[2]

                curso = rxc.search(l)[1].strip()

                if c not in d:
                    d[c] = curso

                # print("{cod:6s} {turma:3s} {curso:20s}".format(cod=c, turma=t, curso=curso))

    return d


####################################################################################################################
####################                  Funcao              caca_fantasmas                   #########################
####################################################################################################################
# Remove os fantasmas da lista turmas
def caca_fantasmas(arquivo, turmas):
    with open(arquivo, "r") as fonte:
        print("\nRemovendo disciplinas fantasmas")
        print("-------------------------------\n")

        for num_linha, linha in enumerate(fonte, 1):
            fantasma = linha.split("\t")
            fantasma_inexistente = True
            i = 0

            while i < len(turmas):
                if int(turmas[i].codigo) == int(fantasma[0]) and int(
                    turmas[i].turma
                ) == int(fantasma[1]):
                    print("Turma " + turmas[i].id() + " removida")
                    del turmas[i]
                    fantasma_inexistente = False
                else:
                    i += 1
            if fantasma_inexistente:
                print(
                    "\nAVISO: Linha "
                    + str(num_linha)
                    + " - Este fantasma nao existe:"
                    + fantasma[0]
                    + "_"
                    + fantasma[1]
                    + ".\n"
                )
    return turmas


def ler_solucao_gurobi_jump(professores, turmas, arquivo):
    with open(arquivo, "r") as fonte:
        for linha in fonte:
            # Pula as linhas que nao setam variaveis
            if not "[" in linha:
                continue

            a = re.split(r"[\[\]]", linha)

            b = a[1].split(",")
            professor = b[0]
            variavel = a[0]

            if variavel == "carga_horaria":
                for p in professores:
                    if p.nome() == professor:
                        p.carga_horaria = float(linha.split()[-1])
            elif variavel == "x":
                turmaid = b[1].strip("'")
                if float(a[-1].strip()) > 0.9:
                    for t in turmas:
                        if t.id() == turmaid:
                            break
                    for p in professores:
                        if p.nome() == professor:
                            p.turmas_a_lecionar.append(t)
                            break
            elif variavel == "insat":
                for p in professores:
                    if p.nome() == professor:
                        p.insatisfacao = float(linha.split()[-1])
            elif variavel == "insat_disciplinas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_disciplinas = float(linha.split()[-1])
            elif variavel == "insat_cargahor":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_cargahor = float(linha.split()[-1])
            elif variavel == "insat_numdisc":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_numdisc = float(linha.split()[-1])
            elif variavel == "insat_horario":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_horario = float(linha.split()[-1])
            elif variavel == "insat_distintas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_distintas = float(linha.split()[-1])
            elif variavel == "insat_manha_noite":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_manha_noite = float(linha.split()[-1])
            elif variavel == "insat_janelas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_janelas = float(linha.split()[-1])


####################################################################################################################
####################    Funcao                 ler_solucao              e auxiliares      #########################
####################################################################################################################
def ler_solucao(professores, turmas, arquivo):
    with open(arquivo, "r") as fonte:
        for linha in fonte:
            # Pula as linhas que nao setam variaveis
            if not "(" in linha:
                continue

            a = re.split(r"[\[\]]", linha)

            b = a[1].split(",")
            professor = b[0]
            variavel = a[0]

            if variavel == "carga_horaria":
                for p in professores:
                    if p.nome() == professor:
                        p.carga_horaria = float(linha.split()[-1])
            elif variavel == "x":
                turmaid = b[1].strip("'")
                if float(a[-1].strip()) > 0.9:
                    for t in turmas:
                        if t.id() == turmaid:
                            break
                    for p in professores:
                        if p.nome() == professor:
                            p.add_course(t)
                            t.add_professor(p)
                            break
            elif variavel == "insat":
                for p in professores:
                    if p.nome() == professor:
                        p.insatisfacao = float(linha.split()[-1])
            elif variavel == "insat_disciplinas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_disciplinas = float(linha.split()[-1])
            elif variavel == "insat_cargahor":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_cargahor = float(linha.split()[-1])
            elif variavel == "insat_numdisc":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_numdisc = float(linha.split()[-1])
            elif variavel == "insat_horario":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_horario = float(linha.split()[-1])
            elif variavel == "insat_distintas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_distintas = float(linha.split()[-1])
            elif variavel == "insat_manha_noite":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_manha_noite = float(linha.split()[-1])
            elif variavel == "insat_janelas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_janelas = float(linha.split()[-1])


def ler_solucao_jl(professores, turmas, arquivo):
    with open(arquivo, "r") as fonte:
        for linha in fonte:
            # Pula as linhas que nao setam variaveis
            if not "[" in linha:
                continue

            a = re.split(r"[\[\]]", linha)

            b = a[1].split(",")
            professor = b[0]
            variavel = a[0]

            if variavel == "carga_horaria":
                for p in professores:
                    if p.nome() == professor:
                        p.carga_horaria = float(a[-1])
            elif variavel == "x":
                turmaid = b[1]
                if float(a[-1]) > 0.9:
                    for t in turmas:
                        if t.id() == turmaid:
                            break
                    for p in professores:
                        if p.nome() == professor:
                            p.add_course(t)
                            t.add_professor(p)
                            break
            elif variavel == "insat":
                for p in professores:
                    if p.nome() == professor:
                        p.insatisfacao = float(a[-1])
            elif variavel == "insat_disciplinas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_disciplinas = float(a[-1])
            elif variavel == "insat_cargahor":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_cargahor = float(a[-1])
            elif variavel == "insat_numdisc":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_numdisc = float(a[-1])
            elif variavel == "insat_horario":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_horario = float(a[-1])
            elif variavel == "insat_distintas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_distintas = float(a[-1])
            elif variavel == "insat_manha_noite":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_manha_noite = float(a[-1])
            elif variavel == "insat_janelas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_janelas = float(a[-1])


####################################################################################################################
####################    Funcao                 ler_solucao_cbc          e auxiliares      #########################
####################################################################################################################
def ler_solucao_cbc(professores, turmas, arquivo):
    with open(arquivo, "r") as fonte:
        for linha in fonte:
            # Pula as linhas que nao setam variaveis
            if not "(" in linha:
                continue

            a = re.split("[()]", linha.split()[1])
            b = a[1].split(",")

            professor = b[0]
            variavel = a[0]

            if variavel == "carga_horaria":
                for p in professores:
                    if p.nome() == professor:
                        p.carga_horaria = float(linha.split()[-2])
            elif variavel == "x":
                turmaid = b[1].strip("'")
                if linha.split()[-2] == "1":
                    for t in turmas:
                        if t.id() == turmaid:
                            break
                    for p in professores:
                        if p.nome() == professor:
                            p.turmas_a_lecionar.append(t)
                            break
            elif variavel == "insat":
                for p in professores:
                    if p.nome() == professor:
                        p.insatisfacao = float(linha.split()[-2])
            elif variavel == "insat_disciplinas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_disciplinas = float(linha.split()[-2])
            elif variavel == "insat_cargahor":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_cargahor = float(linha.split()[-2])
            elif variavel == "insat_numdisc":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_numdisc = float(linha.split()[-2])
            elif variavel == "insat_horario":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_horario = float(linha.split()[-2])
            elif variavel == "insat_distintas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_distintas = float(linha.split()[-2])
            elif variavel == "insat_manha_noite":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_manha_noite = float(linha.split()[-2])
            elif variavel == "insat_janelas":
                for p in professores:
                    if p.nome() == professor:
                        p.insat_janelas = float(linha.split()[-2])


####################################################################################################################
####################    Funcao                 ler_grupos                e auxiliares      #########################
####################################################################################################################
def ler_grupos(arquivo):  # Le os grupos do arquivo de grupos
    grupos = []
    with open(arquivo, "r") as fonte:
        for linha in fonte:
            if not linha.isspace():
                tok = linha.split()
                g = classes.Grupo()
                g.id = funcoes_gerais.uniformize(tok[1])
                if tok[0] == "C":
                    g.canonico = True
                for i in tok[2:]:
                    g.disciplinas.append(i)
                grupos.append(g)
    return grupos


####################################################################################################################
####################    Funcao                 ler_sar                   e auxiliares      #########################
####################################################################################################################
def get_sar_version(sarfile):
    """
    Devolve um inteiro associado com a versao do SAR `sarfile` enviado.
    """

    with open(sarfile, "r") as fp:
        for linha in fp:
            if "DISC" in linha:
                if "TIPO" in linha:
                    if "VAGAS" in linha:
                        return 3

                    return 2

                return 1


def sar_vale(linha):  # Define se a linha lida do SAR possui informacoes relevantes
    if len(linha) < 10:
        return False
    tok = linha.split()
    if len(tok) < 10:
        return False
    if tok[0] == "DISC":
        return False
    if tok[-9] in ["MARINGA", "CIANORTE"]:
        return True
    # Caso com horario indisponivel
    if tok[-7] in ["MARINGA", "CIANORTE"]:
        return True


# ----------------------------------------------------------------------------------------------------------------------
def sar_primaria(
    linha,
):  # Uma linha primaria e aquela que comeca uma nova turma, essa funcao as identifica
    if not sar_vale(linha):
        return False
    tok = linha.split()

    # Elimina o caso que a linha comeca com o dia e o caso em que
    # comeca com T,P,T-P
    if len(tok[0]) > 2 and tok[0].isdigit():
        return True

    return False


# ----------------------------------------------------------------------------------------------------------------------
def horario_valido(d, h):
    return d >= 1 and d <= 7 and h >= 1 and h <= 16


# ----------------------------------------------------------------------------------------------------------------------
def copia_turmas(origem):
    destino = classes.Turma()
    destino.codigo = origem.codigo
    destino.turma = origem.turma
    destino.nome = origem.nome
    destino.semestralidade = origem.semestralidade
    destino.dini = origem.dini
    destino.dend = origem.dend
    destino.horarios = list(origem.horarios)  # Cria uma copia por valor
    destino.grupo = origem.grupo
    destino.professor = origem.professor
    destino.vinculada = origem.vinculada
    destino.ch = origem.ch
    destino.curso = origem.curso
    return destino


def _csv_to_dataframe(sarfile):
    df = pd.read_csv(
        sarfile,
        header=None,
        parse_dates=[15, 16],
        delimiter=r"\s*,\s*",
        engine="python",
        comment="#",
    )

    # Transforma em pares
    df[18] = df[[6, 7]].apply(lambda x: [(x[6], x[7])], axis=1)

    # Agrega tudo

    agg_map = {i: "first" for i in range(2, 18) if i not in [6, 7, 14]}
    agg_map[18] = "sum"

    return df.groupby([0, 1, 14]).agg(agg_map)


def _get_grupo(codigo, semestralidade, grupos):
    codigo_s = codigo + "_S{}".format(semestralidade)

    for g in grupos:
        if codigo in g.disciplinas or codigo_s in g.disciplinas:
            return g

    return None


def _load_turmas(df_sar, grupos):
    turmas = []

    for r in df_sar.itertuples():
        t = classes.Turma()

        t.codigo = str(r.Index[0])
        t.turma = str(r.Index[1])
        t.semestralidade = 1 if r.Index[2] == "S1" else 2

        t.grupo = _get_grupo(t.codigo, t.semestralidade, grupos)

        t.dini = r._11.date()
        t.dend = r._12.date()

        t.curso = "" if pd.isna(r._13) else r._13

        if any([(not horario_valido(d, h)) for (d, h) in r._14]):
            print(
                "AVISO: Ignorando turma %s: horario invalido (%d, %d)."
                % (t.codigo, d, h)
            )

            continue

        t.horarios.extend(r._14)

        t.nome = r._1

        t.ch = int(r._9)

        turmas.append(t)

    # Procura vinculadas

    for t in [t for t in turmas if (t.dend - t.dini).days > 180]:
        if t.vinculada:
            continue

        for tt in [tt for tt in turmas if not tt.vinculada]:
            if (
                t.codigo == tt.codigo
                and t.turma == tt.turma
                and t.semestralidade != tt.semestralidade
            ):
                t.vinculada = True
                tt.vinculada = True

    return turmas


def ler_sar_csv(arquivo, grupos):
    return _load_turmas(_csv_to_dataframe(arquivo), grupos)


# ----------------------------------------------------------------------------------------------------------------------
def ler_sar(
    arquivo, grupos, cursos={}
):  # arquivo: arquivo do SAR, grupos: lista dos objetos grupos
    turmas = []
    anual = False
    invalida = False
    t = None

    sar_version = get_sar_version(arquivo)

    with open(arquivo, "r") as fonte:
        for linha in fonte:
            tok = linha.split()
            if sar_primaria(linha):
                # Se a ultima linha era valida, guarde-a
                if t is not None and not invalida:
                    turmas.append(t)

                # se a ultima disciplina lida foi anual, sua correspondente no segundo semestre sera criada
                if anual and not invalida:
                    t = copia_turmas(turmas[-1])
                    t.semestralidade = 2
                    temp = str(t.codigo) + "_S2"
                    for g in grupos:
                        if temp in g.disciplinas:
                            t.grupo = g
                            break
                    turmas.append(t)

                invalida = False
                anual = False
                semestres = []
                t = classes.Turma()
                t.codigo = tok[0]
                t.turma = tok[1]

                # Handle the semester
                l = list(map(int, tok[-3].split("/")))
                t.dini = date(l[2], l[1], l[0])

                l = list(map(int, tok[-1].split("/")))
                t.dend = date(l[2], l[1], l[0])

                if tok[-4] == "A":
                    t.semestralidade = 1
                    anual = True
                    t.vinculada = True
                else:
                    anual = False
                    if tok[-4] == "S1" or tok[-4] == "M1":
                        t.semestralidade = 1
                    else:
                        t.semestralidade = 2

                # Cuida do caso em que nao veio a
                # carga horaria da disciplina
                ntok = -10
                if "." in tok[-6] or "," in tok[-6]:
                    ntok = -12

                d, h = (int(tok[ntok]), int(tok[ntok + 1]))

                if not horario_valido(d, h):
                    print(
                        "AVISO: Ignorando turma %s: horario invalido (%d, %d)."
                        % (t.codigo, d, h)
                    )
                    invalida = True
                    continue

                t.horarios.append((d, h))

                # Ajusta nome de acordo com versao do SAR
                if sar_version == 2:
                    ntok -= 1
                elif sar_version == 3:
                    ntok -= 3

                t.nome = ""
                for i in tok[2:ntok]:
                    t.nome = t.nome + " " + i

                temp = str(t.codigo)
                if anual:
                    temp += "_S" + str(t.semestralidade)
                for g in grupos:
                    if temp in g.disciplinas:
                        t.grupo = g
                        break

                # Para a carga horaria, precisamos
                # remover a virgula
                # O novo SAR vem com
                # '.' ao invés de ',', entao esse
                # codigo é para compatibilidade
                t.ch = 0
                if "," in tok[-6]:
                    t.ch = int(tok[-6].split(",")[0])

                if "." in tok[-6]:
                    t.ch = int(tok[-6].split(".")[0])

                # Determina o curso
                if t.codigo in cursos:
                    t.curso = cursos[t.codigo]

                else:
                    print("AVISO: Disciplina {} sem curso.".format(t.id()))

            else:
                if sar_vale(linha) and not invalida:
                    # Novo SAR, agora tem um T ou T-P ou P em cada linha ou,
                    # pior, com vagas e matriculados.
                    if sar_version == 1:
                        d, h = (int(tok[0]), int(tok[1]))
                    elif sar_version == 2:
                        d, h = (int(tok[1]), int(tok[2]))
                    elif sar_version == 3:
                        d, h = (int(tok[3]), int(tok[4]))

                    if not horario_valido(d, h):
                        print(
                            "AVISO: Ignorando turma %s: horario invalido (%d, %d)."
                            % (t.codigo, d, h)
                        )
                        invalida = True
                        continue

                    t.horarios.append((d, h))

        # fim do loop grande
        if t is not None and not invalida:
            turmas.append(t)

        # se a ultima disciplina (de todas) lida foi anual, sua correspondente no segundo semestre sera criada
        if anual and not invalida:
            t = copia_turmas(turmas[len(turmas)])
            t.semestralidade = 2
            temp = str(t.codigo) + "_S2"
            for g in grupos:
                if temp in g.disciplinas:
                    t.grupo = g
                    break
            turmas.append(t)

        return turmas


############################################################################################################################
#########################################                LER PREFERENCIAS                   ################################
############################################################################################################################
converter_horario = {
    "07:45 - 09:25": (1, 2),
    "09:40 - 12:10": (3, 4, 5),
    "13:30 - 15:10": (6, 7),
    "15:20 - 17:50": (8, 9, 10),
    "17:50 - 19:30": (11, 12),
    "19:30 - 21:10": (13, 14),
    "21:20 - 23:00": (15, 16),
}
# ----------------------------------------------------------------------------------------------------------------------
converter_dia = {"SEG": 2, "TER": 3, "QUA": 4, "QUI": 5, "SEX": 6, "SAB": 7}
# ----------------------------------------------------------------------------------------------------------------------
converter_codigo_de_horario = {
    1: (1, 2),
    2: (3, 4, 5),
    3: (6, 7),
    4: (8, 9, 10),
    5: (11, 12),
    6: (13, 14),
    7: (15, 16),
}
# ----------------------------------------------------------------------------------------------------------------------
converter_periodo = {
    "MANHA": (1, 2, 3, 4, 5),
    "TARDE": (6, 7, 8, 9, 10, 11, 12),
    "NOITE": (13, 14, 15, 16),
}
# ----------------------------------------------------------------------------------------------------------------------
converter_preferencia = {
    "NAO GOSTARIA": 0,
    "DESGOSTARIA LEVEMENTE": 2.5,
    "INDIFERENTE": 5,
    "GOSTARIA LEVEMENTE": 7.5,
    "GOSTARIA": 10,
}


# ----------------------------------------------------------------------------------------------------------------------
def ler_pref(form, grupos, max_impedimentos):
    professores = []
    with open(form, "r", encoding="utf-8") as f:
        for l in f:
            p = classes.Professor()
            tokens = iter(l.split("\t"))
            next(tokens)  # Pula timestamp
            next(tokens)  # Pula email duplicado
            p.nome_completo = funcoes_gerais.uniformize(next(tokens))  # Identificacao
            logger.debug("\tReading teacher %s", p.nome_completo)
            p.matricula = int(next(tokens))  # Identificacao Unica
            # Jeito tosco de remover duplicatas
            # TODO: melhorar isso
            for i in professores:
                if i.matricula == p.matricula:
                    logger.info(
                        "AVISO: Professores "
                        + i.nome()
                        + " e "
                        + p.nome()
                        + " com mesma matrícula. Eliminando entrada antiga.\n"
                    )
                    professores.remove(i)
            p.email = next(tokens)
            p.tel = next(tokens)
            chp1 = next(tokens)
            chp2 = next(tokens)
            if chp1.strip() == "":
                chp1 = "0"
            if chp2.strip() == "":
                chp2 = "0"
            p.chprevia1 = int(chp1)
            p.chprevia2 = int(chp2)
            p.discriminacao_chprevia = funcoes_gerais.uniformize(next(tokens))
            w = funcoes_gerais.uniformize(next(tokens))  # Licença
            if "PRIMEIRO" in w:
                p.licenca1 = True
            if "SEGUNDO" in w:
                p.licenca2 = True
            if "ANUAL" in w:
                continue
            w = funcoes_gerais.uniformize(next(tokens))  # Temporario
            if w == "TEMPORARIO":
                p.temporario = True
            # Le qual o programa de pos
            p.programa_pos = funcoes_gerais.uniformize(next(tokens))
            # Professor tem reducao de carga para a pos?
            p.pos = (
                "PMA" in p.programa_pos
                or "PCM" in p.programa_pos
                or "PEQ" in p.programa_pos
                or "PROFMAT" in p.programa_pos
                or "OUTRO" in p.programa_pos
            )
            # Pesos das disciplinas
            p.peso_disciplinas_bruto = funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_horario_bruto =     funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_cargahor =          funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_distintas =         funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_numdisc =           funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_manha_noite =       funcoes_gerais.convert_numeric_field(float, next(tokens))
            p.peso_janelas_bruto =     funcoes_gerais.convert_numeric_field(float, next(tokens))
            # Inaptidao em grupos
            w = funcoes_gerais.uniformize(next(tokens))
            if len(w) > 0:
                p.inapto = w.split(", ")
            # Preferencia por grupos
            for g in grupos:
                if g.canonico:
                    s = funcoes_gerais.uniformize(next(tokens))
                    if len(s) > 0:  # se a preferencia foi preenchida
                        p.pref_grupos_bruto[g.id] = converter_preferencia[s]
                    else:  # se não, atribuir default 5
                        p.pref_grupos_bruto[g.id] = converter_preferencia["INDIFERENTE"]
            # Reuniao departamento
            w = funcoes_gerais.uniformize(next(tokens))
            if "SIM" in w:
                p.pref_reuniao = True
            # Preferencia compacto/esparso (define o respectivo peso como zero se nao especificado)
            w = funcoes_gerais.uniformize(next(tokens))
            p.peso_janelas = p.peso_janelas_bruto
            if "ESPARSOS" in w:
                p.pref_janelas = True
            elif "COMPACTOS" not in w:
                p.peso_janelas = (
                    0  # Zera peso_janelas se a Preferencia nao for informada
                )
            for i in range(0, max_impedimentos):
                dia = funcoes_gerais.uniformize(next(tokens))
                periodo = funcoes_gerais.uniformize(next(tokens))
                justificativa = funcoes_gerais.uniformize(next(tokens))
                # guarda os dados do impedimento como string para conferencia posterior
                p.lista_impedimentos.append(dia + ", " + periodo + ", " + justificativa)
                # se o dia e periodo foram corretamente preenchidos, marca a respectiva posicao na matriz como 1
                if (
                    len(dia) > 0
                    and not dia.isspace()
                    and dia != "SEM IMPEDIMENTO"
                    and len(periodo) > 0
                    and not periodo.isspace()
                    and periodo != "SEM IMPEDIMENTO"
                ):
                    for h in converter_periodo[periodo]:
                        p.impedimentos[h, converter_dia[dia]] = 1

            # Perguntas do curso - ignorar ate chegar na grade horaria
            w = funcoes_gerais.uniformize(next(tokens))
            while not ("DETALHADO" in w or "RESUMIDO" in w):
                w = funcoes_gerais.uniformize(next(tokens))

            # Comeca o prechimento das tabelas de horario
            m = numpy.zeros((15, 8))
            if "DETALHADO" in w:
                for d in range(2, 8):
                    periodos = ["MANHA", "TARDE", "NOITE"]
                    if d == 7:
                        periodos = ["MANHA", "TARDE"]
                    for i in periodos:
                        pref = funcoes_gerais.uniformize(next(tokens))
                        for h in converter_periodo[i]:
                            if len(pref) == 0:
                                pref = "INDIFERENTE"
                            p.pref_horarios_bruto[h, d] = converter_preferencia[pref]
                for i in range(0, 5):  # Pula as posicoes em branco do formulario
                    try:
                        next(tokens)
                    except StopIteration:
                        pass
            else:
                for i in range(
                    0, 3 * 5 + 2
                ):  # pula as posicoes em branco do formulario
                    next(tokens)
                for i in [
                    "MANHA",
                    "TARDE",
                    "NOITE",
                ]:  # le as preferencias para os dias da semana
                    pref = funcoes_gerais.uniformize(next(tokens))
                    for h in converter_periodo[i]:
                        for d in range(2, 7):  # grava uma copia em cada dia da semana
                            if len(pref) == 0:
                                pref = "INDIFERENTE"
                            p.pref_horarios_bruto[h, d] = converter_preferencia[pref]
                for i in ["MANHA", "TARDE"]:  # lendo as preferencias do sabado
                    pref = funcoes_gerais.uniformize(next(tokens))
                    for h in converter_periodo[i]:
                        if len(pref) == 0:
                            pref = "INDIFERENTE"
                        p.pref_horarios_bruto[h, d + 1] = converter_preferencia[pref]
            # Tudo o que vier depois daqui eh considerado comentario.
            for obs in tokens:
                p.observacoes += funcoes_gerais.uniformize(obs)

            professores.append(p)
    return professores


############################################################################################################################
#########################################                LER PRE-ATRIBUIDAS                 ################################
############################################################################################################################
def ler_pre_atribuidas(arquivo, arquivo_de_fantasmas, professores, turmas):
    """
    Devolve uma lista de pares (professor,turma) pre atribuidos
    """

    print("\nCarregando pre-atribuidas")
    print("---------------------------\n")

    fantasma = []

    with open(arquivo_de_fantasmas, "r") as fant:
        for linha in fant:
            tok = linha.split("\t")

            fantasma.append((tok[0], tok[1]))

    delim = "\t"

    with open(arquivo, "r") as f:
        for l in f:
            if len(l) > 0 and not l.isspace() and r"," in l:
                delim = r","
                break

    with open(arquivo, "r") as f:
        linha = 1

        pre_atribuidas = []

        for l in f:
            if len(l) < 0 or l.isspace():
                continue

            tokens = iter(l.split(delim))

            try:
                matricula = int(next(tokens))

                nome_professor = next(tokens)

                cod_disciplina = next(tokens)

                turma = next(tokens)

                nome_disciplina = next(tokens).rstrip()

                next(tokens)

                semestralidade = int(next(tokens).rstrip()[1])

            except Exception as e:
                s = (
                    "AVISO: Ignorando linha "
                    + str(linha)
                    + " em PRE-ATRIBUIDAS. Erro: "
                    + str(e)
                )

                print(s)

                linha += 1

                continue

            for p in professores:
                if p.matricula == matricula:
                    encontrada = False
                    for t in turmas:
                        # Nao precisa se preocupar com a semestralidade, pois
                        # o codigo e a turma vao bater duas vezes, em caso de
                        # disciplina anual
                        if (
                            t.codigo == cod_disciplina
                            and t.turma == turma
                            and t.semestralidade == semestralidade
                        ):
                            encontrada = True
                            if not (cod_disciplina, turma) in fantasma:
                                pre_atribuidas.append((p, t))
                    if not encontrada:
                        if not (cod_disciplina, turma) in fantasma:
                            s = (
                                "AVISO: Disciplina "
                                + cod_disciplina
                                + " turma "
                                + turma
                                + " ("
                                + nome_disciplina
                                + ") nao encontrada."
                            )
                            print(s)
                    break
            else:
                s = "AVISO: Linha " + str(linha) + ": matricula " + str(matricula) + " "
                s += "(professor " + nome_professor + ")" + " nao encontrada!"
                print(s)

            linha += 1

    return pre_atribuidas


############################################################################################################################
#########################################                LER AQUIVO DE CONFIGURACAO         ################################
############################################################################################################################


def ler_conf(arquivo):
    """
    Le o arquivo de configuracao e devolve um mapa {PARAMETRO:VALOR}com os parametros lidos
    """

    param = {}
    linha = 1

    with open(arquivo, "r") as f:
        for l in f:
            if l.isspace() or l.startswith("#"):
                continue

            tokens = l.split()

            if len(tokens) == 2:
                param[tokens[0]] = tokens[1]
            else:
                print("\nLER_CONF.PY Erro na linha " + str(linha) + "\n")

            linha += 1

    return param
