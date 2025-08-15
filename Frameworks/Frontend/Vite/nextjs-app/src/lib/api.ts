import { Device, ApiResponse } from '@/types'

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// Mock device data
const mockDevices: Device[] = [
  {
    id: '1',
    name: 'Temperature Sensor A1',
    type: 'sensor',
    status: 'online',
    location: 'Factory Floor',
    lastSeen: new Date(Date.now() - 1000 * 60 * 5).toISOString(), // 5 minutes ago
    temperature: 23.5,
    humidity: 45,
    batteryLevel: 85,
    firmware: '1.2.3',
  },
  {
    id: '2',
    name: 'Humidity Control B2',
    type: 'actuator',
    status: 'online',
    location: 'Greenhouse',
    lastSeen: new Date(Date.now() - 1000 * 60 * 2).toISOString(), // 2 minutes ago
    temperature: 26.8,
    humidity: 62,
    batteryLevel: 92,
    firmware: '2.1.0',
  },
  {
    id: '3',
    name: 'Gateway Main',
    type: 'gateway',
    status: 'online',
    location: 'Server Room',
    lastSeen: new Date(Date.now() - 1000 * 30).toISOString(), // 30 seconds ago
    batteryLevel: 100,
    firmware: '3.0.1',
  },
  {
    id: '4',
    name: 'Pressure Monitor C3',
    type: 'sensor',
    status: 'warning',
    location: 'Pipeline Section C',
    lastSeen: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 minutes ago
    temperature: 31.2,
    batteryLevel: 23,
    firmware: '1.1.8',
  },
  {
    id: '5',
    name: 'Motor Controller D4',
    type: 'controller',
    status: 'offline',
    location: 'Assembly Line D',
    lastSeen: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
    batteryLevel: 0,
    firmware: '2.0.5',
  },
  {
    id: '6',
    name: 'Environment Monitor E5',
    type: 'sensor',
    status: 'online',
    location: 'Office Area',
    lastSeen: new Date(Date.now() - 1000 * 60).toISOString(), // 1 minute ago
    temperature: 22.1,
    humidity: 40,
    batteryLevel: 78,
    firmware: '1.3.2',
  },
]

// Server-side API functions (these run on the server)
export async function getDeviceData(): Promise<Device[]> {
  // Simulate API call delay
  await delay(100)
  
  console.log('[Server] Fetching device data...', new Date().toISOString())
  
  // In a real application, this would be a database query or external API call
  return mockDevices
}

export async function getServerTime(): Promise<string> {
  // Simulate API call delay
  await delay(50)
  
  console.log('[Server] Getting server time...', new Date().toISOString())
  
  return new Date().toISOString()
}

export async function getDeviceById(id: string): Promise<Device | null> {
  await delay(80)
  
  console.log(`[Server] Fetching device by ID: ${id}`, new Date().toISOString())
  
  return mockDevices.find(device => device.id === id) || null
}

// Client-side API functions (these run in the browser)
export async function fetchDevices(): Promise<ApiResponse<Device[]>> {
  const response = await fetch('/api/devices')
  if (!response.ok) {
    throw new Error('Failed to fetch devices')
  }
  return response.json()
}

export async function fetchDevice(id: string): Promise<ApiResponse<Device>> {
  const response = await fetch(`/api/devices/${id}`)
  if (!response.ok) {
    throw new Error('Failed to fetch device')
  }
  return response.json()
}

export async function updateDevice(id: string, data: Partial<Device>): Promise<ApiResponse<Device>> {
  const response = await fetch(`/api/devices/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
  
  if (!response.ok) {
    throw new Error('Failed to update device')
  }
  
  return response.json()
}
