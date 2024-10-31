from sqlalchemy.exc import SQLAlchemyError
from db import Task, Session
import logging


# Función para agregar una nueva tarea
def add_task(name, description, due_date, status="pendiente"):
    session = Session()
    try:
        new_task = Task(name=name, description=description, due_date=due_date, status=status)
        session.add(new_task)
        session.commit()
        logging.debug(f"Tarea '{name}' creada exitosamente con estado '{status}'.")
        return True
    except SQLAlchemyError as e:
        session.rollback()
        logging.error(f"Error al crear la tarea: {str(e)}")
        return False
    finally:
        session.close()


# Función para listar todas las tareas
def list_tasks():
    session = Session()
    try:
        tasks = session.query(Task).all()
        if tasks:
            task_list = [
                {
                    'name': task.name,
                    'description': task.description,
                    'due_date': task.due_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                for task in tasks
            ]
            return task_list
        else:
            logging.info("No se encontraron tareas.")
            return []
    except SQLAlchemyError as e:
        logging.error(f"Error al consultar las tareas: {str(e)}")
        return []
    finally:
        session.close()
