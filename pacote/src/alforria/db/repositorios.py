from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..classes import Professor, Turma
from .conversao import professor_para_orm
from .modelos import ProfessorORM, TurmaORM


class RepositorioTurmas(Protocol):
    def buscar_por_id(self, id: str) -> Turma | None: ...


class RepositorioTurmasSQL(RepositorioTurmas):
    def __init__(self, session: Session):
        self._session = session

    def buscar_por_id(self, id: str) -> Turma | None:
        pass


class RepositorioTurmasMemoria(RepositorioTurmas):
    def __init__(self):
        self._dados: dict[str, Turma] = {}

    def buscar_por_id(self, id: str) -> Turma | None:
        return self._dados.get(id)


class RepositorioProfessores(Protocol):
    def buscar_por_matricula(self, matricula: str) -> Professor | None: ...
    def buscar_por_nome(self, nome: str) -> Professor | None: ...
    def salvar(self, professor: Professor) -> None: ...


class RepositorioProfessoresSQL(RepositorioProfessores):
    def __init__(self, session: Session):
        self._session = session

    def buscar_por_matricula(self, matricula: str) -> Professor | None:
        return self._session.get(ProfessorORM, matricula)

    def buscar_por_nome(self, nome: str) -> Professor | None:
        pass

    def salvar(self, professor: Professor) -> None:
        orm = professor_para_orm(professor)
        self._session.merge(orm)


class RepositorioProfessoresMemoria(RepositorioProfessores):
    def __init__(self):
        self._dados: dict[str, Professor] = {}

    def buscar_por_matricula(self, matricula: str) -> Professor | None:
        return self._dados.get(matricula, None)

    def buscar_por_nome(self, nome: str) -> Professor | None:
        pass

    def salvar(self, professor: Professor):
        self._dados[professor.matricula] = professor
