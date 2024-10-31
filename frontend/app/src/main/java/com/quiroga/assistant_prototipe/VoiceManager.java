package com.quiroga.assistant_prototipe;

import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;

import com.quiroga.assistant_prototipe.api.FlaskApi;
import com.quiroga.assistant_prototipe.ui.VoiceUI;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.RequestBody;
import okhttp3.ResponseBody;
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
                .connectTimeout(60, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)
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

        Call<Map<String, Object>> call = flaskApi.sendCommandVoice(body);
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
                        }
                    } else {
                        Log.e(TAG, "La respuesta no contiene un campo 'texto' válido.");
                        ((VoiceUI) context).speakOut("No se ha recibido una respuesta válida.");
                    }
                } else {
                    try {
                        String errorBody = response.errorBody().string();  // Extrae el cuerpo del error como String

                        // Parsear el JSON para extraer el campo "error"
                        JSONObject jsonObject = new JSONObject(errorBody);
                        String errorMessage = jsonObject.getString("error");  // Obtener el contenido de "error"

                        Log.e(TAG, "Error al transcribir: " + response.code() + ", Mensaje: '" + errorMessage + "'");
                        handleText(errorMessage);
                    } catch (IOException | JSONException e) {
                        Log.e(TAG, "Error al procesar la respuesta del servidor: " + e.getMessage(), e);
                    }
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

    @Override
    public void sendImageAndAudio(String audioFilePath, Uri imageUri) {
        File audioFile = new File(audioFilePath);
        if (!audioFile.exists() || audioFile.length() == 0) {
            Log.e(TAG, "El archivo de audio no existe o está vacío.");
            return;
        }

        // Crea el cuerpo de audio
        RequestBody requestFileAudio = RequestBody.create(MediaType.parse("audio/mp4"), audioFile);
        MultipartBody.Part audioBody = MultipartBody.Part.createFormData("audio", audioFile.getName(), requestFileAudio);

        // Convertir el Uri en InputStream sin intentar obtener una ruta física
        try {
            InputStream inputStream = context.getContentResolver().openInputStream(imageUri);
            RequestBody requestFileImage = null;
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
                requestFileImage = RequestBody.create(MediaType.parse("image/jpeg"), inputStream.readAllBytes());
            }
            MultipartBody.Part imageBody = MultipartBody.Part.createFormData("image", "image.jpg", requestFileImage);

            // Llamada a la API
            Call<ResponseBody> call = flaskApi.sendImageAndAudio(audioBody, imageBody);
            call.enqueue(new Callback<ResponseBody>() {
                @Override
                public void onResponse(@NonNull Call<ResponseBody> call, @NonNull Response<ResponseBody> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        Log.d(TAG, "Respuesta recibida.");

                        // Procesa la imagen y el mensaje
                        InputStream inputStream = response.body().byteStream();
                        Bitmap processedBitmap = BitmapFactory.decodeStream(inputStream);
                        ((VoiceUI) context).updateImageView(processedBitmap);  // Actualiza la imagen
                        String message = response.headers().get("message");
                        if (message != null) {
                            Log.d(TAG, "Mensaje recibido: " + message);
                            handleText(message);
                        }else {
                            
                            Log.e(TAG, "No se recibió un mensaje en la respuesta.");
                            handleText("No se ha recibido una respuesta válida.");
                        }
                    } else {
                        Log.e(TAG, "Error al procesar el comando: " + response.code());
                        ((VoiceUI) context).speakOut("Hubo un error al procesar tu solicitud.");
                    }
                }

                @Override
                public void onFailure(@NonNull Call<ResponseBody> call, @NonNull Throwable t) {
                    Log.e(TAG, "Fallo en la conexión: " + t.getMessage(), t);
                    handleText("No me he podido conectar al servidor...");
                }
            });
        } catch (IOException e) {
            Log.e(TAG, "Error al leer la imagen desde el URI", e);
            handleText("Hubo un error al leer la imagen.");
        }
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

    @Deprecated
    public String getRealPathFromURI(Uri uri) {
        String[] projection = {MediaStore.Images.Media.DATA};
        Cursor cursor = context.getContentResolver().query(uri, projection, null, null, null);
        if (cursor != null) {
            int column_index = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA);
            cursor.moveToFirst();
            String path = cursor.getString(column_index);
            cursor.close();
            return path;
        } else {
            return uri.getPath();  // Si no se puede obtener, devuelve la ruta del URI
        }
    }

    public void saveBitmapToGallery(Bitmap bitmap) {
        String savedImagePath = null;
        String imageFileName = "IMG_" + System.currentTimeMillis() + ".jpg";
        File storageDir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES) + "/AssistantPrototipe");

        boolean success = true;
        if (!storageDir.exists()) {
            success = storageDir.mkdirs();  // Crea el directorio si no existe
        }

        if (success) {
            File imageFile = new File(storageDir, imageFileName);
            try {
                FileOutputStream fos = new FileOutputStream(imageFile);
                bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);  // Guarda la imagen
                fos.close();

                // Añadir la imagen a la galería
                Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
                Uri contentUri = Uri.fromFile(imageFile);
                mediaScanIntent.setData(contentUri);
                context.sendBroadcast(mediaScanIntent);

                Toast.makeText(context, "Imagen guardada en la galería", Toast.LENGTH_LONG).show();
            } catch (IOException e) {
                Log.e(TAG, "Error al guardar la imagen", e);
            }
        }
    }

    // Método para actualizar la imagen procesada en el ImageView
    private void updateImageFromResponse(ResponseBody responseBody) {
        // Convertir la respuesta a un Bitmap
        InputStream inputStream = responseBody.byteStream();
        Bitmap processedBitmap = BitmapFactory.decodeStream(inputStream);

        // Actualizar el ImageView con la nueva imagen procesada
        ((VoiceUI) context).updateImageView(processedBitmap);

        // Guardar la imagen procesada en la galería si es necesario
        saveBitmapToGallery(processedBitmap);
    }

}
