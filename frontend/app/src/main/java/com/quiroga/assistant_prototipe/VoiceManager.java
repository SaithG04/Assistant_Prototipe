package com.quiroga.assistant_prototipe;

import android.content.Context;
import android.graphics.Bitmap;
import android.media.MediaRecorder;
import android.util.Log;
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

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class VoiceManager implements VoiceController {

    private MediaRecorder mediaRecorder;
    private final String audioFileName, imageFileName;
    private final FlaskApi flaskApi;
    private final Context context;
    private static final String TAG = "VoiceManager";

    public VoiceManager(Context context, String apiUrl) {
        this.context = context;

        // Configurar Retrofit
        Retrofit retrofit = new Retrofit.Builder()
                .baseUrl(apiUrl)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        flaskApi = retrofit.create(FlaskApi.class);

        // Configuración de grabación de audio
        audioFileName = Objects.requireNonNull(context.getExternalFilesDir(null)).getAbsolutePath() + "/recorded_audio.mp4";
        imageFileName = Objects.requireNonNull(context.getExternalFilesDir(null)).getAbsolutePath() + "/processed_image.jpg";
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
                    String transcribedText = (String) response.body().get("texto");
                    // Mostrar el texto y generar respuesta por voz
                    TextView resultText = ((VoiceUI) context).findViewById(R.id.result_text);
                    resultText.setText(transcribedText);

                    // Generar la respuesta por voz
                    ((VoiceUI) context).speakOut(transcribedText);
                } else {
                    Log.e(TAG, "Error al transcribir: " + response.code());
                }
            }

            @Override
            public void onFailure(@NonNull Call<Map<String, Object>> call, @NonNull Throwable t) {
                Log.e(TAG, "Fallo en la conexión: " + t.getMessage());
                ((VoiceUI) context).speakOut("Verifica tu conexión a internet.");
            }
        });
    }

    @Override
    public void sendImageToBackend(String filePath, Bitmap imageBitmap) {
        // Guardar el bitmap como archivo en el almacenamiento local
        File imageFile = new File(filePath);
        try (FileOutputStream fos = new FileOutputStream(imageFile)) {
            imageBitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Crear la solicitud Multipart para enviar la imagen
        RequestBody requestFile = RequestBody.create(MediaType.parse("image/jpeg"), imageFile);
        MultipartBody.Part body = MultipartBody.Part.createFormData("file", imageFile.getName(), requestFile);

        Call<Map<String, Object>> call = flaskApi.processImage(body);
        call.enqueue(new Callback<Map<String, Object>>() {
            @Override
            public void onResponse(@NonNull Call<Map<String, Object>> call, @NonNull Response<Map<String, Object>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    // Manejar la respuesta del backend (por ejemplo, mostrar la imagen procesada)
                    String processedImageUrl = (String) response.body().get("processed_image_url");
                    // Aquí se carga y muestra la imagen procesada en el ImageView
                    ((VoiceUI) context).loadProcessedImage(processedImageUrl);
                }
            }

            @Override
            public void onFailure(@NonNull Call<Map<String, Object>> call, @NonNull Throwable t) {
                Log.e(TAG, "Error al procesar la imagen: " + t.getMessage());
                Toast.makeText(context, "Error al procesar la imagen", Toast.LENGTH_SHORT).show();
            }
        });
    }

    public String getAudioFileName() {
        return audioFileName;
    }

    public String getImageFileName(){
        return imageFileName;
    }

}
