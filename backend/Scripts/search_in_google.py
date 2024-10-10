import requests
from bs4 import BeautifulSoup
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask import jsonify


# La función de predicción aún no se ha implementado
def predecir_url_correcta(titulo_seleccionado, modelo, tokenizer):
    secuencia = tokenizer.texts_to_sequences([titulo_seleccionado])
    secuencia_padded = pad_sequences(secuencia, maxlen=50)
    prediccion = modelo.predict(secuencia_padded)[0][0]
    return prediccion


def search_information(consult):
    # Reemplazar espacios en la consulta con "+"
    consult = consult.replace(' ', '+')
    url = f"https://www.google.com/search?q={consult}"
    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        # Si hay un error en la solicitud, retornamos un error en formato JSON
        return jsonify({'error': f"Error al realizar la solicitud: {e}"}), 500

    # Analizamos el HTML
    soup = BeautifulSoup(response.text, 'lxml')
    resultados = soup.find_all('h3')
    enlaces = soup.find_all('a', href=True)

    # Listas para almacenar los títulos y enlaces válidos
    links_validos = []
    titulos_validos = [resultado.get_text() for resultado in resultados[:5]]  # Mostrar solo 5 resultados

    for enlace in enlaces:
        href = enlace['href']
        if "/url?q=" in href:
            url_limpio = href.split("/url?q=")[1].split("&")[0]
            if url_limpio.startswith("http"):
                links_validos.append(url_limpio)

    # Retornar los títulos y enlaces como JSON
    if titulos_validos:
        # Devolvemos los resultados en formato JSON
        return jsonify({
            'resultados': [{'titulo': tit, 'link': link} for tit, link in zip(titulos_validos, links_validos[:5])]
        })
    else:
        # Si no hay resultados válidos
        return jsonify({'error': 'No se encontraron resultados'}), 404


def mostrar_texto_pagina(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        # En caso de error al obtener la página
        return jsonify({'error': f"Error al realizar la solicitud a la página: {e}"}), 500

    # Extraemos los párrafos del contenido de la página
    soup = BeautifulSoup(response.text, 'lxml')
    párrafos = soup.find_all('p')
    if párrafos:
        # Limitar el texto extraído a los primeros 2000 caracteres
        texto_pagina = "\n".join([párrafo.get_text() for párrafo in párrafos])
        return jsonify({
            'texto': texto_pagina[:2000],  # Limitar a los primeros 2000 caracteres
            'truncado': True  # Indicar que el texto fue truncado
        })
    else:
        return jsonify({'error': 'No se encontró contenido relevante en la página'}), 404
