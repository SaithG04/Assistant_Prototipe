package com.quiroga.assistant_prototipe.api;

import java.util.Map;

import okhttp3.MultipartBody;
import retrofit2.Call;
import retrofit2.http.GET;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.Part;
import retrofit2.http.Path;

public interface FlaskApi {

    @Multipart
    @POST("/process_voice_command")
    Call<Map<String, Object>> speechToText(@Part MultipartBody.Part file);

    // Endpoint para obtener el horario de un día específico
    @GET("/get_schedule/{day_of_week}")
    Call<Map<String, Object>> getSchedule(@Path("day_of_week") String dayOfWeek);

    // Endpoint para obtener las tareas
    //@GET("/get_tasks")
    //Call<Map<String, Object>> getTasks();

    // Endpoint para obtener la información de un DNI
    @GET("/get_dni/{dni}")
    Call<Map<String, Object>> getDni(@Path("dni") String dni);
}
