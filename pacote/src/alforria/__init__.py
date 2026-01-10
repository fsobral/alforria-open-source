"""Pacote Alforria"""

__version__ = "0.3.0"

import logging
import re
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter, merge_completers

from . import check
from . import funcoes_escrita as escrita
from . import funcoes_leitura as leitura

_PATHS_PATH = "../config/paths.cnf"
_ALFCFG_PATH = "../config/alforria.cnf"
_CONST_PATH = "../config/constantes.cnf"

_alforria_completer = WordCompleter(
    [
        "attribute",
        "set_paths",
        "set_config",
        "load",
        "save",
        "moveto",
        "to_pdf",
        "check",
        "verbosity",
        "show",
        "remove",
        "report",
    ],
    ignore_case=True,
)

_session = None

# Configura nivel de saida

# Adiciona o vazio, caso necessario
logging.getLogger().addHandler(logging.NullHandler())

logger = logging.getLogger("alforria")

logger.addHandler(logging.StreamHandler())

logger.setLevel(logging.ERROR)

professores = None

grupos = None

turmas = None

pre_atribuidas = None

_professor_search_name = dict()

_course_search_id = dict()

_course_professor_search = dict()

_hd_course_search = dict()


def set_config_path(path: str):
    global _PATHS_PATH, _ALFCFG_PATH, _CONST_PATH
    _PATHS_PATH = path + "/paths.cnf"
    _ALFCFG_PATH = path + "/alforria.cnf"
    _CONST_PATH = path + "/constantes.cnf"


def __gen_stats__(params):
    """
    Utility function to calculate stats for courses and professors.
    """

    # Classes
    num_t = 0

    ch = [0, 0, 0]

    # Professors
    num_p_co = 0
    num_p_ef = 0
    num_p_ef_pos = 0

    ch_previa = [0, 0, 0]

    chminpe = [0, 0, 0]
    chmaxpe = [0, 0, 0]
    chminpc = [0, 0, 0]
    chmaxpc = [0, 0, 0]

    for t in turmas:
        # Conta as anuais como 2
        num_t += 1

        ch[2] += t.carga_horaria()

        if t.semestralidade == 1:
            ch[0] += t.carga_horaria()
        else:
            ch[1] += t.carga_horaria()

    for p in professores:
        ch_previa[0] += p.chprevia1
        ch_previa[1] += p.chprevia2
        ch_previa[2] += p.chprevia1 + p.chprevia2

        if p.temporario:
            num_p_co += 1
            chmaxsem = int(params["chmax_temporario_semestral"])
            chmaxanual = int(params["chmax_temporario_anual"])
            chminanual = int(params["chmin_temporario_anual"])
        else:
            num_p_ef += 1
            if p.pos:
                num_p_ef_pos += 1
            chmaxsem = int(params["chmax_efetivo_semestral"])
            chmaxanual = int(params["chmax_efetivo_anual"])
            chminanualgrad = int(params["chmin_graduacao"])
            chminanual = int(params["chmin_efetivo_anual"])

        if p.licenca1 and p.licenca2:
            continue

        if p.licenca1:
            if p.temporario:
                chminpc[1] += chminanual / 2
                chmaxpc[1] += chmaxsem
                chminpc[2] += chminanual / 2
                chmaxpc[2] += chmaxsem
            else:
                chminpe[1] += chminanual / 2
                chmaxpe[1] += chmaxsem
                chminpe[2] += chminanual / 2
                chmaxpe[2] += chmaxsem
        elif p.licenca2:
            if p.temporario:
                chminpc[0] += chminanual / 2
                chmaxpc[0] += chmaxsem
                chminpc[2] += chminanual / 2
                chmaxpc[2] += chmaxsem
            else:
                chminpe[0] += chminanual / 2
                chmaxpe[0] += chmaxsem
                chminpe[2] += chminanual / 2
                chmaxpe[2] += chmaxsem
        else:
            if p.temporario:
                chminpc[0] += chminanual / 2
                chmaxpc[0] += chmaxsem
                chminpc[1] += chminanual / 2
                chmaxpc[1] += chmaxsem
                chminpc[2] += chminanual
                chmaxpc[2] += chmaxanual
            else:
                chminpe[0] += chminanual / 2
                chmaxpe[0] += chmaxsem
                chminpe[1] += chminanual / 2
                chmaxpe[1] += chmaxsem
                chminpe[2] += chminanual
                chmaxpe[2] += chmaxanual

    return (
        [num_t],
        [num_p_ef],
        [num_p_ef_pos],
        [num_p_co],
        ch,
        ch_previa,
        chminpe,
        chmaxpe,
        chminpc,
        chmaxpc,
    )


