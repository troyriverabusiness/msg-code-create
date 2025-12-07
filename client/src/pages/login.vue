<template>
  <div class="login-page">
    <v-container class="login-container">
      <v-row justify="center" align="center" style="min-height: 80vh;">
        <v-col cols="12" sm="8" md="5" lg="4">
          <v-card class="login-card" elevation="4">
            <v-card-title class="login-title text-center">
              <h2>Anmelden</h2>
            </v-card-title>
            
            <v-card-text class="login-form">
              <v-form ref="loginForm" v-model="valid">
                <v-text-field
                  v-model="credentials.username"
                  label="Benutzername"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-account"
                  :rules="[rules.required]"
                  class="mb-3"
                />
                
                <v-text-field
                  v-model="credentials.password"
                  label="Passwort"
                  variant="outlined"
                  density="comfortable"
                  prepend-inner-icon="mdi-lock"
                  :type="showPassword ? 'text' : 'password'"
                  :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                  @click:append-inner="showPassword = !showPassword"
                  :rules="[rules.required]"
                  class="mb-2"
                />
                
                <div class="d-flex justify-space-between align-center mb-4">
                  <v-checkbox
                    v-model="rememberMe"
                    label="Angemeldet bleiben"
                    density="compact"
                    hide-details
                    class="remember-me"
                  />
                  <a href="#" class="forgot-password">Passwort vergessen?</a>
                </div>
                
                <v-btn
                  color="#EC0016"
                  size="large"
                  block
                  class="login-btn"
                  :disabled="!valid"
                  @click="login"
                >
                  Anmelden
                </v-btn>
                
                <v-divider class="my-6" />
                
                <div class="text-center">
                  <p class="register-text">
                    Noch kein Konto?
                    <a href="#" class="register-link">Jetzt registrieren</a>
                  </p>
                </div>
              </v-form>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const valid = ref(false)
const showPassword = ref(false)
const rememberMe = ref(false)
const loginForm = ref(null)

const credentials = ref({
  username: '',
  password: ''
})

const rules = {
  required: value => !!value || 'Dieses Feld ist erforderlich'
}

function login() {
  if (valid.value) {
    console.log('Login attempt:', {
      username: credentials.value.username,
      rememberMe: rememberMe.value
    })
    // Frontend-only: Hier würde die Backend-Authentifizierung erfolgen
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #F0F3F5 0%, #E8EBED 100%);
  padding: 2rem 1rem;
}

.login-container {
  max-width: 1340px;
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.login-title {
  color: #282D37;
  font-weight: 700;
  font-size: 1rem;
  padding: 0.5rem 0 1rem 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.login-form {
  padding: 1rem 1.5rem 2rem 1.5rem;
}

.login-btn {
  text-transform: none;
  font-weight: 600;
  letter-spacing: 0.3px;
  font-size: 1rem;
  color: white;
}

.forgot-password {
  color: #EC0016;
  text-decoration: none;
  font-size: 0.8rem;
  font-weight: 500;
}

.forgot-password:hover {
  text-decoration: underline;
}

.register-text {
  color: #282D37;
  font-size: 0.95rem;
  margin: 0;
}

.register-link {
  color: #EC0016;
  text-decoration: none;
  font-weight: 600;
  margin-left: 0.3rem;
}

.register-link:hover {
  text-decoration: underline;
}

.mb-3 {
  margin-bottom: 0.75rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.my-6 {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.remember-me :deep(.v-label) {
  font-size: 0.8rem;
}
</style>
