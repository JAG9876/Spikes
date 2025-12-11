package com.example.clientgooglesignin

import android.content.Context
import androidx.credentials.CredentialManager
/*
import androidx.credentials.GetCredentialRequest
import androidx.credentials.GetCredentialResponse
import androidx.credentials.exceptions.GetCredentialException
import androidx.credentials.PasswordCredential
import androidx.credentials.GoogleIdTokenCredential
import androidx.credentials.GetPasswordOption
import androidx.credentials.GetGoogleIdTokenOption
*/

class MyAuthManager(private val context: Context) {

    private val credentialManager = CredentialManager.create(context)

    suspend fun getCredentialManager(): CredentialManager {
        return credentialManager;
    }
    /*
    suspend fun signInUser(): CredentialResult {
        val request = GetCredentialRequest(
            credentialOptions = listOf(
                GetPasswordOption(), // Option to retrieve a saved password
                GetGoogleIdTokenOption(
                    serverClientId = "YOUR_SERVER_CLIENT_ID", // Replace with your server client ID
                    filterByAuthorizedAccounts = true,
                    associateLinkedAccounts = true
                ) // Option to retrieve a Google ID token
            )
        )

        return try {
            val response = credentialManager.getCredential(request)
            when (val credential = response.credential) {
                is PasswordCredential -> {
                    // User signed in with a saved password
                    CredentialResult.Success(credential.id, credential.password)
                }
                is GoogleIdTokenCredential -> {
                    // User signed in with a Google ID token
                    CredentialResult.Success(credential.id, credential.idToken)
                }
                else -> CredentialResult.Error("Unknown credential type")
            }
        } catch (e: GetCredentialException) {
            CredentialResult.Error("Failed to get credential: ${e.message}")
        }
    }

    sealed class CredentialResult {
        data class Success(val userId: String, val tokenOrPassword: String) : CredentialResult()
        data class Error(val message: String) : CredentialResult()
    }

     */
}