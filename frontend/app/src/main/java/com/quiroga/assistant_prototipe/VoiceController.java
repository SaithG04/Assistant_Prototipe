package com.quiroga.assistant_prototipe;

public interface VoiceController {
    void startRecording();
    void stopRecording();
    void sendAudioFile(String filePath);}
