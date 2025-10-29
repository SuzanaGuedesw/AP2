from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

ENGINE = create_engine('sqlite:///atividades.db', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Atividade(Base):
    __tablename__ = 'atividades'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    peso = Column(Float)
    
    turma_id = Column(Integer)
    professor_id = Column(Integer)

class Nota(Base):
    __tablename__ = 'notas'
    id = Column(Integer, primary_key=True, index=True)
    nota = Column(Float, nullable=False)
    aluno_id = Column(Integer)
    atividade_id = Column(Integer)

Base.metadata.create_all(ENGINE)