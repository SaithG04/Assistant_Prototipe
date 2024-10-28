from sqlalchemy import create_engine, Column, Integer, String, Text, Enum, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL

# Conexión a la base de datos
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)

Base = declarative_base()


# Modelo para el historial de conversación
class ConversationHistory(Base):
    __tablename__ = 'conversation_history'
    id = Column(Integer, primary_key=True)
    role = Column(Enum('user', 'assistant'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")


# Modelo para el horario
class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, primary_key=True)
    subject = Column(String(255), nullable=False)
    day_of_week = Column(Enum('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    location = Column(String(255), nullable=True)


# Modelo para las tareas
class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    due_date = Column(TIMESTAMP, nullable=False)


# Crear las tablas si no existen
Base.metadata.create_all(engine)


# Función para agregar un horario
def add_schedule(subject, day_of_week, start_time, end_time, location=None):
    session = Session()
    try:
        new_schedule = Schedule(subject=subject, day_of_week=day_of_week, start_time=start_time, end_time=end_time,
                                location=location)
        session.add(new_schedule)
        session.commit()
        print("Horario agregado exitosamente.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error al agregar el horario: {str(e)}")
    finally:
        session.close()


# Función para obtener el horario por día
def get_schedule_by_day(day_of_week):
    session = Session()
    try:
        schedule = session.query(Schedule).filter_by(day_of_week=day_of_week).all()
        return schedule if schedule else []
    except SQLAlchemyError as e:
        print(f"Error al consultar el horario: {str(e)}")
        return []
    finally:
        session.close()


# Función para guardar el historial en la base de datos
def save_message_to_db(role, content):
    session = Session()
    new_message = ConversationHistory(role=role, content=content)
    session.add(new_message)
    session.commit()
