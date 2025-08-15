import React from 'react';
import { Device } from '../types';
import { format } from 'date-fns';

interface DeviceCardProps {
  device: Device;
  onUpdate?: (device: Device) => void;
  onDelete?: (id: string) => void;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({ device, onUpdate, onDelete }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-600 bg-green-100';
      case 'offline': return 'text-red-600 bg-red-100';
      case 'error': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'temperature': return '🌡️';
      case 'humidity': return '💧';
      case 'motion': return '🚶';
      case 'light': return '💡';
      case 'pressure': return '📊';
      default: return '📱';
    }
  };

  const getBatteryColor = (battery: number) => {
    if (battery > 50) return 'text-green-600';
    if (battery > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const toggleStatus = () => {
    if (onUpdate) {
      onUpdate({
        ...device,
        status: device.status === 'online' ? 'offline' : 'online'
      });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getTypeIcon(device.type)}</span>
          <div>
            <h3 className="text-lg font-semibold text-gray-800">{device.name}</h3>
            <p className="text-sm text-gray-600">{device.location}</p>
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(device.status)}`}>
          {device.status}
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Value:</span>
          <span className="text-lg font-bold text-blue-600">
            {device.value} {device.unit}
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Battery:</span>
          <span className={`text-sm font-semibold ${getBatteryColor(device.battery)}`}>
            {device.battery}%
          </span>
        </div>

        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">Last Update:</span>
          <span className="text-xs text-gray-500">
            {format(new Date(device.lastUpdate), 'MMM dd, HH:mm')}
          </span>
        </div>
      </div>

      <div className="flex space-x-2 mt-4">
        <button
          onClick={toggleStatus}
          className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
            device.status === 'online'
              ? 'bg-red-500 hover:bg-red-600 text-white'
              : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          {device.status === 'online' ? 'Turn Off' : 'Turn On'}
        </button>
        
        {onDelete && (
          <button
            onClick={() => onDelete(device.id)}
            className="px-3 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-md text-sm font-medium transition-colors"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
};
