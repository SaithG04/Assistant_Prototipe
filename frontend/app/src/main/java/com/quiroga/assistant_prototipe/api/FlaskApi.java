package com.quiroga.assistant_prototipe.api;

import java.util.Map;

import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.*;

public interface FlaskApi {

    @Multipart
    @POST("/process_voice_command")
    Call<Map<String, Object>> sendCommandVoice(@Part MultipartBody.Part file);

    @Multipart
    @POST("/process_image_and_audio")
    Call<ResponseBody> sendImageAndAudio(@Part MultipartBody.Part audio, @Part MultipartBody.Part image);
}