def _report_(*args):
    """
    Create graphical and text reports, for data visualization.
    """

    import matplotlib.pyplot as plt
    import numpy as np

    global _CONST_PATH
    global professores, grupos, turmas

    params = leitura.ler_conf(_CONST_PATH)

    if len(args) == 0:
        logger.error("Uso: report [imp|t|g|ch]")

        return

    rtype = args[0]

    if rtype == "imp":
        h = np.zeros((17, 8))

        for p in professores:
            np.add(h, p.impedimentos, out=h)

        plt.matshow(h[1:17, 2:8], cmap=plt.cm.Reds)
        plt.colorbar()
        plt.xticks(np.arange(0, 6), ["S", "T", "Q", "Q", "S", "S"])
        plt.title("Impedimentos dos professores")
        plt.show()

    elif rtype == "t":
        hc = np.zeros((17, 8))

        for t in turmas:
            for d, h in t.horarios:
                hc[h, d] += 1.0

        plt.matshow(hc[1:18, 2:8], cmap=plt.cm.Reds)
        plt.colorbar()
        plt.title("Horarios das disciplinas ofertadas")
        plt.show()

    elif rtype == "g":
        hg = dict([(g.id, 0) for g in grupos])

        for p in professores:
            for gid in p.inapto:
                hg[gid] += 1

        plt.bar(hg.keys(), hg.values())
        plt.title("Impedimentos em grupos")
        plt.xticks(rotation=45)
        plt.show()

    elif rtype == "ch":
        nd, npe, npep, npc, ch, ch_previa, chminpe, chmaxpe, chminpc, chmaxpc = (
            __gen_stats__(params)
        )

        width = 0.25

        x = np.arange(0, 3)

        fig, axes = plt.subplots(ncols=2, nrows=1)

        axes[0].bar(x, ch, width, color="lightcoral", label="Demanda")
        axes[0].bar(
            x, ch_previa, width, color="indianred", label="Ch. Previa", bottom=ch
        )
        axes[0].bar(
            x + width, chminpe, width, color="cornflowerblue", label="Min. Efetivo"
        )
        axes[0].bar(
            x + width,
            chminpc,
            width,
            color="lightsteelblue",
            label="Min. Colaborador",
            bottom=chminpe,
        )
        axes[0].bar(
            x + 2 * width, chmaxpe, width, color="darkblue", label="Max. Efetivo"
        )
        axes[0].bar(
            x + 2 * width,
            chmaxpc,
            width,
            color="mediumblue",
            label="Max. Colaborador",
            bottom=chmaxpe,
        )
        axes[0].set_xticks(x + 1.25 * width)
        axes[0].set_xticklabels(["1S", "2S", "Total"])
        axes[0].set_title("Demanda e oferta")
        axes[0].legend()

        x = np.arange(0, 2)

        axes[1].bar(x[0], nd)
        axes[1].bar(x[1:], npe, label="Efetivos")
        axes[1].bar(x[1:], npep, label="Efetivos Pos", bottom=npe)
        axes[1].bar(x[1:], npc, label="Colaboradores", bottom=[npe[0] + npep[0]])
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(["Turmas", "Professores"])
        axes[1].set_title("Turmas e professores")
        axes[1].legend()

        plt.show()

    else:
        logger.error("Uso: report [imp|t|g|ch]")


