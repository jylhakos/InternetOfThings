import { Request, Response } from 'express';
import database from '../database';
import {
  CreateUserRequest,
  SignInRequest,
  AuthResponse,
  User,
  AuthUtils,
  createSuccessResponse,
  createErrorResponse,
  ApiError,
  validateCreateUser,
  validateSignIn,
  logger
} from '@microservices/shared';

export class AuthController {
  static async signup(req: Request, res: Response) {
    try {
      const { error, value } = validateCreateUser(req.body);
      if (error) {
        return res.status(400).json(
          createErrorResponse('Validation failed', error.details[0].message)
        );
      }

      const { username, email, phoneNumber, password }: CreateUserRequest = value;

      // Check if user already exists
      const existingUser = await database.query(
        'SELECT id FROM users WHERE email = $1 OR username = $2',
        [email, username]
      );

      if (existingUser.rows.length > 0) {
        return res.status(409).json(
          createErrorResponse('User already exists', 'Email or username already registered')
        );
      }

      // Hash password
      const passwordHash = await AuthUtils.hashPassword(password);

      // Create user
      const result = await database.query(
        `INSERT INTO users (username, email, phone_number, password_hash) 
         VALUES ($1, $2, $3, $4) 
         RETURNING id, username, email, phone_number, created_at`,
        [username, email, phoneNumber, passwordHash]
      );

      const user = result.rows[0];
      const token = AuthUtils.generateToken({
        userId: user.id,
        email: user.email
      });

      const response: AuthResponse = {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          phoneNumber: user.phone_number,
          createdAt: user.created_at
        },
        token
      };

      logger.info(`User created successfully: ${email}`);
      res.status(201).json(createSuccessResponse(response, 'User created successfully'));
    } catch (error) {
      logger.error('Signup error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to create user')
      );
    }
  }

  static async signin(req: Request, res: Response) {
    try {
      const { error, value } = validateSignIn(req.body);
      if (error) {
        return res.status(400).json(
          createErrorResponse('Validation failed', error.details[0].message)
        );
      }

      const { email, password }: SignInRequest = value;

      // Find user
      const result = await database.query(
        'SELECT id, username, email, phone_number, password_hash FROM users WHERE email = $1',
        [email]
      );

      if (result.rows.length === 0) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'Invalid credentials')
        );
      }

      const user = result.rows[0];

      // Verify password
      const isPasswordValid = await AuthUtils.comparePassword(password, user.password_hash);
      if (!isPasswordValid) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'Invalid credentials')
        );
      }

      // Generate token
      const token = AuthUtils.generateToken({
        userId: user.id,
        email: user.email
      });

      const response: AuthResponse = {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          phoneNumber: user.phone_number
        },
        token
      };

      logger.info(`User signed in successfully: ${email}`);
      res.json(createSuccessResponse(response, 'Sign in successful'));
    } catch (error) {
      logger.error('Signin error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to sign in')
      );
    }
  }

  static async verifyToken(req: Request, res: Response) {
    try {
      const token = AuthUtils.extractTokenFromHeader(req.headers.authorization);
      if (!token) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'No token provided')
        );
      }

      const payload = AuthUtils.verifyToken(token);
      
      // Get user details
      const result = await database.query(
        'SELECT id, username, email, phone_number FROM users WHERE id = $1',
        [payload.userId]
      );

      if (result.rows.length === 0) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'User not found')
        );
      }

      const user = result.rows[0];
      res.json(createSuccessResponse({
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          phoneNumber: user.phone_number
        },
        isValid: true
      }));
    } catch (error) {
      logger.error('Token verification error:', error);
      res.status(401).json(
        createErrorResponse('Authentication failed', 'Invalid token')
      );
    }
  }
}
