package com.onekki.dzdp_android.data

import com.google.gson.annotations.SerializedName
import retrofit2.http.HeaderMap
import retrofit2.http.Headers

data class Config(
    val username: String,
    val email: String,
    val phone: String,
    val city: String,

    @SerializedName("category_ids")
    val categoryIds: List<String>,
    val headers: Map<String, String?>? = null
)

data class Job(
    val id: String,
    val result: String?,
    val status: String,
    val error: String?
)