from typing import Protocol

from sqlalchemy.orm import Session

from .classes import Professor, Turma
from .modelos import ProfessorORM, TurmaORM


class RepositorioTurmas(Protocol):
    def busca_por_id(self, id: str) -> Turma | None: ...


class RepositorioTurmasSQL(RepositorioTurmas):
    def __init__(self, session: Session):
        self._session = session

    def busca_por_id(self, id: str) -> Turma | None:
        pass


class RepositorioTurmasMemoria(RepositorioTurmas):
    def __init__(self):
        self._dados = dict[str, Turma] = {}

    def busca_por_id(self, id: str) -> Turma | None:
        return self._dados.get(id)


class RepositorioProfessores(Protocol):
    def busca_por_id(self, id: str) -> Professor | None: ...
    def busca_por_nome(self, nome: str) -> Professor | None: ...


class RepositorioProfessoresSQL(RepositorioProfessores):
    def __init__(self, session: Session):
        self._session = session

    def busca_por_id(self, id: str) -> Professor | None:
        pass

    def busca_por_nome(self, nome: str) -> Professor | None:
        pass


class RepositorioProfessoresMemoria(RepositorioProfessores):
    def __init__(self):
        self._dados = dict[str, Professor] = {}

    def busca_por_id(self, id: str) -> Professor | None:
        return self._dados.get(id)

    def busca_por_nome(self, nome: str) -> Professor | None:
        pass

    def salvar(self, professor):
        self._dados[professor.id] = professor
