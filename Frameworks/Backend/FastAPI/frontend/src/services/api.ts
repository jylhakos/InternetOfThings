import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Authentication API
export const authAPI = {
  login: async (credentials: { phone: string; password: string }) => {
    const response = await api.post('/auth/login', credentials)
    return response.data
  },

  register: async (userData: { phone: string; password: string; email: string }) => {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  getProfile: async () => {
    const response = await api.get('/users/profile')
    return response.data
  },
}

// Health check API
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health')
    return response.data
  },
}

// Cache test API
export const cacheAPI = {
  test: async (key: string, value?: string) => {
    const url = value ? `/cache/test/${key}?value=${value}` : `/cache/test/${key}`
    const response = await api.get(url)
    return response.data
  },
}

// Performance test API
export const performanceAPI = {
  heavyOperation: async () => {
    const response = await api.get('/performance/heavy')
    return response.data
  },
}

export default api