def _load_():
    """

    This function loads all the data.

    """

    global _PATHS_PATH, _ALFCFG_PATH
    global professores, grupos, turmas, pre_atribuidas
    global _professor_search_name, _course_search_id, _course_professor_search

    paths = leitura.ler_conf(_PATHS_PATH)
    configuracoes = leitura.ler_conf(_ALFCFG_PATH)

    # Carrega os grupos de disciplinas
    grupos = leitura.ler_grupos(paths["GRUPOSPATH"])

    # Carrega os professores e suas preferencias e ajusta os valores dados
    # às preferências para que fiquem entre 0 e 10.
    professores = leitura.ler_pref(
        paths["PREFPATH"], grupos, int(configuracoes["MAXIMPEDIMENTOS"])
    )

    # Updates the names of professors to the autocompleter. Also,
    # initializes the fast search for professors for a given time of
    # the week.

    for p in professores:
        p.ajustar()

    # Cria uma lista de busca dos professores por nome, para agilizar
    # a busca
    _professor_search_name = {p.nome(): p for p in professores}

    global _session

    if _session is not None:
        _session.completer = merge_completers(
            [_session.completer, WordCompleter(list(p.nome() for p in professores))]
        )

    # Carrega as turmas de disciplinas do ano e elimina as disciplinas
    # fantasmas (turmas com números diferentes que são, na verdade, a
    # mesma turma)

    turmas = leitura.ler_sar_csv(paths["SARPATH"], grupos)

    turmas = leitura.caca_fantasmas(paths["FANTPATH"], turmas)

    # Updates the names of the courses to the autocompleter

    if _session is not None:
        _session.completer = merge_completers(
            [_session.completer, WordCompleter(list(t.id() for t in turmas))]
        )

    for t in turmas:
        for d, h in t.horarios:
            if (d, h, t.semestralidade) in _hd_course_search:
                _hd_course_search[(d, h, t.semestralidade)].add(t)

            else:
                _hd_course_search[(d, h, t.semestralidade)] = {t}

    _course_professor_search = {
        t.id(): {p for p in professores if p.can_teach(t)} for t in turmas
    }

    # Cria uma lista de busca de turmas por id
    # (NOME_TURMA_SEMESTRALIDADE) para agilizar as buscas

    _course_search_id = {t.id(): t for t in turmas}

    # Carrega o arquivo de disciplinas pre-atribuidas
    pre_atribuidas = leitura.ler_pre_atribuidas(
        paths["ATRIBPATH"], paths["FANTPATH"], professores, turmas
    )


def _set_log_level_(level):
    """

    This function changes the log level for Alforria.

    """

    global logger

    v = int(cmds[1])

    if v < 1:
        logger.setLevel(logging.ERROR)

    elif v == 1:
        logger.setLevel(logging.INFO)

    else:
        logger.setLevel(logging.DEBUG)

    print("Changed logger level")


def _move_to_(*args):
    """Move a set o courses from a professor to another. Does not check
    overlapping courses.

    """

    global _professor_search_name, _course_search_id

    # Show correct usage of the function
    if len(args) < 3:
        logger.error(
            "Uso: moveto <professor origem> <professor destino> turma1 [turma2 turma3...]"
        )

        return

    # Check if both professors exist
    if args[0] not in _professor_search_name:
        logger.error("Nao encontrado docente: %s" % args[0])

        return

    if args[1] not in _professor_search_name:
        logger.error("Nao encontrado docente: %s" % args[1])

        return

    p_from = _professor_search_name[args[0]]

    p_to = _professor_search_name[args[1]]

    c = args[2:]

    # Only moves if the origin professor actually teaches all the
    # courses (that exist)

    tlist = _parse_turmas_(c, _course_search_id)

    for t in tlist:
        if t.professor is not p_from:
            logger.error(
                "Professor %s nao ministra turma %s. Nao ira mover disciplina alguma."
                % (p_from.nome(), t.id())
            )

            return

    for t in tlist:
        _remove_from_(t, p_from)

        _attribute_t_to_p(t, p_to)


def _parse_turmas_gen_(cstr, course_fast_index):
    """Cria um gerador, listando apenas as turmas existentes na lista
    'cstr'self.

    """

    for c in cstr:
        if c not in course_fast_index:
            logger.error("Turma %s nao encontrada. Ignorando." % c)

            continue

        yield course_fast_index[c]


def _parse_turmas_(cstr, course_fast_index):
    """Devolve uma lista de objetos do tipo Turma, criada a partir de uma
    lista de ids.

    """

    return list(_parse_turmas_gen_(cstr, course_fast_index))


def _attribute_t_to_p(t, p):
    """Utility function to add course to professor, checking previous
    attribuitions. Also, handles annual courses.

    """

    global _course_search_id

    # if t.vinculada and t.semestralidade == 2:

    #     logger.error("Nao permitido atribuir parte de disciplina anual %s -> %s.", (t.id(), p.nome()))

    #     return

    if t.professor is not None:
        if t.professor != p:
            logger.error("Turma %s ja atribuida a %s." % (t.id(), t.professor.nome()))

        return

    p.add_course(t)

    t.add_professor(p)

    # # Se a disciplina anual, sabemos S1 e S2 estao
    # # vinculados. Desta forma, procuramos S2 na lista de
    # # turmas

    # if t.vinculada and t.semestralidade == 1:

    #     cvinc = (t.id()).replace("S1", "S2")

    #     if cvinc not in _course_search_id:

    #         logger.error("Nao encontrada turma vinculada: %s", cvinc)

    #         return

    #     tvinc = _course_search_id[cvinc]

    #     p.add_course(tvinc)

    #     # Isso pode dar um problema se apenas o segundo semestre de
    #     # uma disciplina anual foi atribuido. Por enquanto isso eh
    #     # proibido.
    #     tvinc.add_professor(p)


