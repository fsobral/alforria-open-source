from copy import deepcopy
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..classes import Professor, Turma
from .conversao import (
    professor_para_dominio,
    professor_para_orm,
    turma_para_dominio,
    turma_para_orm,
)
from .modelos import ProfessorORM, TurmaORM


class RepositorioTurmas(Protocol):
    def buscar_por_id(self, id: str) -> Turma | None: ...
    def salvar(self, turma: Turma) -> None: ...


class RepositorioTurmasSQL(RepositorioTurmas):
    def __init__(self, session: Session):
        self._session = session

    def buscar_por_id(self, id: str) -> Turma | None:
        orm = self._session.get(TurmaORM, id)
        return turma_para_dominio(orm) if orm is not None else None

    def salvar(self, turma: Turma) -> None:
        orm = turma_para_orm(turma)
        self._session.merge(orm)


class RepositorioTurmasMemoria(RepositorioTurmas):
    def __init__(self):
        self._dados: dict[str, Turma] = {}

    def buscar_por_id(self, id: str) -> Turma | None:
        return self._dados.get(id)

    def salvar(self, turma: Turma) -> None:
        self._dados[turma.id] = turma


class RepositorioProfessores(Protocol):
    def buscar_por_matricula(self, matricula: str) -> Professor | None: ...
    def buscar_por_nome(self, nome: str) -> Professor | None: ...
    def salvar(self, professor: Professor) -> None: ...
    def listar(self, temporario: bool | None = None) -> list[Professor]: ...


class RepositorioProfessoresSQL(RepositorioProfessores):
    def __init__(self, session: Session):
        self._session = session

    def buscar_por_matricula(self, matricula: str) -> Professor | None:
        orm = self._session.get(ProfessorORM, matricula)
        return professor_para_dominio(orm) if orm is not None else None

    def buscar_por_nome(self, nome: str) -> Professor | None:
        pass

    def salvar(self, professor: Professor) -> None:
        orm = professor_para_orm(professor)
        self._session.merge(orm)

    def listar(self, temporario: bool | None = None) -> list[Professor]:
        stmt = select(ProfessorORM)

        if temporario is not None:
            stmt = stmt.where(ProfessorORM.temporario == temporario)

        orms = self._session.scalars(stmt).all()
        return [professor_para_dominio(orm) for orm in orms]


class RepositorioProfessoresMemoria(RepositorioProfessores):
    def __init__(self):
        self._dados: dict[str, Professor] = {}

    def buscar_por_matricula(self, matricula: str) -> Professor | None:
        p = self._dados.get(matricula, None)
        return deepcopy(p) if p is not None else None

    def buscar_por_nome(self, nome: str) -> Professor | None:
        pass

    def salvar(self, professor: Professor):
        self._dados[professor.matricula] = professor

    def listar(self, temporario: bool | None = None) -> list[Professor]:
        resultado = list(self._dados.values())

        if temporario is not None:
            resultado = [p for p in resultado if p.temporario == temporario]

        return [deepcopy(p) for p in resultado]
