import sys
from search_google import ejecutar_busqueda
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'



def menu_principal():
    while True:
        print("\n=== BIENVENIDO ===")
        print("1. Búsqueda de Información")
        print("2. Otra Función (Placeholder)")
        print("3. Salir")
        print("prototipe v1.0")

        opcion = input("Por favor, elija una opción: ")

        if opcion == '1':
            ejecutar_busqueda()
        elif opcion == '2':
            print("Funcionalidad en desarrollo...")
        elif opcion == '3':
            print("Hasta pronto...")
            sys.exit()
        else:
            print("Opción no válida. Por favor, elige nuevamente.")


if __name__ == "__main__":
    menu_principal()
