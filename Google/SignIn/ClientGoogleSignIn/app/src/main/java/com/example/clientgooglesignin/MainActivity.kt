package com.example.clientgooglesignin

import android.content.Context
import android.os.Bundle
import android.util.Log
import android.widget.Button
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.credentials.PasswordCredential
import androidx.credentials.PublicKeyCredential
import androidx.credentials.exceptions.NoCredentialException
import androidx.lifecycle.lifecycleScope
import com.google.android.libraries.identity.googleid.GetSignInWithGoogleOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    companion object {
        const val WEB_CLIENT_ID = "935891679520-ur0sfnqsi9kchrtlhtmefdnsqup9771s.apps.googleusercontent.com"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val button: Button = findViewById(R.id.button)
        button.setOnClickListener {
            googleLogin(this)

            Toast.makeText(this, "Button clicked!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun googleLogin(context: Context) {
        val signInWithGoogleOption = GetSignInWithGoogleOption.Builder(WEB_CLIENT_ID)
            .build()

        val request: GetCredentialRequest = GetCredentialRequest.Builder()
            .addCredentialOption(signInWithGoogleOption)
            .build()

        val credentialManager = CredentialManager.create(context)

        lifecycleScope.launch {
            val loginFlow = flow {
                val result = credentialManager.getCredential(
                    context = context,
                    request = request
                )
                //**// Boom! NoCredentialException: No credentials available**

                emit(result.credential)
            }.catch { e ->
                if(e is NoCredentialException) {
                    Log.e("TAG", "loginSuccess NoCredentialException", e)
                }
            }.collect {
                loginSuccess(it)
            }
        }
    }

    private fun loginSuccess(credential: androidx.credentials.Credential) {
        when(credential) {
            is PasswordCredential -> {
                val password = credential.password
                val id = credential.id
                Log.e("TAG", "loginSuccess id: $id password: $password")
            }
            is GoogleIdTokenCredential -> {
                val idToken = credential.idToken
                Log.e("TAG", "loginSuccess idToken: $idToken")
            }
            is PublicKeyCredential -> {
                Log.e("TAG", "loginSuccess PublicKeyCredential")
            }
            is CustomCredential -> {

                if(credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL) {
                    try {
                        val googleIdTokenCredential = GoogleIdTokenCredential.createFrom(credential.data)
                        Log.e("TAG", "loginSuccess idToken: ${googleIdTokenCredential.idToken}  ${googleIdTokenCredential.displayName}")
                    } catch (e: GoogleIdTokenParsingException) {
                        e.printStackTrace()
                    }
                }
                else {
                    Log.e("TAG", "Unexcepted CustomCredential type: ${credential.type}")
                }
            }
        }
    }
}
