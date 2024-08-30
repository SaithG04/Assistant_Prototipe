import sys
from search_google import ejecutar_busqueda
from consults import consultar_por_dni, consultar_por_ruc
import os
import json

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

def menu_principal():
    while True:
        print("\n=== BIENVENIDO ===")
        print("1. Búsqueda de Información")
        print("2. Consultar por DNI")
        print("3. Consultar por RUC")
        print("4. Salir")
        print("prototipe v1.0")

        opcion = input("Por favor, elija una opción: ")

        if opcion == '1':
            ejecutar_busqueda()
        elif opcion == '2':
            dni = input("Introduce el número de DNI: ").strip()
            resultado = consultar_por_dni(dni)
            if resultado:
                print("Datos de la persona:")
                print(json.dumps(resultado, indent=4))
            else:
                print("No se pudo encontrar información para el DNI proporcionado.")
        elif opcion == '3':
            ruc = input("Introduce el número de RUC: ").strip()
            resultado = consultar_por_ruc(ruc)
            if resultado:
                print("Datos de la empresa:")
                print(json.dumps(resultado, indent=4))
            else:
                print("No se pudo encontrar información para el RUC proporcionado.")
        elif opcion == '4':
            print("Hasta pronto...")
            sys.exit()
        else:
            print("Opción no válida. Por favor, elige nuevamente.")

if __name__ == "__main__":
    menu_principal()