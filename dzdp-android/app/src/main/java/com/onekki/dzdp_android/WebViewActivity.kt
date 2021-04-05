package com.onekki.dzdp_android

import android.annotation.SuppressLint
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.webkit.CookieManager
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isGone
import com.onekki.dzdp_android.databinding.ActivityWebViewBinding
import org.json.JSONObject

class WebViewActivity : AppCompatActivity() {

    private val TAG = "Dzdp.WebView"

    private val USER_AGENT_DESKTOP =
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding = ActivityWebViewBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.webView.settings.userAgentString = USER_AGENT_DESKTOP
        binding.webView.settings.javaScriptEnabled = true
        binding.webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                binding.pbWebView.isGone = true
            }
        }

        intent?.let {
            val uri = intent.data

            Log.d(TAG, "onCreate: uri - $uri")
            val action = uri?.getQueryParameter("action")
            val url = uri?.getQueryParameter("url")
            Log.d(TAG, "onCreate: $action")
            when (action) {
                "create" -> {
                    url?.let { binding.webView.loadUrl(url) }
                }
                "update" -> CookieManager.getInstance().removeAllCookies {
                    url?.let { binding.webView.loadUrl(url) }
                }
                "validate" -> {
                    val headers = uri.getQueryParameter("headers")
                    Log.d(TAG, "onCreate: headers - $headers")
                    val jo = JSONObject(headers!!)
                    val userAgent = jo.opt("User-Agent") as String
                    val cookie = jo.opt("Cookie") as String
                    binding.webView.settings.userAgentString = userAgent
                    CookieManager.getInstance().setCookie(url, cookie) {
                        url?.let { binding.webView.loadUrl(url) }
                    }
                }
                else -> finish()
            }
        }
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.web_view, menu)
        return super.onCreateOptionsMenu(menu)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if (item.itemId == R.id.action_ok) {
            val uri = intent.data
            val url = uri?.getQueryParameter("url")
            val cookieManager = CookieManager.getInstance()
            val cookie = cookieManager.getCookie(url)
            Log.d(TAG, "onOptionsItemSelected: $cookie")

            val result = Intent()
            result.putExtra("User-Agent", USER_AGENT_DESKTOP)
            result.putExtra("Cookie", cookie)
            setResult(RESULT_OK, result)
            finish()
        }
        return super.onOptionsItemSelected(item)
    }
}