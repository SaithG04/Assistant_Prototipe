package com.quiroga.assistant_prototipe.ui;


import static android.content.ContentValues.TAG;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.speech.tts.TextToSpeech;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.FileProvider;

import com.quiroga.assistant_prototipe.R;
import com.quiroga.assistant_prototipe.VoiceManager;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Locale;

public class VoiceUI extends AppCompatActivity implements TextToSpeech.OnInitListener {

    private static final int REQUEST_IMAGE_CAPTURE = 1;
    private static final int REQUEST_GALLERY_IMAGE = 2;
    private static final int MAX_IMAGE_SIZE = 10000;

    private VoiceManager voiceManager;
    private boolean isRecording = false;
    private boolean isImageLoaded = false;
    private TextToSpeech tts;
    ImageView imageView;
    private Uri imageUri;
    private Uri photoUri;

    @SuppressLint("SetTextI18n")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        TextView resultText = findViewById(R.id.result_text);
        Button btnTakePhoto = findViewById(R.id.btn_take_photo);
        Button btnSelectFromGallery = findViewById(R.id.btn_select_gallery);
        Button btnRecordVoice = findViewById(R.id.btn_record_voice);
        Button btnLimpiar = findViewById(R.id.btn_limpiar);
        imageView = findViewById(R.id.processed_image_view);

        // Inicializar Text-to-Speech
        tts = new TextToSpeech(this, this);

        // Inicializar VoiceManager con la API_URL
        voiceManager = new VoiceManager(this, getResources().getString(R.string.API_URL));

        // Captura desde la cámara
        btnTakePhoto.setOnClickListener(v -> openCamera());

        // Selección desde la galería
        btnSelectFromGallery.setOnClickListener(v -> openGallery());

        // Botón para limpiar la imagen
        btnLimpiar.setOnClickListener(v -> cleanImageView());

