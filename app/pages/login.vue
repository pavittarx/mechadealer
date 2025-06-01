<template>
  <div class="login-page-wrapper">
    <div class="login-container">
      <img src="/mechadealer_logo.png" alt="Mechadealer Logo" class="logo">
      <h1>Member Login</h1>
      <p class="subtitle">Access your Mechadealer account</p>
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username or Email</label>
          <input type="text" id="username" v-model="username" required placeholder="Enter your username or email" />
        </div>
        <div class="form-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required placeholder="Enter your password" />
        </div>
        <div class="form-actions">
          <NuxtLink to="/forgot-password" class="forgot-password-link">Forgot Password?</NuxtLink>
          <button type="submit" class="login-button">Login</button>
        </div>
      </form>
      <p class="signup-link">
        Don't have an account? <NuxtLink to="/register">Sign Up</NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const username = ref('');
const password = ref('');
const error = ref('');

type LoginRespose = {
  is_error: boolean;
  is_success: boolean;
  message: string;
  data: {
    user_id: number;
    token: string;
  }
}

const handleLogin = async () => {
  const runtimeConfig = useRuntimeConfig()
  const url = runtimeConfig.public.baseUrl + '/login';

  try {
    const res: LoginRespose = await $fetch(url, {
      method: 'POST',
      body: {
        username: username.value,
        password: password.value
      }
    })

    if (res.is_error) {
      error.value = res.message;
    }

    const userStore = useUserStore();

    userStore.setUserId(res.data.user_id);
    userStore.setToken(res.data.token);

    console.log('Login Succeessful')
    navigateTo('/dashboard');
  }
  catch (error) {
    console.log("Error while logging in.");
    console.error(error);
  }

};
</script>

<style scoped>
.login-page-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #1A237E 0%, #283593 50%, #3949AB 100%);
  /* Deep Indigo to Indigo */
  padding: 20px;
  font-family: 'Roboto', 'Arial', sans-serif;
}

.login-container {
  background-color: #ffffff;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 450px;
  text-align: center;
}

.logo {
  max-width: 150px;
  margin-bottom: 20px;
}

.login-container h1 {
  font-size: 2em;
  color: #1A237E;
  /* Deep Indigo */
  margin-bottom: 10px;
  font-weight: 600;
}

.subtitle {
  font-size: 1em;
  color: #555;
  margin-bottom: 30px;
}

.login-form {
  text-align: left;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 0.95em;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  box-sizing: border-box;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  border-color: #3949AB;
  /* Indigo */
  outline: none;
  box-shadow: 0 0 0 2px rgba(57, 73, 171, 0.2);
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 25px;
}

.forgot-password-link {
  font-size: 0.9em;
  color: #3949AB;
  /* Indigo */
  text-decoration: none;
}

.forgot-password-link:hover {
  text-decoration: underline;
}

.login-button {
  background-color: #FFC107;
  /* Amber */
  color: #333;
  padding: 12px 25px;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.login-button:hover {
  background-color: #FFB300;
  /* Darker Amber */
  transform: translateY(-1px);
}

.signup-link {
  margin-top: 25px;
  font-size: 0.95em;
  color: #555;
}

.signup-link a {
  color: #FFC107;
  /* Amber */
  font-weight: bold;
  text-decoration: none;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>