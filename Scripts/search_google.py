import requests
from bs4 import BeautifulSoup
from tensorflow.keras.preprocessing.sequence import pad_sequences

def predecir_url_correcta(titulo_seleccionado, modelo, tokenizer):
    secuencia = tokenizer.texts_to_sequences([titulo_seleccionado])
    secuencia_padded = pad_sequences(secuencia, maxlen=50)
    prediccion = modelo.predict(secuencia_padded)[0][0]
    return prediccion

def buscar_informacion(consulta):
    consulta = consulta.replace(' ', '+')
    url = f"https://www.google.com/search?q={consulta}"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
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

                        for links_valido in links_validos:
                            print(links_valido)

                        url = links_validos[indice_real]
                        print(f"\nBuscando URL para el resultado seleccionado: {titulo_seleccionado}")
                        print(f"Evaluando URL: {url}")
                        confirm = input("¿Desea acceder al enlace? (y/n)")
                        if(confirm == 'y'):
                            mostrar_texto_pagina(url)
                        else:
                            break
                    else:
                        print("Número fuera de rango.")
                except ValueError:
                    print("Entrada no válida.")
    else:
        print("No se encontraron resultados.")
        return

def mostrar_texto_pagina(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud a la página: {e}")
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

if __name__ == "__main__":
    consulta = input("Ingresa tu consulta: ")
    buscar_informacion(consulta)