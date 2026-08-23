from alforria.db.repositorios import RepositorioTurmas
from alforria.dominio.turma import Turma


def test_salvar_e_buscar(repo_turmas: RepositorioTurmas):
    t = Turma(nome="Cálculo 1", codigo_disc="1", numero_turma=1, semestralidade=1)
    repo_turmas.salvar(t)

    encontrada = repo_turmas.buscar_por_id("1_1_1")

    assert encontrada is not None
    assert encontrada.nome == "Cálculo 1"


def test_buscar_inexistente_retorna_none(repo_turmas: RepositorioTurmas):
    assert repo_turmas.buscar_por_id("nao existe") is None


#     assert repo_professores.buscar_por_matricula("nao_existe") is None
