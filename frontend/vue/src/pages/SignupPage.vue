<template>
  <div class="signup-container">
    <div class="form-card">
      <h2>Sign Up</h2>
      <form @submit.prevent="handleSubmit">

        <label for="first-name">First Name</label>
        <input id="first-name" type="first-name" v-model="form.firstName" required />

        <label for="last-name">Last Name</label>
        <input id="last-name" type="last-name" v-model="form.lastName" required />

        <label for="email">Email</label>
        <input id="email" type="email" v-model="form.email" required />

        <label for="password">Password</label>
        <input id="password" type="password" v-model="form.password" required />

        <label for="confirm-password">Confirm Password</label>
        <input id="confirm-password" type="password" v-model="form.confirmPassword" required />

        <button type="submit">Sign Up</button>
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
const form = ref({ firstName: '', lastName: '', email: '', password: '', confirmPassword: '' })
const error = ref(null)

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

async function handleSubmit() {
  error.value = null
  if (form.value.password !== form.value.confirmPassword) {
    error.value = "Passwords do not match"
    return
  }

  try {
    await api.post('/api/login/signup/', {
      name: `${form.value.firstName} ${form.value.lastName}`,
      email: form.value.email,
      password1: form.value.password,
      password2: form.value.confirmPassword
    })
    router.push('/login')
  } catch (err) {
    error.value =
      err.response?.data?.message ||
      err.message
  }
  /* console.log('logging in with', form.value)
  router.push('/') */
}
</script>

<style scoped>
.signup-container {
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
