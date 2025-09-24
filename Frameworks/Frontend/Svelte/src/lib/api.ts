import axios from 'axios';
import { authStore } from './stores/auth';

const API_BASE_URL = 'http://localhost:3000/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  let token: string | null = null;
  
  // Get token from store
  authStore.subscribe(state => {
    token = state.token;
  })();
  
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  return config;
});

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, logout user
      authStore.logout();
    }
    return Promise.reject(error);
  }
);

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  name: string;
  email: string;
  password: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
}

export const authApi = {
  login: async (credentials: LoginCredentials) => {
    const response = await api.post<ApiResponse<{ user: any; token: string }>>('/auth/login', credentials);
    return response.data;
  },
  
  register: async (credentials: RegisterCredentials) => {
    const response = await api.post<ApiResponse<{ user: any; token: string }>>('/auth/register', credentials);
    return response.data;
  },
  
  logout: async () => {
    const response = await api.post<ApiResponse<null>>('/auth/logout');
    return response.data;
  },
  
  me: async () => {
    const response = await api.get<ApiResponse<any>>('/auth/me');
    return response.data;
  }
};

export const dataApi = {
  getItems: async () => {
    const response = await api.get<ApiResponse<any[]>>('/items');
    return response.data;
  },
  
  createItem: async (item: any) => {
    const response = await api.post<ApiResponse<any>>('/items', item);
    return response.data;
  }
};

export default api;