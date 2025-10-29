from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import date

ENGINE = create_engine('sqlite:///reservas.db', echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=ENGINE, autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Reserva(Base):
    __tablename__ = 'reservas'
    id = Column(Integer, primary_key=True, index=True)
    num_sala = Column(String(10), nullable=False)
    data_reserva = Column(Date, default=date.today)
   
    turma_id = Column(Integer)

Base.metadata.create_all(ENGINE)