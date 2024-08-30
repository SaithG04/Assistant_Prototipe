import requests
from bs4 import BeautifulSoup
from tensorflow.keras.preprocessing.sequence import pad_sequences
from memory import cargar_modelo, cargar_tokenizer
import json
import subprocess
from difflib import SequenceMatcher

# Cargar el modelo y el tokenizer desde memory.py
modelo = cargar_modelo('modelo_clasificador.h5')
tokenizer = cargar_tokenizer('tokenizer.json')


def ejecutar_busqueda():
    consulta = input("\n¿Qué deseas buscar? ")
    buscar_informacion(consulta)


def buscar_informacion(consulta):
    consulta = consulta.replace(' ', '+')
    url = f"https://www.google.com/search?q={consulta}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al acceder a la búsqueda: {http_err}")
        return
    except requests.exceptions.RequestException as req_err:
        print(f"Error al realizar la solicitud: {req_err}")
        return

    soup = BeautifulSoup(response.text, 'lxml')
    resultados = soup.find_all('h3')
    enlaces = soup.find_all('a', href=True)

    links_validos = []
    titulos_validos = [resultado.get_text() for resultado in resultados[:5]]  # Mostrar solo 5 resultados

    for enlace in enlaces:
        href = enlace['href']
        if "/url?q=" in href:
            url_limpio = href.split("/url?q=")[1].split("&")[0]
            if url_limpio.startswith("http"):
                links_validos.append(url_limpio)

    if titulos_validos:
        while True:
            print(f"\nMostrando resultados:\n")
            for j, resultado in enumerate(titulos_validos, start=1):
                print(f"{j}. {resultado}")

            seleccion = input(
                "\nElige un número para obtener más información, escribe 'siguiente' para ver más resultados, o 'salir' para regresar al menú: ").strip().lower()

            if seleccion == 'siguiente':
                print("Ya has visto todos los resultados disponibles.")
                break
            elif seleccion == 'salir':
                print("Regresando al menú principal.")
                break
            else:
                try:
                    seleccion = int(seleccion)
                    if 1 <= seleccion <= len(titulos_validos):
                        indice_real = seleccion - 1
                        titulo_seleccionado = titulos_validos[indice_real]
                        url_correcto = links_validos[indice_real]
                        print(f"\nBuscando URL para el resultado seleccionado: {titulo_seleccionado}")
                        print(f"Evaluando URL: {url_correcto}")

                        # Preprocesar el título seleccionado y predecir con el modelo
                        secuencia = tokenizer.texts_to_sequences([titulo_seleccionado])
                        secuencia_padded = pad_sequences(secuencia, maxlen=50)
                        prediccion = modelo.predict(secuencia_padded)[0][0]

                        if prediccion > 0.5:
                            print(f"\nEl modelo predice que el URL es correcto.")
                            confirmacion = obtener_confirmacion("¿El modelo tiene razón? (s/n): ")
                            if confirmacion == 's':
                                mostrar_texto_pagina(url_correcto)
                            else:
                                proporcionar_url_correcto(titulo_seleccionado)
                        else:
                            print(f"\nEl modelo predice que el URL no es correcto.")
                            posible_url = buscar_en_datos_json(titulo_seleccionado)
                            if posible_url:
                                print(f"Se encontró una coincidencia en datos.json: {posible_url}")
                                confirmacion = obtener_confirmacion("¿El modelo tiene razón? (s/n): ")
                                if confirmacion == 's':
                                    decision = input(
                                        "¿Quieres usar alguna coincidencia, proporcionar un URL correcto, realizar otra búsqueda o salir al menú? (coincidencia/proporcionar/buscar/salir): ").strip().lower()
                                    if decision == 'coincidencia':
                                        mostrar_texto_pagina(posible_url)
                                    elif decision == 'proporcionar':
                                        proporcionar_url_correcto(titulo_seleccionado)
                                    elif decision == 'buscar':
                                        ejecutar_busqueda()
                                    elif decision == 'salir':
                                        print("Regresando al menú principal.")
                                        break
                                    else:
                                        print("Opción no válida.")
                                else:
                                    mostrar_texto_pagina(url_correcto)
                            else:
                                print("No se encontró una coincidencia en datos.json.")
                                proporcionar_url_correcto(titulo_seleccionado)
                        break
                    else:
                        print("Número fuera de rango.")
                except ValueError:
                    print("Entrada no válida.")
    else:
        print("No se encontraron resultados.")


def obtener_confirmacion(mensaje):
    while True:
        confirmacion = input(mensaje).strip().lower()
        if confirmacion in ['s', 'n']:
            return confirmacion
        else:
            print("Entrada no válida. Por favor, ingresa 's' para sí o 'n' para no.")


def proporcionar_url_correcto(titulo_seleccionado):
    decision = obtener_confirmacion("¿Quieres proporcionar un URL correcto? (s/n): ")
    if decision == 's':
        url_manual = input("Por favor, proporciona el URL correcto: ").strip()
        actualizar_datos_json(titulo_seleccionado, url_manual, 1)
        print("Reentrenando el modelo con el nuevo dato...")
        subprocess.run(['python', 'train_model.py'])
        print("El modelo ha sido reentrenado.")
    if nueva_busqueda_confirm():
        return


def nueva_busqueda_confirm():
    continuar = input("¿Deseas realizar otra búsqueda o regresar al menú? (buscar/menú): ").strip().lower()
    if continuar == 'buscar':
        ejecutar_busqueda()
        return False
    else:
        print("Regresando al menú principal.")
        return True


def buscar_en_datos_json(titulo_seleccionado):
    try:
        with open('datos.json', 'r') as file:
            datos = json.load(file)
            mejor_coincidencia = None
            mayor_ratio = 0.0
            for item in datos:
                ratio = SequenceMatcher(None, titulo_seleccionado, item['title']).ratio()
                if ratio > mayor_ratio:
                    mayor_ratio = ratio
                    mejor_coincidencia = item['url']
            return mejor_coincidencia if mayor_ratio > 0.7 else None  # Considera coincidencia si el ratio es mayor a 0.7
    except FileNotFoundError:
        print("El archivo datos.json no existe.")
        return None


def actualizar_datos_json(titulo, url, label):
    nuevo_dato = {"title": titulo, "url": url, "label": label}
    try:
        with open('datos.json', 'r+') as file:
            datos = json.load(file)
            datos.append(nuevo_dato)
            file.seek(0)
            json.dump(datos, file, indent=4)
        print("Nuevo dato agregado a datos.json")
    except FileNotFoundError:
        with open('datos.json', 'w') as file:
            json.dump([nuevo_dato], file, indent=4)
        print("Archivo datos.json creado y nuevo dato agregado.")


def mostrar_texto_pagina(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP al acceder a la página: {http_err}")
        return
    except requests.exceptions.RequestException as req_err:
        print(f"Error al realizar la solicitud a la página: {req_err}")
        return

    soup = BeautifulSoup(response.text, 'lxml')
    parrafos = soup.find_all('p')
    if parrafos:
        texto_pagina = "\n".join([parrafo.get_text() for parrafo in parrafos])
        print("\nTexto extraído de la página:")
        print(texto_pagina[:2000])
        print("\n...\nTexto truncado...")
    else:
        print("No se encontró contenido relevante en la página.")


# Ejemplo de uso
if __name__ == "__main__":
    ejecutar_busqueda()