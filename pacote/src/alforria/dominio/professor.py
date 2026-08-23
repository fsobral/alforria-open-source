from __future__ import annotations

from typing import TYPE_CHECKING

import numpy

if TYPE_CHECKING:
    from .turma import Turma


class Professor:
    def __init__(self, *, matricula: str, nome_completo: str, temporario: bool = False):
        self.matricula = matricula  # id único do professor (chave primária)
        self.nome_completo = nome_completo
        self.email = None
        self.tel = None
        self.chprevia1 = 0.0
        self.chprevia2 = 0.0
        self.licenca1 = False
        self.licenca2 = False
        self.discriminacao_chprevia = None
        self.temporario = temporario
        self.impedimentos = numpy.zeros((17, 8))
        self.peso_disciplinas = 0.0
        self.peso_disciplinas_bruto = 0.0
        self.peso_horario = 0.0
        self.peso_horario_bruto = 0.0
        self.peso_cargahor = 0.0
        self.peso_distintas = 0.0
        self.peso_janelas = 0.0
        self.peso_janelas_bruto = 0.0
        self.peso_numdisc = 0.0
        self.peso_manha_noite = 0.0
        self.inapto = []  # Lista de ids de grupos
        self.pref_grupos_bruto = {}  # Mapa id de grupo para preferencia
        self.pref_reuniao = False
        self.pref_janelas = False
        self.pref_horarios_bruto = numpy.zeros((17, 8))
        self.pref_grupos = {}
        self.pref_horarios = numpy.zeros((17, 8))
        self.lista_impedimentos = []
        self.chmax = None
        self.chmax1 = None
        self.chmax2 = None
        self.fantasma = False
        self.pos = False
        self.observacoes = ""

        # --------------------------------Valores lidos no arquivo de solucao---------------------
        self.turmas_a_lecionar: list[Turma] = []
        self.carga_horaria = 0.0
        self.insatisfacao = 0.0
        self.insat_disciplinas = 0.0
        self.insat_cargahor = 0.0
        self.insat_numdisc = 0.0
        self.insat_horario = 0.0
        self.insat_distintas = 0.0
        self.insat_manha_noite = 0.0
        self.insat_janelas = 0.0

    def can_teach(self, t):
        """Return true if professor is able and available to teach class 't'."""

        return not (
            any(self.impedimentos[h, d] for (d, h) in t.horarios)
            or (t.grupo and t.grupo.id in self.inapto)
        )

    def add_course(self, t):
        if t in self.turmas_a_lecionar:
            return

        self.turmas_a_lecionar.append(t)
        t.add_professor(self)

    def remove_course(self, t: Turma):
        if t not in self.turmas_a_lecionar:
            return
        self.turmas_a_lecionar.remove(t)
        t.remove_professor(self)

    def carga_horaria_atrib(self):
        ch = 0

        for t in self.turmas_a_lecionar:
            ch += t.carga_horaria()

        return ch

    def _carga_horaria_s(self, semestre):
        ch = 0

        for t in [
            turma
            for turma in self.turmas_a_lecionar
            if turma.semestralidade is semestre
        ]:
            ch += t.carga_horaria()

        return ch

    def carga_horaria_s1(self):
        return self.chprevia1 + self._carga_horaria_s(1)

    def carga_horaria_s2(self):
        return self.chprevia2 + self._carga_horaria_s(2)

    def carga_horaria_total(self):
        return self.chprevia1 + self.chprevia2 + self.carga_horaria_atrib()

    @property
    def id(self):
        # O certo sera return self.matricula, mas ainda nao funciona
        return self.matricula

    def nome(self):
        tok = self.nome_completo.split()
        n = ""
        for palavra in tok:
            if len(palavra) != 0:
                if n != "":
                    n += "_" + palavra
                else:
                    n += palavra
        return n

    def __eq__(self, p):
        return True if (self.id() == p.id()) else False

    def __hash__(self):
        return hash(self.id())

    def __str__(self):
        s = (
            str(self.nome_completo)
            + " "
            + str(self.matricula)
            + " "
            + str(self.email)
            + "\n"
        )
        s += (
            "Temporario: "
            + str(self.temporario)
            + " Pref. Janelas: "
            + str(self.pref_janelas)
            + "\n"
        )
        s += (
            "Carga horaria previa - S1: "
            + str(self.chprevia1)
            + " S2: "
            + str(self.chprevia2)
            + "\n"
        )
        s += (
            "Pesos db="
            + str(self.peso_disciplinas_bruto)
            + " d="
            + str(self.peso_disciplinas)
            + " hb="
            + str(self.peso_horario_bruto)
            + " h="
            + str(self.peso_horario)
            + " c="
            + str(self.peso_cargahor)
            + " dist="
            + str(self.peso_distintas)
            + " jb="
            + str(self.peso_janelas_bruto)
            + " j="
            + str(self.peso_janelas)
            + " n="
            + str(self.peso_numdisc)
            + " mn="
            + str(self.peso_manha_noite)
            + "\n"
        )
        s += "Inapto=" + str(self.inapto) + "\n"
        s += "Impedimentos=\n" + str(self.impedimentos[1:17, 2:8]) + "\n"
        s += "Pref. Grupos Bruto=\n" + str(self.pref_grupos_bruto) + "\n"
        s += "Pref. Grupos=\n" + str(self.pref_grupos) + "\n"
        s += "Pref. Horarios Bruto\n" + str(self.pref_horarios_bruto[1:17, 2:8]) + "\n"
        s += "Pref. Horarios\n" + str(self.pref_horarios[1:17, 2:8])
        return s

    def ajustar(self):
        # Ajuste do impedimento caso seja um titular que queira participar da reuniao
        if self.pref_reuniao and not self.temporario:
            for h in range(1, 6):
                self.impedimentos[h, 3] = 1

        # Ajuste da preferencia por horarios
        maximo = 0
        for j in range(2, 8):
            fim = 17
            if j == 7:
                fim = 11
            for i in range(1, fim):
                if (
                    self.pref_horarios_bruto[i, j] > maximo
                    and not self.impedimentos[i, j]
                ):
                    maximo = self.pref_horarios_bruto[i, j]
        minimo = 10
        for j in range(2, 8):
            fim = 17
            if j == 7:
                fim = 11
            for i in range(1, fim):
                if (
                    self.pref_horarios_bruto[i, j] < minimo
                    and not self.impedimentos[i, j]
                ):
                    minimo = self.pref_horarios_bruto[i, j]
        if maximo == minimo:
            self.peso_horario = 0.0
        else:
            self.peso_horario = self.peso_horario_bruto
            for j in range(2, 8):
                for i in range(1, 17):
                    self.pref_horarios[i, j] = (
                        -10
                        * (self.pref_horarios_bruto[i, j] - maximo)
                        / (maximo - minimo)
                    )
            # Se o temporario deseja participar da reuniao, entao coloca insatisfacao maxima no horario
            if self.pref_reuniao and self.temporario:
                for h in range(1, 6):
                    self.pref_horarios[h, 3] = 10
        # Ajuste da preferencia por grupos
        maximo = 0
        for g in self.pref_grupos_bruto.keys():
            if self.pref_grupos_bruto[g] > maximo and g not in self.inapto:
                maximo = self.pref_grupos_bruto[g]
        minimo = 10
        for g in self.pref_grupos_bruto.keys():
            if self.pref_grupos_bruto[g] < minimo and g not in self.inapto:
                minimo = self.pref_grupos_bruto[g]
        if maximo == minimo:
            self.peso_disciplinas = 0.0
        else:
            self.peso_disciplinas = self.peso_disciplinas_bruto
            for g in self.pref_grupos_bruto.keys():
                self.pref_grupos[g] = (
                    -10 * (self.pref_grupos_bruto[g] - maximo) / (maximo - minimo)
                )
