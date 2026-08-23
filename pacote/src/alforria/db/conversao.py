from ..dominio.professor import Professor
from ..dominio.turma import Turma
from .modelos import ProfessorORM, TurmaORM


def professor_para_orm(professor: Professor) -> ProfessorORM:
    return ProfessorORM(
        matricula=professor.matricula,
        nome_completo=professor.nome_completo,
        temporario=professor.temporario,
    )


def turma_para_orm(turma: Turma) -> TurmaORM:
    p = turma.professor
    matricula = p.matricula if p is not None else None
    return TurmaORM(
        id=turma.id,
        nome=turma.nome,
        codigo_disc=turma.codigo_disc,
        numero_turma=turma.numero_turma,
        semestralidade=turma.semestralidade,
        professor_matricula=matricula,
    )


def professor_para_dominio(
    professor: ProfessorORM, *, incluir_turmas: bool = True
) -> Professor:

    p = Professor(
        matricula=professor.matricula,
        nome_completo=professor.nome_completo,
        temporario=professor.temporario,
    )

    if incluir_turmas:
        for t_orm in professor.turmas:
            p.add_course(turma_para_dominio(t_orm, incluir_professor=False))

    return p


def turma_para_dominio(turma: TurmaORM, *, incluir_professor: bool = True) -> Turma:
    t = Turma(
        codigo_disc=turma.codigo_disc,
        nome=turma.nome,
        numero_turma=turma.numero_turma,
        semestralidade=turma.semestralidade,
    )

    if turma.professor is not None:
        t.add_professor(professor_para_dominio(turma.professor, incluir_turmas=False))
    return t
