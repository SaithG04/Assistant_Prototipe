package com.quiroga.assistant_prototipe.ui;


import android.annotation.SuppressLint;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.quiroga.assistant_prototipe.R;
import com.quiroga.assistant_prototipe.VoiceManager;

import java.util.Locale;

public class VoiceUI extends AppCompatActivity implements TextToSpeech.OnInitListener {

    private static final int REQUEST_IMAGE_CAPTURE = 1;

    private VoiceManager voiceManager;
    private boolean isRecording = false;
    private TextToSpeech tts;
    ImageView imageView;

    @SuppressLint("SetTextI18n")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        Button btnRecordVoice = findViewById(R.id.btn_record_voice);
        TextView resultText = findViewById(R.id.result_text);
        imageView = findViewById(R.id.processed_image_view);

        // Inicializar Text-to-Speech
        tts = new TextToSpeech(this, this);

        // Inicializar VoiceManager con la API_URL
        voiceManager = new VoiceManager(this, getResources().getString(R.string.API_URL));

        // Configurar botón circular para alternar entre grabar y enviar audio
        btnRecordVoice.setOnClickListener(v -> {
            if (!isRecording) {
                voiceManager.startRecording();
                isRecording = true;
                btnRecordVoice.setText("Detener");  // Cambiar el texto a 'Detener'
            } else {
                voiceManager.stopRecording();
                isRecording = false;
                btnRecordVoice.setText("Hablar");  // Cambiar el texto a 'Hablar'
                voiceManager.sendAudioFile(voiceManager.getAudioFileName());  // Enviar el archivo después de grabar
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

    public void speakOut(String text) {
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, null);
    }

    public void loadProcessedImage(String url) {
        // Lógica para cargar y mostrar la imagen procesada en la interfaz
        //Glide.with(this).load(url).into(imageView);
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
        /*if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            Bundle extras = data.getExtras();
            Bitmap imageBitmap = (Bitmap) extras.get("data");

            // Convertir el bitmap en archivo y enviarlo al backend
            assert imageBitmap != null;
            voiceManager.sendImageToBackend(voiceManager.getImageFileName(), imageBitmap);
        }*/
    }

}