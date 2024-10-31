package com.quiroga.assistant_prototipe;

import android.net.Uri;

public interface VoiceController {
    void startRecording();
    void stopRecording();
    void sendAudioFile(String filePath);
    void sendImageAndAudio(String audioFilePath, Uri imageUri);
}