def _remove_(*args):
    """
    Remove the given courses from the given professor.
    """

    global _professor_search_name, _course_search_id

    if len(args) < 2:
        logger.error("Uso: remove <professor> <turma1> [turma2 ...]")

        return

    name = args[0]

    cour = args[1:]

    if name not in _professor_search_name:
        logger.error("Nao encontrado docente: %s", name)

        return

    p = _professor_search_name[name]

    for tc in _parse_turmas_gen_(cour, _course_search_id):
        _remove_from_(tc, p)


def _remove_from_(t, p):
    """Remove turma 't' do professor 'p'. Se a turma eh anual, entao
    remove o segundo semestre tambem.

    TODO: Tratar o caso de disciplina anual quando o segundo semestre eh enviado.

    """

    t.remove_professor(p)

    p.remove_course(t)

    if t.vinculada and t.semestralidade == 1:
        cvinc = (t.id()).replace("S1", "S2")

        logger.warn("Atencao. Verifique se professor ministra %s.", cvinc)

        # if cvinc not in _course_search_id:

        #     logger.error("Nao encontrada turma vinculada: %s", cvinc)

        #     return

        # tvinc = _course_search_id[cvinc]

        # p.remove_course(tvinc)

        # tvinc.remove_professor(p)


def _attribute_(*args):
    """This function attributes courses to professors and professors to
    courses, according to the specified files or according to the arguments.

    """

    global \
        pre_atribuidas, \
        professores, \
        turmas, \
        _professor_search_name, \
        _course_search_id

    if pre_atribuidas is None or professores is None or turmas is None:
        print("Necessary to load data first.")

    nargs = len(args)

    if nargs == 0:
        for p, t in pre_atribuidas:
            _attribute_t_to_p(t, p)

            # # Nao adiciona o segundo semestre quando vinculada
            # if not t.vinculada or t.semestralidade == 1:

            #     _attribute_t_to_p(t, p)

    elif nargs >= 2:
        name = args[0]

        cour = args[1:]

        if name not in _professor_search_name:
            logger.error("Nao encontrado docente: %s", name)

            return

        p = _professor_search_name[name]

        for c in cour:
            if c not in _course_search_id:
                logger.error("Nao encontrada turma: %s", c)

                continue

            t = _course_search_id[c]

            _attribute_t_to_p(t, p)

    else:
        logger.error("Uso: attribute [professor turma1 turma2 ...].")


def _show_(*args):
    global professores, turmas, _professor_search_name, _course_search_id

    if len(args) != 1:
        print("Usage: show <professor ou turma>")

        return

    if professores is None or turmas is None:
        print("Necessary to load data first.")

        return

    name = args[0]

    if name not in _professor_search_name:
        if name not in _course_search_id:
            logger.error("Nao encontrado: %s.", name)

        else:
            print(_course_search_id[name])

    else:
        print(_professor_search_name[name].display())


def _save_csv_(*args):
    """
    This function saves the relations professors and classes.
    """

    global _ALFCFG_PATH
    global professores, turmas

    configuracoes = leitura.ler_conf(_ALFCFG_PATH)

    fname = configuracoes["RELDIR"] + "/atribuicoes.csv"

    if len(args) > 1:
        logger.error("Usage: save [fname]")

    elif len(args) == 1:
        fname = configuracoes["RELDIR"] + "/" + args[0]

    escrita.escreve_atribuicoes(professores, turmas, fname)


def _to_pdf_():
    global _ALFCFG_PATH
    global professores, turmas

    if professores is not None:
        configuracoes = leitura.ler_conf(_ALFCFG_PATH)

        prof_ord = sorted(professores, key=lambda x: x.nome())

        RELDIR = configuracoes["RELDIR"]

        escrita.cria_relatorio_geral(prof_ord, RELDIR)

        escrita.escreve_pre_atribuidas(
            professores, turmas, RELDIR + "pre_atribuidas.tsv"
        )

        escrita.escreve_atribuicoes(professores, turmas, RELDIR + "atribuicoes.csv")

        escrita.escreve_disciplinas(professores, turmas, RELDIR + "disciplinas.csv")

        escrita.write_ch_table(professores, RELDIR)

        print("Report created in directory %s" % RELDIR)

    else:
        print("Necessary to load data first.")


