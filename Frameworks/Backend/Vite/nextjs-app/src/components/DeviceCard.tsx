'use client'

import { Device } from '@/types'
import { format } from 'date-fns'

interface DeviceCardProps {
  device: Device
}

const statusColors = {
  online: 'bg-green-100 text-green-800',
  offline: 'bg-red-100 text-red-800',
  warning: 'bg-yellow-100 text-yellow-800',
}

const typeIcons = {
  sensor: '🌡️',
  actuator: '⚡',
  gateway: '🌐',
  controller: '🎛️',
}

export function DeviceCard({ device }: DeviceCardProps) {
  const statusColor = statusColors[device.status]
  const typeIcon = typeIcons[device.type]

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">{typeIcon}</span>
          <div>
            <h3 className="font-semibold text-gray-900">{device.name}</h3>
            <p className="text-sm text-gray-500">{device.type}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
          {device.status}
        </span>
      </div>

      {/* Location */}
      <div className="mb-3">
        <p className="text-sm text-gray-600">
          📍 {device.location}
        </p>
      </div>

      {/* Metrics */}
      <div className="space-y-2 mb-4">
        {device.temperature !== undefined && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Temperature:</span>
            <span className="text-sm font-medium">{device.temperature}°C</span>
          </div>
        )}
        {device.humidity !== undefined && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Humidity:</span>
            <span className="text-sm font-medium">{device.humidity}%</span>
          </div>
        )}
        {device.batteryLevel !== undefined && (
          <div className="flex justify-between">
            <span className="text-sm text-gray-600">Battery:</span>
            <span className="text-sm font-medium">{device.batteryLevel}%</span>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t pt-3 space-y-1">
        <div className="flex justify-between text-xs text-gray-500">
          <span>Firmware: {device.firmware}</span>
        </div>
        <div className="text-xs text-gray-500">
          Last seen: {format(new Date(device.lastSeen), 'MMM dd, HH:mm')}
        </div>
      </div>
    </div>
  )
}
