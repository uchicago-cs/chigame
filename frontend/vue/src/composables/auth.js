import { ref } from 'vue'
import axios from 'axios'

const isAuth = ref(false)
const isLoading = ref(true)
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('access-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

async function checkAuth() {
  isLoading.value = true
  const token = localStorage.getItem('access-token')
  if (!token) {
    isLoading.value = false
    isAuth.value = false
    return
  }
  try {
    const response = await api.get('/api/login/checkauth/')
    isAuth.value = response.data.authenticated === true
  } catch {
    isAuth.value = false
  } finally {
    isLoading.value = false
  }
}

export function useAuth() {
  return {isAuth, isLoading, checkAuth, api}
}
