import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { logger } from '../utils/logger';

interface User {
  id: string;
  username: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
  lastLoginAt?: Date;
  isActive: boolean;
  role: 'user' | 'admin';
  apiKeyHash?: string;
}

interface LoginRequest {
  username: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

interface AuthToken {
  token: string;
  expiresIn: string;
  user: Omit<User, 'passwordHash' | 'apiKeyHash'>;
}

export class AuthService {
  private users: Map<string, User> = new Map();
  private jwtSecret: string;
  private jwtExpiresIn: string;

  constructor() {
    this.jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key';
    this.jwtExpiresIn = process.env.JWT_EXPIRES_IN || '24h';
    
    // Initialize with a default admin user for development
    this.initializeDefaultUsers();
  }

  private async initializeDefaultUsers(): Promise<void> {
    try {
      // Create default admin user
      const adminUser: User = {
        id: 'admin-001',
        username: 'admin',
        email: 'admin@example.com',
        passwordHash: await bcrypt.hash('admin123', 10),
        createdAt: new Date(),
        isActive: true,
        role: 'admin',
      };

      // Create default regular user
      const regularUser: User = {
        id: 'user-001',
        username: 'demo',
        email: 'demo@example.com',
        passwordHash: await bcrypt.hash('demo123', 10),
        createdAt: new Date(),
        isActive: true,
        role: 'user',
      };

      this.users.set(adminUser.id, adminUser);
      this.users.set(regularUser.id, regularUser);

      logger.info('Default users initialized');
    } catch (error) {
      logger.error('Error initializing default users:', error);
    }
  }

  public async register(registerData: RegisterRequest): Promise<AuthToken> {
    try {
      // Check if user already exists
      const existingUser = Array.from(this.users.values()).find(
        u => u.username === registerData.username || u.email === registerData.email
      );

      if (existingUser) {
        throw new Error('User already exists');
      }

      // Hash password
      const passwordHash = await bcrypt.hash(registerData.password, 10);

      // Create new user
      const newUser: User = {
        id: `user-${Date.now()}`,
        username: registerData.username,
        email: registerData.email,
        passwordHash,
        createdAt: new Date(),
        isActive: true,
        role: 'user',
      };

      this.users.set(newUser.id, newUser);

      // Generate JWT token
      const token = this.generateToken(newUser);

      logger.info('User registered successfully', { userId: newUser.id, username: newUser.username });

      return {
        token,
        expiresIn: this.jwtExpiresIn,
        user: this.sanitizeUser(newUser),
      };
    } catch (error) {
      logger.error('Registration error:', error);
      throw error;
    }
  }

  public async login(loginData: LoginRequest): Promise<AuthToken> {
    try {
      // Find user by username
      const user = Array.from(this.users.values()).find(
        u => u.username === loginData.username
      );

      if (!user) {
        throw new Error('Invalid credentials');
      }

      if (!user.isActive) {
        throw new Error('Account is disabled');
      }

      // Verify password
      const isPasswordValid = await bcrypt.compare(loginData.password, user.passwordHash);

      if (!isPasswordValid) {
        throw new Error('Invalid credentials');
      }

      // Update last login time
      user.lastLoginAt = new Date();
      this.users.set(user.id, user);

      // Generate JWT token
      const token = this.generateToken(user);

      logger.info('User logged in successfully', { userId: user.id, username: user.username });

      return {
        token,
        expiresIn: this.jwtExpiresIn,
        user: this.sanitizeUser(user),
      };
    } catch (error) {
      logger.error('Login error:', error);
      throw error;
    }
  }

  public async validateToken(token: string): Promise<User | null> {
    try {
      const decoded = jwt.verify(token, this.jwtSecret) as any;
      const user = this.users.get(decoded.userId);

      if (!user || !user.isActive) {
        return null;
      }

      return user;
    } catch (error) {
      logger.warn('Token validation failed:', error);
      return null;
    }
  }

  public async generateApiKey(userId: string): Promise<string> {
    try {
      const user = this.users.get(userId);
      if (!user) {
        throw new Error('User not found');
      }

      // Generate API key
      const apiKey = `llm_${Math.random().toString(36).substr(2, 32)}`;
      const apiKeyHash = await bcrypt.hash(apiKey, 10);

      // Store hashed API key
      user.apiKeyHash = apiKeyHash;
      this.users.set(userId, user);

      logger.info('API key generated', { userId });
      return apiKey;
    } catch (error) {
      logger.error('Error generating API key:', error);
      throw error;
    }
  }

  public async validateApiKey(apiKey: string): Promise<User | null> {
    try {
      // Find user with matching API key
      const user = Array.from(this.users.values()).find(async (u) => {
        if (!u.apiKeyHash) return false;
        return await bcrypt.compare(apiKey, u.apiKeyHash);
      });

      if (!user || !user.isActive) {
        return null;
      }

      return user;
    } catch (error) {
      logger.warn('API key validation failed:', error);
      return null;
    }
  }

  public getUserById(userId: string): User | null {
    return this.users.get(userId) || null;
  }

  public getAllUsers(): User[] {
    return Array.from(this.users.values()).map(this.sanitizeUser);
  }

  public async updateUser(userId: string, updates: Partial<User>): Promise<User> {
    const user = this.users.get(userId);
    if (!user) {
      throw new Error('User not found');
    }

    // Hash password if it's being updated
    if (updates.passwordHash) {
      updates.passwordHash = await bcrypt.hash(updates.passwordHash, 10);
    }

    const updatedUser = { ...user, ...updates };
    this.users.set(userId, updatedUser);

    logger.info('User updated', { userId });
    return this.sanitizeUser(updatedUser);
  }

  public async deleteUser(userId: string): Promise<void> {
    const user = this.users.get(userId);
    if (!user) {
      throw new Error('User not found');
    }

    this.users.delete(userId);
    logger.info('User deleted', { userId });
  }

  private generateToken(user: User): string {
    const payload = {
      userId: user.id,
      username: user.username,
      role: user.role,
    };

    return jwt.sign(payload, this.jwtSecret, { 
      expiresIn: this.jwtExpiresIn,
      issuer: 'llm-inference-server',
      audience: 'llm-users',
    });
  }

  private sanitizeUser(user: User): Omit<User, 'passwordHash' | 'apiKeyHash'> {
    const { passwordHash, apiKeyHash, ...sanitized } = user;
    return sanitized;
  }

  // Get usage statistics for a user
  public getUserStats(userId: string): any {
    const user = this.users.get(userId);
    if (!user) {
      return null;
    }

    return {
      userId: user.id,
      username: user.username,
      role: user.role,
      createdAt: user.createdAt,
      lastLoginAt: user.lastLoginAt,
      isActive: user.isActive,
      // Add more stats as needed (API calls, tokens used, etc.)
    };
  }
}
