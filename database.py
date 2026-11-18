# Conexión a la base de datos SQLite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#aca esta la base de datos
DATABASE_URL = "sqlite:///./helpdesk.db"

#engine es el motor
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Abre una sesión por cada petición y la cierra al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
