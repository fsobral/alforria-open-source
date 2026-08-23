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


def test_salvar_atualiza_professor_existente(repo_professores: RepositorioProfessores):
    p = Professor(matricula="p1", nome_completo="Ana")
    repo_professores.salvar(p)

    p.nome_completo = "Anna"
    repo_professores.salvar(p)

    encontrado = repo_professores.buscar_por_matricula("p1")

    assert encontrado.nome_completo == "Anna"


def test_listar_todos_os_professores(repo_professores: RepositorioProfessores):
    p1 = Professor(matricula="p1", nome_completo="Professor 1")
    repo_professores.salvar(p1)
    p2 = Professor(matricula="p2", nome_completo="Professor 2")
    repo_professores.salvar(p2)
    p3 = Professor(matricula="p3", nome_completo="Professor 3")
    repo_professores.salvar(p3)
    p4 = Professor(matricula="p4", nome_completo="Professor 4")
    repo_professores.salvar(p4)

    professores = repo_professores.listar()

    assert len(professores) == 4
    assert any(p.matricula == "p1" for p in professores)
    assert any(p.matricula == "p2" for p in professores)
    assert any(p.matricula == "p3" for p in professores)
    assert any(p.matricula == "p4" for p in professores)


def test_listar_repo_vazio_retorna_lista_vazia(
    repo_professores: RepositorioProfessores,
):
    assert repo_professores.listar() == []


def test_listar_filtra_por_temporario(repo_professores: RepositorioProfessores):
    p1 = Professor(matricula="p1", nome_completo="Professor 1", temporario=False)
    repo_professores.salvar(p1)
    p2 = Professor(matricula="p2", nome_completo="Professor 2", temporario=True)
    repo_professores.salvar(p2)
    p3 = Professor(matricula="p3", nome_completo="Professor 3", temporario=False)
    repo_professores.salvar(p3)
    p4 = Professor(matricula="p4", nome_completo="Professor 4", temporario=False)
    repo_professores.salvar(p4)
    p5 = Professor(matricula="p5", nome_completo="Professor 5", temporario=True)
    repo_professores.salvar(p5)

    temporarios = repo_professores.listar(temporario=True)
    efetivos = repo_professores.listar(temporario=False)

    assert len(temporarios) == 2
    assert any(p.matricula == "p2" for p in temporarios)
    assert any(p.matricula == "p5" for p in temporarios)

    assert len(efetivos) == 3
    assert any(p.matricula == "p1" for p in efetivos)
    assert any(p.matricula == "p3" for p in efetivos)
    assert any(p.matricula == "p4" for p in efetivos)


def test_salvar_duas_vezes_nao_duplica(repo_professores: RepositorioProfessores):
    p1 = Professor(matricula="p1", nome_completo="Professor 1")
    repo_professores.salvar(p1)
    p2 = Professor(matricula="p2", nome_completo="Professor 2")
    repo_professores.salvar(p2)
    repo_professores.salvar(p1)
    repo_professores.salvar(p1)

    professores = repo_professores.listar()

    assert len(professores) == 2
    assert any(p.matricula == "p1" for p in professores)
    assert any(p.matricula == "p2" for p in professores)
