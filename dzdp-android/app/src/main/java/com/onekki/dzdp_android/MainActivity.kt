package com.onekki.dzdp_android

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.text.util.Linkify
import android.view.Menu
import android.view.MenuItem
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import com.onekki.dzdp_android.data.Config
import com.onekki.dzdp_android.data.Job
import com.onekki.dzdp_android.data.Network
import com.onekki.dzdp_android.data.Resp
import com.onekki.dzdp_android.databinding.ActivityMainBinding
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding

    private val launcher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) {
        if (it.resultCode == RESULT_OK && it.data != null) {
            val userAgent = it.data!!.getStringExtra("User-Agent")
            val cookie = it.data!!.getStringExtra("Cookie")
            val config = Config(
                username = binding.tvUsername.text.toString(),
                email = binding.tvEmail.text.toString(),
                phone = binding.tvMobile.text.toString(),
                city = binding.tvCity.text.toString(),
                categoryIds = binding.tvCategoryIds.text.toString().split("\n"),
                headers = hashMapOf("User-Agent" to userAgent, "Cookie" to cookie)
            )
            Network.jobService().create(config).enqueue(object : Callback<Resp<Job>> {
                override fun onResponse(
                    call: Call<Resp<Job>>,
                    response: Response<Resp<Job>>
                ) {
                    if (response.isSuccessful) {
                        val resp = response.body()
                        resp?.let {
                            if (resp.isSuccessfully) {
                                binding.tvStatus.text = resp.data?.status
                                binding.tvResult.text = resp.data?.result
                            }
                            Toast.makeText(this@MainActivity, resp.msg, Toast.LENGTH_SHORT).show()
                        }
                    } else{
                        Toast.makeText(this@MainActivity, response.errorBody().toString(), Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Resp<Job>>, t: Throwable) {
                    Toast.makeText(this@MainActivity, t.message, Toast.LENGTH_SHORT).show()
                }
            })
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnStart.setOnClickListener {
            val intent = Intent(this, WebViewActivity::class.java)
            val url = "https://account.dianping.com/login?redir=http%3A%2F%2Fwww.dianping.com%2F"
            intent.data = Uri.parse("https://onekki.com/dzdp?action=create&url=$url")
            launcher.launch(intent)
        }

        binding.btnQuery.setOnClickListener {
            Network.jobService().queryStatus(binding.tvUsername.text.toString()).enqueue(object : Callback<Resp<Job>> {
                override fun onResponse(call: Call<Resp<Job>>, response: Response<Resp<Job>>) {
                    if (response.isSuccessful) {
                        val resp = response.body()
                        resp?.let {
                            if (resp.isSuccessfully) {
                                if (resp.data != null) {
                                    binding.tvStatus.text = resp.data.status
                                    binding.tvResult.text = resp.data.result

                                    binding.tvResult.isEnabled = resp.data.result != null &&
                                            resp.data.result.startsWith("http")
                                }
                            }
                            Toast.makeText(this@MainActivity, resp.msg, Toast.LENGTH_SHORT).show()
                        }
                    } else{
                        Toast.makeText(this@MainActivity, response.errorBody().toString(), Toast.LENGTH_SHORT).show()
                    }
                }

                override fun onFailure(call: Call<Resp<Job>>, t: Throwable) {
                    Toast.makeText(this@MainActivity, t.message, Toast.LENGTH_SHORT).show()
                }
            })
        }

        binding.tvDownload.text = Network.BASE_URL
            .plus("/download/")
            .plus(binding.tvCity.text.toString())
            .plus(".db")

        binding.tvResult.setOnClickListener {
            val intent = Intent(this, WebViewActivity::class.java)
            intent.data = Uri.parse(binding.tvResult.text.toString())
            launcher.launch(intent)
        }
    }
}