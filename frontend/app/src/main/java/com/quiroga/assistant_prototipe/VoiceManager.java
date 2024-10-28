package com.quiroga.assistant_prototipe;

import android.content.Context;
import android.content.Intent;
import android.media.MediaRecorder;
import android.net.Uri;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.quiroga.assistant_prototipe.api.FlaskApi;
import com.quiroga.assistant_prototipe.ui.VoiceUI;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class VoiceManager implements VoiceController {

    private MediaRecorder mediaRecorder;
    private final String audioFileName;
    private final FlaskApi flaskApi;
    private final Context context;
    private static final String TAG = "VoiceManager";

    public VoiceManager(Context context, String apiUrl) {
        this.context = context;

        OkHttpClient okHttpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();

        // Configurar Retrofit
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(apiUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .client(okHttpClient)
                .build();

        flaskApi = retrofit.create(FlaskApi.class);

        // Configuración de grabación de audio
        audioFileName = Objects.requireNonNull(context.getExternalFilesDir(null)).getAbsolutePath() + "/recorded_audio.mp4";
    }

    @Override
    public void startRecording() {
        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);  // Formato MP4
        mediaRecorder.setOutputFile(audioFileName);  // Ruta del archivo
        mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);  // Códec AAC
        mediaRecorder.setAudioEncodingBitRate(128000);  // Bitrate para buena calidad de audio
        mediaRecorder.setAudioSamplingRate(44100);  // Tasa de muestreo de 44.1 kHz

        try {
            mediaRecorder.prepare();
            mediaRecorder.start();
            Toast.makeText(context, "Grabando...", Toast.LENGTH_SHORT).show();
        } catch (IOException e) {
            Log.e(TAG, "Fallo al preparar el MediaRecorder: " + e.getMessage());
        }
    }

    @Override
    public void stopRecording() {
        if (mediaRecorder != null) {
            mediaRecorder.stop();
            mediaRecorder.release();
            mediaRecorder = null;
            Toast.makeText(context, "Grabación detenida", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void sendAudioFile(String filePath) {
        File file = new File(filePath);
        if (!file.exists() || file.length() == 0) {
            Log.e(TAG, "El archivo no existe o está vacío: " + filePath);
            return;
        }

        RequestBody requestFile = RequestBody.create(MediaType.parse("audio/mp4"), file);
        MultipartBody.Part body = MultipartBody.Part.createFormData("file", file.getName(), requestFile);

        Call<Map<String, Object>> call = flaskApi.speechToText(body);
        call.enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(@NonNull Call<Map<String, Object>> call, @NonNull Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    Log.d(TAG, "Respuesta recibida: " + response.body().toString());

                    // Extraer el objeto 'texto', que es un mapa o un string
                    Object textoObject = response.body().get("texto");

                    if (textoObject instanceof String) {
                        // Si es texto normal (no relacionado a DNI)
                        String transcribedText = (String) textoObject;
                        handleText(transcribedText); // Manejar texto normal
                    } else if (textoObject instanceof Map) {
                        // Si es una respuesta con formato de DNI
                        Map<String, Object> textoMap = (Map<String, Object>) textoObject;

                        if (textoMap.containsKey("numeroDocumento")) {
                            // Si tiene un DNI, formatear la respuesta de DNI
                            String dniInfo = "El DNI " + textoMap.get("numeroDocumento") + " corresponde a " +
                                    textoMap.get("nombres") + " " +
                                    textoMap.get("apellidoPaterno") + " " +
                                    textoMap.get("apellidoMaterno") + ".";

                            TextView resultText = ((VoiceUI) context).findViewById(R.id.result_text);
                            resultText.setText(dniInfo);
                            ((VoiceUI) context).speakOut(dniInfo);
                        } else {
                            // Si no tiene información de DNI, manejarlo como un mensaje normal
                            Object messageObject = textoMap.get("message");
                            if (messageObject instanceof String) {
                                String message = (String) messageObject;
                                handleText(message); // Manejar texto normal
                            }
                        }

                        // Verificar si hay un código para descargar
                        Object codeObject = textoMap.get("code");
                        if (codeObject instanceof String && !((String) codeObject).isEmpty()) {
                            String code = (String) codeObject;
                            ((VoiceUI) context).speakOut("Puedes descargar el código si gustas.");

                            // Habilitar el botón de descarga
                            Button downloadCodeButton = ((VoiceUI) context).findViewById(R.id.download_code_button);
                            downloadCodeButton.setVisibility(View.VISIBLE);

                            // Descargar el código
                            downloadCodeButton.setOnClickListener(view -> {
                                saveCodeToFile(code);
                            });
                        } else {
                            Log.d(TAG, "No se recibió un código para mostrar o descargar.");
                        }
                    } else {
                        Log.e(TAG, "La respuesta no contiene un campo 'texto' válido.");
                        ((VoiceUI) context).speakOut("No se ha recibido una respuesta válida.");
                    }
                } else {
                    Log.e(TAG, "Error al transcribir: " + response.code() + ", " + response.errorBody());
                    ((VoiceUI) context).speakOut("Hubo un error al procesar tu solicitud.");
                }
            }

            @Override
            public void onFailure(@NonNull Call<Map<String, Object>> call, @NonNull Throwable t) {
                Log.e(TAG, "Fallo en la conexión: " + t.getMessage(), t);
                ((VoiceUI) context).speakOut("No me he podido conectar al servidor...");
            }
        });
    }

    private void handleText(String transcribedText) {
        // Aquí procesas el texto transcrito como un string normal
        TextView resultText = ((VoiceUI) context).findViewById(R.id.result_text);
        resultText.setText(transcribedText);

        // Decir el texto por voz
        ((VoiceUI) context).speakOut(transcribedText);
    }


    public String getAudioFileName() {
        return audioFileName;
    }

    private void saveCodeToFile(String code) {
        try {
            // Ruta donde se guardará el archivo .txt
            File path = context.getExternalFilesDir(null);
            File file = new File(path, "codigo.txt");

            // Escribir el código en el archivo
            FileOutputStream stream = new FileOutputStream(file);
            stream.write(code.getBytes());
            stream.close();

            // Informar al usuario que el archivo se ha guardado
            ((VoiceUI) context).speakOut("El código ha sido guardado. Abriendo el archivo...");
            Toast.makeText(context, "En: " + file.getAbsolutePath(), Toast.LENGTH_LONG).show();
            Log.d(TAG, "Código guardado en: " + file.getAbsolutePath());

            // Crear un Intent para abrir el archivo
            Intent intent = new Intent(Intent.ACTION_VIEW);
            intent.setDataAndType(Uri.fromFile(file), "text/plain");
            intent.setFlags(Intent.FLAG_ACTIVITY_NO_HISTORY);

            // Verificar si existe una aplicación que pueda abrir archivos de texto
            if (intent.resolveActivity(context.getPackageManager()) != null) {
                context.startActivity(intent);
            } else {
                // Si no hay una aplicación disponible, mostrar un mensaje adecuado
                ((VoiceUI) context).speakOut("No tienes una aplicación para abrir archivos de texto, pero el código está guardado.");
                Toast.makeText(context, "No tienes una aplicación para abrir archivos de texto, pero el código está guardado.", Toast.LENGTH_SHORT).show();

            }

            // Ocultar el botón de descarga después de abrir el archivo
            Button downloadCodeButton = ((VoiceUI) context).findViewById(R.id.download_code_button);
            downloadCodeButton.setVisibility(View.GONE);

        } catch (IOException e) {
            Log.e(TAG, "Error al guardar el archivo de código: " + e.getMessage());
            ((VoiceUI) context).speakOut("Hubo un error al guardar el código.");
        }
    }

}
