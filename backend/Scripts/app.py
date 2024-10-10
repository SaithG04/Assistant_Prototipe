from flask import Flask, request, jsonify
from consults_reniec import get_info_by_dni, get_info_by_ruc
from search_in_google import search_information
from voice import speak, listen

app = Flask(__name__)


# Ruta para consultas por DNI
@app.route('/get_dni_info', methods=['POST'])
def get_dni_info():
    data = request.json
    dni = data.get('dni')
    if dni:
        info = get_info_by_dni(dni)
        return jsonify(info)
    return jsonify({'error': 'DNI no proporcionado'}), 400


# Ruta para consultas por RUC
@app.route('/get_ruc_info', methods=['POST'])
def get_ruc_info():
    data = request.json
    ruc = data.get('ruc')
    if ruc:
        info = get_info_by_ruc(ruc)
        return jsonify(info)
    return jsonify({'error': 'RUC no proporcionado'}), 400


# Ruta para búsqueda en Google
@app.route('/search_google', methods=['POST'])
def search_google():
    data = request.json
    consulta = data.get('consulta')
    if consulta:
        resultado = search_information(consulta)
        return resultado  # Ya que search_information devuelve un jsonify
    return jsonify({'error': 'Consulta no proporcionada'}), 400


# Ruta para convertir voz a texto
@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    # Aquí recibimos un archivo de audio desde el cliente (puede ser una app o Postman)
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró un archivo de audio'}), 400

    audio_file = request.files['file']

    # Usamos la función `listen` para convertir el audio en texto
    listened = listen(audio_file)

    if not listened:
        return jsonify({'error': 'No se pudo entender el audio, inténtalo nuevamente.'}), 400

    speak(listened)
    # Enviamos el texto de vuelta al cliente
    return jsonify({'texto': listened, 'mensaje': 'Texto recibido correctamente.'})


# Ejecución del servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
