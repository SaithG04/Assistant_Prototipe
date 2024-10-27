from flask import Flask, request, jsonify, send_file
from voice import convert_audio_to_wav, transcribe_audio, dispatch_command
from image_processing import process_image_for_edges

app = Flask(__name__)

@app.route('/speech_to_text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró un archivo de audio'}), 400

    audio_file = request.files['file']
    file_ext = audio_file.filename.split('.')[-1].lower()

    print(f"Tipo de archivo recibido: {audio_file.content_type}")
    print(f"Extensión de archivo: {file_ext}")

    if file_ext not in ['wav', 'mp3', 'mp4', 'ogg', 'flac']:
        return jsonify({'error': 'Formato de archivo no compatible. Se espera uno de los siguientes: wav, mp3, mp4, ogg, flac.'}), 400

    try:
        # Convertir el archivo a WAV si es necesario
        wav_audio = convert_audio_to_wav(audio_file, file_ext)

        # Transcribir el audio a texto
        transcribed_text = transcribe_audio(wav_audio)
        if not transcribed_text:
            return jsonify({'error': 'No se pudo entender el audio, inténtalo nuevamente.'}), 400

        # Despachar el comando a la función correspondiente
        resultado = dispatch_command(transcribed_text)
        print(f"Resultado del comando: {resultado}")

        return jsonify({'texto': resultado, 'mensaje': 'Texto procesado correctamente.'})

    except Exception as e:
        print(f"Error en el procesamiento: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@app.route('/process_image', methods=['POST'])
def process_image():
    """
    Endpoint que recibe una imagen, la procesa (detecta bordes) y devuelve la imagen procesada.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo.'}), 400

    # Leer la imagen enviada
    file = request.files['file']

    try:
        # Procesar la imagen usando la lógica separada
        processed_image = process_image_for_edges(file.stream)

        # Enviar la imagen procesada de vuelta
        return send_file(processed_image, mimetype='image/png')

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error al procesar la imagen: {str(e)}'}), 500


# Ejecución del servidor Flask
if __name__ == '__main__':
    #app.run(host=os.getenv('HOST'), port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
