import pytest
from alforria.db.modelos import Base
from alforria.db.repositorios import (
    RepositorioProfessoresMemoria,
    RepositorioProfessoresSQL,
    RepositorioTurmasMemoria,
    RepositorioTurmasSQL,
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessaoSQL = sessionmaker(bind=engine)

    with SessaoSQL() as s:
        yield s


@pytest.fixture(params=["sql", "memoria"])
def repo_professores(request, session):
    if request.param == "sql":
        return RepositorioProfessoresSQL(session)
    return RepositorioProfessoresMemoria()


@pytest.fixture(params=["sql", "memoria"])
def repo_turmas(request, session):
    if request.param == "sql":
        return RepositorioTurmasSQL(session)
    return RepositorioTurmasMemoria()
