export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData extends LoginData {
  first_name: string;
  last_name: string;
  phone: string;
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  description: string;
  condition: string;
  visibility: number;
  timestamp: string;
  location: string;
}