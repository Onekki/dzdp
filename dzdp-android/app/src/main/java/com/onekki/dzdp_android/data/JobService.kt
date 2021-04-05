package com.onekki.dzdp_android.data

import retrofit2.Call
import retrofit2.http.*

interface JobService {

    @POST("/job")
    fun create(@Body config: Config): Call<Resp<Job>>

    @GET("/jobs/{job_id}")
    fun queryStatus(@Path("job_id") jobId: String): Call<Resp<Job>>
}