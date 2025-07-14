export interface User {
  id: number;
  username: string;
  email: string;
  phoneNumber: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface CreateUserRequest {
  username: string;
  email: string;
  phoneNumber: string;
  password: string;
}

export interface SignInRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user: User;
  token: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface UserProfileUpdate {
  username?: string;
  email?: string;
  phoneNumber?: string;
}
