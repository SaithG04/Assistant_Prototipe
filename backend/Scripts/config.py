import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Variables de entorno
DATABASE_URL = os.getenv('DATABASE_GEMINI_URL')
API_KEY = os.getenv('GEMINI_API_KEY')
API_TOKEN_DNI_RUC = os.getenv('API_TOKEN_DNI_RUC')

if not DATABASE_URL:
    raise ValueError("DATABASE_GEMINI_URL no está configurada. Asegúrate de que la variable de entorno esté definida.")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY no está configurada.")

if not API_TOKEN_DNI_RUC:
    raise ValueError("API_TOKEN_DNI_RUC no está configurada.")