        // Configurar botón circular para alternar entre grabar y enviar audio
        btnRecordVoice.setOnClickListener(v -> {
            if (!isRecording) {
                // Verificar si el TextToSpeech está hablando y detenerlo si es necesario
                if (tts.isSpeaking()) {
                    tts.stop();  // Detiene la reproducción de voz si está en curso
                }

                voiceManager.startRecording();
                isRecording = true;
                btnRecordVoice.setText("Detener");  // Cambiar el texto a 'Detener'
            } else {
                voiceManager.stopRecording();
                isRecording = false;
                btnRecordVoice.setText("Hablar");  // Cambiar el texto a 'Hablar'

                // Verificar si hay una imagen cargada y enviar la imagen junto con el audio
                if (isImageLoaded()) {
                    voiceManager.sendImageAndAudio(voiceManager.getAudioFileName(), imageUri);  // Enviar imagen y audio
                } else {
                    voiceManager.sendAudioFile(voiceManager.getAudioFileName());  // Enviar solo el audio
                }
            }
        });

    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            int result = tts.setLanguage(new Locale("es", "ES"));  // Configurar idioma en español
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                // Manejar el error si el idioma no está disponible
            } else {
                tts.setPitch(1.0f);  // Mantener tono normal
                tts.setSpeechRate(1.25f);  // Aumentar la velocidad de habla (50% más rápido)
            }
        }
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
        }
        super.onDestroy();
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            imageView.setImageURI(imageUri);
        }

        if (requestCode == REQUEST_GALLERY_IMAGE && resultCode == RESULT_OK && data != null) {
            imageUri = data.getData();  // Obtener el URI de la imagen seleccionada de la galería
            imageView.setImageURI(imageUri);  // Mostrar la imagen en el ImageView
        }
    }


    public void speakOut(String text) {
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
    }

    private void openCamera() {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        if (takePictureIntent.resolveActivity(getPackageManager()) != null) {
            File photoFile = null;
            try {
                photoFile = createImageFile();  // Crear el archivo de imagen
            } catch (IOException ex) {
                Log.e("VoiceUI", "Error al crear el archivo de imagen", ex);
            }
            if (photoFile != null) {
                imageUri = FileProvider.getUriForFile(this, "com.quiroga.assistant_prototipe.fileprovider", photoFile);
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, imageUri);
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
            }
        }
    }

    private void openGallery() {
        Intent pickPhotoIntent = new Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(pickPhotoIntent, REQUEST_GALLERY_IMAGE);
    }

    private boolean isImageLoaded() {
        if (imageView.getDrawable() != null && imageUri != null) {
            isImageLoaded = true;
            Log.d(TAG, "La imagen ya está cargada en el ImageView.");
            return true;
        } else {
            Log.d(TAG, "La imagen no está cargada en el ImageView.");
            isImageLoaded = false;
            return false;
        }
    }

    public void updateImageView(Bitmap bitmap) {
        // Verificar el tamaño de la imagen en bytes
        int bitmapByteCount = bitmap.getByteCount();

        // Limitar el tamaño máximo de la imagen en el ImageView
        if (bitmapByteCount > MAX_IMAGE_SIZE) {
            Log.w(TAG, "La imagen es demasiado grande para mostrarla en el ImageView. Solo se habilitará el botón de descarga.");

            // Ocultar el ImageView y mostrar solo el botón de descarga
            imageView.setVisibility(View.GONE);

            // Habilitar el botón de descarga para la imagen
            enableDownloadButton(bitmap);
        } else {
            // Mostrar la imagen en el ImageView y habilitar el botón de descarga
            imageView.setImageBitmap(bitmap);
            imageView.setVisibility(View.VISIBLE);
            enableDownloadButton(bitmap);
        }
    }

    private void enableDownloadButton(Bitmap bitmap) {
        Button downloadButton = findViewById(R.id.download_code_button);
        downloadButton.setVisibility(View.VISIBLE);

        // Configurar el listener para descargar y abrir la imagen en alta resolución
        downloadButton.setOnClickListener(view -> {
            // Guardar la imagen en la galería y obtener la URI de la imagen guardada
            Uri savedImageUri = saveBitmapToGallery(bitmap);

            if (savedImageUri != null) {
                // Crear un Intent para abrir la imagen con la aplicación de fotos predeterminada
                Intent intent = new Intent(Intent.ACTION_VIEW);
                intent.setDataAndType(savedImageUri, "image/jpeg");
                intent.setFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);

                // Utilizar FileProvider para construir un URI seguro
                Uri uriForFile = FileProvider.getUriForFile(this, "com.quiroga.assistant_prototipe.fileprovider", new File(savedImageUri.getPath()));

                // Cambiar el URI al generado por FileProvider
                intent.setData(uriForFile);

                // Verificar si existe una aplicación que pueda abrir imágenes
                if (intent.resolveActivity(getPackageManager()) != null) {
                    startActivity(intent);
                }

                // Ocultar el botón de descarga después de abrir la imagen
                downloadButton.setVisibility(View.GONE);
            } else {
                Toast.makeText(this, "No se pudo guardar la imagen", Toast.LENGTH_SHORT).show();
            }
        });
    }


    public Uri saveBitmapToGallery(Bitmap bitmap) {
        String imageFileName = "IMG_" + System.currentTimeMillis() + ".jpg";
        File storageDir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES) + "/AssistantPrototipe");

        if (!storageDir.exists() && !storageDir.mkdirs()) {
            Log.e(TAG, "Error al crear el directorio de imágenes");
            return null;
        }

        File imageFile = new File(storageDir, imageFileName);
        try (FileOutputStream fos = new FileOutputStream(imageFile)) {
            bitmap.compress(Bitmap.CompressFormat.JPEG, 100, fos);
            Toast.makeText(this, "Imagen guardada en la galería", Toast.LENGTH_LONG).show();

            // Añadir la imagen a la galería
            Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
            Uri contentUri = Uri.fromFile(imageFile);
            mediaScanIntent.setData(contentUri);
            sendBroadcast(mediaScanIntent);

            // Devolver el URI de la imagen guardada
            return contentUri;
        } catch (IOException e) {
            Log.e(TAG, "Error al guardar la imagen", e);
            return null;
        }
    }


    @Deprecated
    public String getRealPathFromURI(Uri uri) {
        String result = null;

        // Si la URI usa el esquema "content", intenta obtener el archivo usando el ContentResolver
        if ("content".equals(uri.getScheme())) {
            try (InputStream inputStream = getApplicationContext().getContentResolver().openInputStream(uri)) {
                // Crear un archivo temporal para copiar los datos del stream
                File tempFile = createTempFileFromInputStream(inputStream);
                result = tempFile.getAbsolutePath();
            } catch (Exception e) {
                Log.e(TAG, "Error al obtener la ruta desde el URI", e);
            }
        } else if ("file".equals(uri.getScheme())) {
            // Si el esquema es "file", simplemente devuelve la ruta del archivo
            result = uri.getPath();
        }

        return result;
    }

    private File createTempFileFromInputStream(InputStream inputStream) throws IOException {
        File tempFile = File.createTempFile("temp_image", ".jpg", getApplicationContext().getCacheDir());
        try (FileOutputStream outputStream = new FileOutputStream(tempFile)) {
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
        }
        return tempFile;
    }

    private File createImageFile() throws IOException {
        String imageFileName = "JPEG_" + System.currentTimeMillis() + "_";
        File storageDir = getExternalFilesDir(Environment.DIRECTORY_PICTURES);
        return File.createTempFile(imageFileName, ".jpg", storageDir);
    }

    private void cleanImageView(){
        imageView.setImageDrawable(null);
        isImageLoaded = false;
    }

}