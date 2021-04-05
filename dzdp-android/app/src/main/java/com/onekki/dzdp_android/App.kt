package com.onekki.dzdp_android

import android.app.Application
import com.onekki.dzdp_android.data.Singleton

class App : Application() {

    override fun onCreate() {
        super.onCreate()

        Singleton.context = this
    }
}