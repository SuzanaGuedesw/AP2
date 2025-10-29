from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base


ENGINE = create_engine('sqlite:///gerenciamento.db', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

def get_db():
    """Gerador para obter a sessão de banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Professor(Base):
    __tablename__ = 'professores'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    materia = Column(String(50))

class Turma(Base):
    __tablename__ = 'turmas'
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(100), nullable=False)
    professor_id = Column(Integer, ForeignKey('professores.id'))
    ativo = Column(Boolean, default=True)

class Aluno(Base):
    __tablename__ = 'alunos'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    turma_id = Column(Integer, ForeignKey('turmas.id'))


Base.metadata.create_all(ENGINE)