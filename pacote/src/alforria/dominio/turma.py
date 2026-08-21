import numpy


class Turma:
    def __init__(self):
        self.codigo = None
        self.turma = None
        self.nome = None
        self.semestralidade = None  # 1 ou 2
        self.horarios: list[
            tuple[numpy.int64, numpy.int64]
        ] = []  # Lista de pares (dia,horario)
        self.grupo: Grupo | None = None  # Objeto Grupo
        self.professor = None  # Objeto Professor ou Nome do Professor ????
        self.vinculada = False
        self.eh_cliente = False  # Indica se a turma eh uma turma cliente ou "fantasma" e tera suas aulas juntamente com outra
        self.turmas_clientes = []  # Lista de turmas que sao clientes desta
        self.pos = False
        self.ch = 0
        self.dini = None
        self.dend = None
        self.curso = ""

    def id(self):
        return str(self.codigo) + "_" + str(self.turma) + "_" + str(self.semestralidade)

    def __str__(self):

        return (
            self.id()
            + " "
            + (" Sem professor" if self.professor is None else self.professor.id())
            + " CH: "
            + str(self.ch)
            + " "
            + str([-"({0:d}, {1:d}) ".format(*h) for h in self.horarios])
        )

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
