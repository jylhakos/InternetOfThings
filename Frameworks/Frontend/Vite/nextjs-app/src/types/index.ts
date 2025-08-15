export interface Device {
  id: string
  name: string
  type: 'sensor' | 'actuator' | 'gateway' | 'controller'
  status: 'online' | 'offline' | 'warning'
  location: string
  lastSeen: string
  temperature?: number
  humidity?: number
  batteryLevel?: number
  firmware: string
}

export interface ApiResponse<T> {
  data: T
  success: boolean
  message: string
  timestamp: string
}

export interface ServerInfo {
  serverTime: string
  nodeVersion: string
  platform: string
  uptime: number
}
