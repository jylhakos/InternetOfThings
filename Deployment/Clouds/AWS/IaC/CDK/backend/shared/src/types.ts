export interface User {
  id?: number;
  username: string;
  email: string;
  phoneNumber: string;
  passwordHash?: string;
  createdAt?: Date;
  updatedAt?: Date;
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
  user: Omit<User, 'passwordHash'>;
  token: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface JwtPayload {
  userId: number;
  email: string;
  iat?: number;
  exp?: number;
}