def _check_(*args):
    global _CONST_PATH, professores, _professor_search_name, _course_search_id

    constantes = leitura.ler_conf(_CONST_PATH)

    if professores is None:
        print("Necessary to load data first.")

        return

    if len(args) == 0:
        for p in professores:
            check.check_p(p, constantes)

    elif len(args) == 1:
        name = args[0]

        if name not in _professor_search_name:
            logger.error("Nao encontrado: %s.", name)

        else:
            check.check_p(_professor_search_name[name], constantes)

    elif len(args) >= 2:
        name = args[0]

        cour = args[1:]

        if name not in _professor_search_name:
            logger.error("Nao encontrado: %s.", name)

            return

        clist = [_course_search_id[c] for c in cour if c in _course_search_id]

        clist2 = [
            _course_search_id[(c.id()).replace("S1", "S2")]
            for c in clist
            if (c.vinculada and c.semestralidade == 1)
        ]

        clist.extend(clist2)

        if len(clist) == 0:
            logger.error("Nao encontrada nenhuma disciplina.")

            return

        check.check_p_c(_professor_search_name[name], clist, constantes)

    else:
        logger.error("Uso: check [professor [turma1 turma2 ...]]")


def _find_(*args):
    """Find available professors to teach a given class."""

    global _CONST_PATH
    global _course_professor_search, _course_search_id

    if len(args) != 1:
        logger.error("Uso: find turma")

        return

    name = args[0]

    if name not in _course_professor_search:
        logger.error("Turma nao encontrada: %s" % name)

        return

    constantes = leitura.ler_conf(_CONST_PATH)

    t = _course_search_id[name]

    s = _course_professor_search[name]

    # Deal with annual courses
    if t.vinculada and t.semestralidade == 1:
        name2 = (t.id()).replace("S1", "S2")

        s = s.intersection(_course_professor_search[name2])

    # Sort by group preference, filtering available professors
    for p in sorted(
        (pp for pp in s if check.check_p_c(pp, [t], constantes, verbosity=False)),
        reverse=True,
        key=lambda x: x.nome() if t.grupo is None else (10 - x.pref_grupos[t.grupo.id]),
    ):
        print(
            " %s: %d"
            % (p.nome(), -1 if t.grupo is None else (10 - p.pref_grupos[t.grupo.id]))
        )


def parse_command(command):
    """

    This function parses the commands and calls the correct functions.

    """

    global _PATHS_PATH
    global _ALFCFG_PATH
    global professores

    cmds = command.split()

    if len(cmds) > 0:
        if cmds[0] == "load":
            _load_()

        elif cmds[0] == "verbosity":
            if len(cmds) == 2:
                _set_log_level_(cmds[1])
            else:
                print("Usage: %s log_level" % cmds[0])

        elif cmds[0] == "set_paths":
            _PATHS_PATH = cmds[1]

        elif cmds[0] == "set_config":
            _ALFCFG_PATH = cmds[1]

        elif cmds[0] == "attribute":
            _attribute_(*cmds[1:])

        elif cmds[0] == "to_pdf":
            _to_pdf_()

        elif cmds[0] == "show":
            _show_(*cmds[1:])

        elif cmds[0] == "check":
            _check_(*cmds[1:])

        elif cmds[0] == "save":
            _save_csv_(*cmds[1:])

        elif cmds[0] == "remove":
            _remove_(*cmds[1:])

        elif cmds[0] == "report":
            _report_(*cmds[1:])

        elif cmds[0] == "find":
            _find_(*cmds[1:])

        elif cmds[0] == "moveto":
            _move_to_(*cmds[1:])

        else:
            print("Unknown command %s" % cmds[0])


def mainfunc():
    global _session

    _session = PromptSession(completer=_alforria_completer)

    while True:
        try:
            command = _session.prompt("> ")

        except KeyboardInterrupt:
            continue

        except EOFError:
            break

        else:
            try:
                parse_command(command)

            except Exception as e:
                logger.error("Unexpected error: " + str(e))

    print("Exiting.")


if __name__ == "__main__":
    mainfunc()
