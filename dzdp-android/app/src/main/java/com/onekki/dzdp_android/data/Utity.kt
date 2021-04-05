package com.onekki.dzdp_android.data

import android.app.Application
import android.content.Context

data class Resp<out T>(val code: Int, val msg: String?, val data: T?) {
    val isSuccessfully: Boolean
        get() = code == 0
}

sealed class Result<out T> {
    object Loading : Result<Nothing>()
    class Success<T>(val data: T?) : Result<T>()
    class Failure(val msg: String?) : Result<Nothing>()
}

object Singleton {
    lateinit var context: Application
}