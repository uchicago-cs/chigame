<template>
  <div class="login-container">
    <div class="form-card">
      <h2>Sign In</h2>
      <form @submit.prevent="handleSubmit">
        <label for="email">Email</label>
        <input id="email" type="email" v-model="form.email" required />

        <label for="password">Password</label>
        <input id="password" type="password" v-model="form.password" required />

        <button type="submit">Sign In</button>
        <div class="mt-3" style="min-height: 20vh;">
          <div v-if="error">
          <div class="alert alert-danger mt-3">
              <p>{{ error }}</p>
            </div>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const form = ref({ email: '', password: '' })
const error = ref(null)

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

async function handleSubmit() {
  error.value = null
  try {
    const { data } = await api.post('/api/login/token/', {
      email: form.value.email,
      password: form.value.password,
    })
    localStorage.setItem('access-token', data.access)
    api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`
    router.push('/')
  } catch (err) {
    error.value =
      err.response?.data?.detail ||
      err.response?.statusText ||
      err.message
  }
}
</script>

<style scoped>
.login-container {
  background: white;     /* page stays white */
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-card {
  background: white;     /* card stays white */
  padding: 1.5rem;
  max-width: 360px;
  width: 100%;
}

h2 {
  margin-bottom: 1rem;
  color: #800000;         /* maroon */
}

label {
  display: block;
  margin: 0.5rem 0 0.25rem;
  color: #737373;         /* dark greystone */
}

input {
  width: 100%;
  padding: 0.5rem;
  margin-bottom: 1rem;

  /* only inputs are grey */
  background: #D9D9D9;    /* light greystone */
  border: 1px solid #A6A6A6; /* greystone */
  border-radius: 3px;
}

input:focus {
  outline: none;
  border-color: #800000;  /* maroon on focus */
}

button {
  width: 100%;
  padding: 0.6rem;
  background: #800000;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
}
</style>
