from alforria.db.repositorios import RepositorioProfessores
from alforria.dominio.professor import Professor


def test_salvar_e_buscar(repo_professores: RepositorioProfessores):
    p = Professor(matricula="p1", nome_completo="Ana")
    repo_professores.salvar(p)

    encontrado = repo_professores.buscar_por_matricula("p1")

    assert encontrado is not None
    assert encontrado.nome_completo == "Ana"


def test_buscar_inexistente_retorna_none(repo_professores: RepositorioProfessores):
    assert repo_professores.buscar_por_matricula("nao_existe") is None
