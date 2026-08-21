import numpy

from .dominio.grupo import Grupo
from .dominio.professor import Professor
from .dominio.turma import Turma


class Paths:
    def __init__(self):
        self.GRUPOSPATH = None
        self.PREFPATH = None
        self.SARPATH = None
        self.ATRIBPATH = None
        self.FANTPATH = None
        self.DATPATH = None
        self.SOLPATH = None
        self.preenchida = False
