import json
import sys
import os
import socket
from search_google import buscar_informacion
from consults import consultar_por_dni, consultar_por_ruc
# from predecir_siguiente_palabra import predecir_siguiente_palabra

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Ruta del archivo de configuración para almacenar el nombre
config_file = 'config.json'

# Función para cargar el nombre de la máquina
def cargar_nombre():
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
            return config.get('nombre_maquina', socket.gethostname())  # Usar nombre de la PC por defecto
    return socket.gethostname()  # Nombre de la PC si no existe archivo de configuración

# Función para guardar el nombre de la máquina
def guardar_nombre(nombre):
    config = {'nombre_maquina': nombre}
    with open(config_file, 'w') as f:
        json.dump(config, f)
    print(f"Nombre de la máquina cambiado a: {nombre}")

# Nombre de la máquina
nombre_maquina = cargar_nombre()

def menu_principal():
    global nombre_maquina  # Coloca esto al inicio de la función

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
        elif opcion == '3':
            ruc = input("Introduce el número de RUC: ").strip()
            resultado = consultar_por_ruc(ruc)
            if resultado:
                print("Datos de la empresa:")
                print(json.dumps(resultado, indent=4))
        elif opcion == '4':
            predecir_palabra()
        elif opcion == '5':
            nuevo_nombre = input("Introduce el nuevo nombre de la máquina: ").strip()
            if nuevo_nombre:
                guardar_nombre(nuevo_nombre)
                nombre_maquina = nuevo_nombre  # Actualiza la variable global
        elif opcion == '6':
            print("Hasta pronto...")
            sys.exit()
        else:
            print("Opción no válida. Por favor, elige nuevamente.")

def predecir_palabra():
    print("\n--- Iniciando conversación con el asistente ---")
    while True:
        consulta = input("Tú: ")
        if consulta.lower() in ['salir', 'exit', 'quit']:
            print("Conversación terminada. Regresando al menú principal.")
            break
        palabra_sugerida = 'INTENTE MAS TARDE'  # predecir_siguiente_palabra(consulta)
        print(f"Asistente: {palabra_sugerida}")

if __name__ == "__main__":
    menu_principal()
