package com.quiroga.assistant_prototipe;

import android.graphics.Bitmap;

public interface VoiceController {
    void startRecording();
    void stopRecording();
    void sendAudioFile(String filePath);
    void sendImageToBackend(String filePath, Bitmap imageBitmap);
}
