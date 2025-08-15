export interface Device {
  id: string;
  name: string;
  type: 'temperature' | 'humidity' | 'motion' | 'light' | 'pressure';
  status: 'online' | 'offline' | 'error';
  value: number;
  unit: string;
  location: string;
  lastUpdate: string;
  battery: number;
}

export interface DeviceStats {
  total: number;
  online: number;
  offline: number;
  lowBattery: number;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  timestamp: string;
}

export interface DevicesResponse {
  devices: Device[];
  stats: DeviceStats;
  timestamp: string;
}
