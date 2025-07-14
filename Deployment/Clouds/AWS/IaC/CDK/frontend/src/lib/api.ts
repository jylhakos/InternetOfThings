import axios, { AxiosError } from 'axios';
import Cookies from 'js-cookie';
import { ApiResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login
      Cookies.remove('token');
      Cookies.remove('user');
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/signin';
      }
    }
    return Promise.reject(error);
  }
);

export const apiClient = {
  // Auth endpoints
  auth: {
    signup: (data: any): Promise<ApiResponse> => 
      api.post('/auth/signup', data).then(res => res.data),
    
    signin: (data: any): Promise<ApiResponse> => 
      api.post('/auth/signin', data).then(res => res.data),
    
    verify: (): Promise<ApiResponse> => 
      api.get('/auth/verify').then(res => res.data),
  },

  // User endpoints
  users: {
    getProfile: (): Promise<ApiResponse> => 
      api.get('/users/profile').then(res => res.data),
    
    updateProfile: (data: any): Promise<ApiResponse> => 
      api.put('/users/profile', data).then(res => res.data),
    
    getUserById: (id: number): Promise<ApiResponse> => 
      api.get(`/users/${id}`).then(res => res.data),
    
    getAllUsers: (params?: { page?: number; limit?: number }): Promise<ApiResponse> => 
      api.get('/users', { params }).then(res => res.data),
  },

  // Health check
  health: (): Promise<any> => 
    api.get('/health').then(res => res.data),
};

export default api;
