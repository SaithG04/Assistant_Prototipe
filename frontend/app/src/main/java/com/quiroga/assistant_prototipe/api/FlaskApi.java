package com.quiroga.assistant_prototipe.api;

import com.quiroga.assistant_prototipe.entity.DniRequest;
import com.quiroga.assistant_prototipe.entity.RucRequest;

import java.util.Map;

import okhttp3.MultipartBody;
import okhttp3.ResponseBody;
import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;

public interface FlaskApi {

    @POST("/get_dni_info")
    Call<Map<String, Object>> getDniInfo(@Body DniRequest dniRequest);

    @POST("/get_ruc_info")
    Call<Map<String, Object>> getRucInfo(@Body RucRequest rucRequest);

    @Multipart
    @POST("/speech_to_text")
    Call<Map<String, Object>> speechToText(@Part MultipartBody.Part file);

    @Multipart
    @POST("/process_image")
    Call<Map<String, Object>> processImage(@Part MultipartBody.Part file);
}
