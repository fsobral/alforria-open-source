from sqlalchemy import Boolean, ForeignKey, Integer, MetaData, SmallInteger, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class GrupoORM(Base):
    __tablename__ = "grupo"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    canonico: Mapped[int] = mapped_column(Boolean)


class ProfessorORM(Base):
    __tablename__ = "professor"

    matricula: Mapped[str] = mapped_column(String, primary_key=True)
    nome_completo: Mapped[str] = mapped_column(String)
    temporario: Mapped[bool] = mapped_column(Boolean, default=False)

    turmas: Mapped[list["TurmaORM"]] = relationship(
        back_populates="professor",
        lazy="selectin",  # evita N + 1
    )


class TurmaORM(Base):
    __tablename__ = "turma"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    nome: Mapped[str] = mapped_column(String)
    codigo_disc: Mapped[str] = mapped_column(String)
    numero_turma: Mapped[int] = mapped_column(Integer)
    semestralidade: Mapped[int] = mapped_column(SmallInteger)

    grupo: Mapped[str] = mapped_column(String, nullable=True)

    professor_matricula: Mapped[str | None] = mapped_column(
        ForeignKey("professor.matricula"), nullable=True
    )

    professor: Mapped["ProfessorORM | None"] = relationship(
        back_populates="turmas",
        lazy="select",  # se deixar selectin aqui o problema reaparece
    )


class DisciplinaORM(Base):
    __tablename__ = "disciplina"
    id: Mapped[int] = mapped_column(primary_key=True)
