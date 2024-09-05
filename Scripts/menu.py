# File: menu.py

import json
import sys
import os
import socket
from search_google import buscar_informacion
from consults import consultar_por_dni, consultar_por_ruc

# Disable TensorFlow optimizations if necessary
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Configuration file for storing machine name
CONFIG_FILE = 'config.json'

# Function to load machine name
def cargar_nombre():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('nombre_maquina', socket.gethostname())  # Use default PC name if not set
    return socket.gethostname()  # Default to PC name if config doesn't exist

# Function to save machine name
def guardar_nombre(nombre):
    config = {'nombre_maquina': nombre}
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    print(f"Nombre de la máquina cambiado a: {nombre}")

# Load machine name
nombre_maquina = cargar_nombre()

def menu_principal():
    """Main menu for interacting with the assistant."""
    global nombre_maquina

    while True:
        print(f"\n=== HOLA, {nombre_maquina} ===")
        print("1. Búsqueda de Información")
        print("2. Consultar por DNI")
        print("3. Consultar por RUC")
        print("4. Predecir palabra")
        print("5. Cambiar nombre de la máquina")
        print("6. Salir")

        opcion = input("Por favor, elija una opción: ")

        if opcion == '1':
            consulta = input("¿Qué deseas buscar? ")
            buscar_informacion(consulta)
        elif opcion == '2':
            dni = input("Introduce el número de DNI: ").strip()
            resultado = consultar_por_dni(dni)
            if resultado:
                print("Datos de la persona:")
                print(json.dumps(resultado, indent=4))
            else:
                print("No se encontraron datos para el DNI proporcionado.")
        elif opcion == '3':
            ruc = input("Introduce el número de RUC: ").strip()
            resultado = consultar_por_ruc(ruc)
            if resultado:
                print("Datos de la empresa:")
                print(json.dumps(resultado, indent=4))
            else:
                print("No se encontraron datos para el RUC proporcionado.")
        elif opcion == '4':
            predecir_palabra()
        elif opcion == '5':
            nuevo_nombre = input("Introduce el nuevo nombre de la máquina: ").strip()
            if nuevo_nombre:
                guardar_nombre(nuevo_nombre)
                nombre_maquina = nuevo_nombre  # Update global variable
        elif opcion == '6':
            print("Hasta pronto...")
            sys.exit()
        else:
            print("Opción no válida. Por favor, elige nuevamente.")

def predecir_palabra():
    """Placeholder for the word prediction functionality."""
    print("\n--- Iniciando conversación con el asistente ---")
    while True:
        consulta = input("Tú: ")
        if consulta.lower() in ['salir', 'exit', 'quit']:
            print("Conversación terminada. Regresando al menú principal.")
            break
        # Dummy response for now
        palabra_sugerida = 'INTENTE MAS TARDE'  # Placeholder for future AI model integration
        print(f"Asistente: {palabra_sugerida}")

if __name__ == "__main__":
    menu_principal()