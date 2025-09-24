import { io, Socket } from 'socket.io-client';
import type { WeatherData } from '../types';

class SocketService {
  private socket: Socket | null = null;
  private url = 'http://localhost:8000';

  connect(): Socket {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(this.url, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
    });

    this.socket.on('connect', () => {
      console.log('Connected to server via Socket.IO');
    });

    this.socket.on('disconnect', (reason) => {
      console.log('Disconnected from server:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('Connection error:', error);
    });

    return this.socket;
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  onWeatherUpdate(callback: (data: WeatherData) => void): void {
    if (this.socket) {
      this.socket.on('weather_update', callback);
    }
  }

  onWeatherError(callback: (error: { error: string }) => void): void {
    if (this.socket) {
      this.socket.on('weather_error', callback);
    }
  }

  requestWeather(): void {
    if (this.socket) {
      this.socket.emit('request_weather');
    }
  }

  removeAllListeners(): void {
    if (this.socket) {
      this.socket.removeAllListeners();
    }
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }
}

export const socketService = new SocketService();
export default socketService;