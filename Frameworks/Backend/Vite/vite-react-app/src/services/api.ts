import axios from 'axios';
import { Device, DevicesResponse } from '@types/index';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status}:`, response.config.url);
    return response;
  },
  (error) => {
    console.error('[API] Response error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

export const deviceService = {
  // Get all devices with stats
  async getAllDevices(): Promise<DevicesResponse> {
    const response = await api.get<DevicesResponse>('/devices');
    return response.data;
  },

  // Get single device
  async getDevice(id: string): Promise<Device> {
    const response = await api.get<Device>(`/devices/${id}`);
    return response.data;
  },

  // Update device
  async updateDevice(id: string, data: Partial<Device>): Promise<Device> {
    const response = await api.put<Device>(`/devices/${id}`, data);
    return response.data;
  },

  // Create new device
  async createDevice(data: Omit<Device, 'id' | 'lastUpdate'>): Promise<Device> {
    const response = await api.post<Device>('/devices', data);
    return response.data;
  },

  // Delete device
  async deleteDevice(id: string): Promise<Device> {
    const response = await api.delete<Device>(`/devices/${id}`);
    return response.data;
  },

  // Health check
  async healthCheck() {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
