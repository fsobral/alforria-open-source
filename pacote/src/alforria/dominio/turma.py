import numpy

from .grupo import Grupo
from .professor import Professor


class Turma:
    def __init__(
        self,
        *,
        nome: str,
        codigo_disc: str,
        numero_turma: int = 1,
        semestralidade: int = 1,
    ):
        self.codigo_disc = codigo_disc
        self.numero_turma = numero_turma
        self.nome = nome
        self.semestralidade = semestralidade  # 1 ou 2
        self.horarios: list[
            tuple[numpy.int64, numpy.int64]
        ] = []  # Lista de pares (dia,horario)
        self.grupo: Grupo | None = None  # Objeto Grupo
        self.professor: Professor = None  # Objeto Professor ou Nome do Professor ????
        self.vinculada = False
        self.eh_cliente = False  # Indica se a turma eh uma turma cliente ou "fantasma" e tera suas aulas juntamente com outra
        self.turmas_clientes = []  # Lista de turmas que sao clientes desta
        self.pos = False
        self.ch = 0
        self.dini = None
        self.dend = None
        self.curso = ""

    @property
    def id(self):
        return f"{self.codigo_disc}_{self.numero_turma}_{self.semestralidade}"

    def __str__(self):
        p = self.professor
        id_professor = p.id if p is not None else "Sem professor"
        horarios_str = [f"({h[0]:d}, {h[1]:d})" for h in self.horarios]

        return f"{self.id} {id_professor} CH: {self.ch} {horarios_str}"

    def carga_horaria(self):
        if self.ch > 0:
            return self.ch
        else:
            return len(self.horarios)

    def add_professor(self, p):
        """Add a relation with professor 'p'."""
        self.professor = p

    def remove_professor(self, p):
        """Remove the relation with professor 'p'."""
        self.professor = None
