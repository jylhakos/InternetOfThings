import { Router, Request, Response } from 'express';
import { body, validationResult } from 'express-validator';
import { AuthService } from '../services/AuthService';
import { logger } from '../utils/logger';

export const authRoutes = (authService: AuthService): Router => {
  const router = Router();

  // Validation middleware
  const validateLogin = [
    body('username').notEmpty().withMessage('Username is required'),
    body('password').notEmpty().withMessage('Password is required'),
  ];

  const validateRegister = [
    body('username')
      .isLength({ min: 3, max: 50 })
      .withMessage('Username must be between 3 and 50 characters'),
    body('email').isEmail().withMessage('Valid email is required'),
    body('password')
      .isLength({ min: 6 })
      .withMessage('Password must be at least 6 characters long'),
  ];

  // Register endpoint
  router.post('/register', validateRegister, async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: {
            message: 'Validation failed',
            type: 'validation_error',
            details: errors.array(),
          }
        });
      }

      const { username, email, password } = req.body;
      const result = await authService.register({ username, email, password });

      res.status(201).json({
        message: 'User registered successfully',
        ...result,
      });
    } catch (error) {
      logger.error('Registration error:', error);
      
      if (error instanceof Error) {
        if (error.message === 'User already exists') {
          return res.status(409).json({
            error: {
              message: error.message,
              type: 'conflict_error',
            }
          });
        }
      }

      res.status(500).json({
        error: {
          message: 'Registration failed',
          type: 'internal_error',
        }
      });
    }
  });

  // Login endpoint
  router.post('/login', validateLogin, async (req: Request, res: Response) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(400).json({
          error: {
            message: 'Validation failed',
            type: 'validation_error',
            details: errors.array(),
          }
        });
      }

      const { username, password } = req.body;
      const result = await authService.login({ username, password });

      res.json({
        message: 'Login successful',
        ...result,
      });
    } catch (error) {
      logger.error('Login error:', error);
      
      if (error instanceof Error) {
        if (error.message === 'Invalid credentials' || error.message === 'Account is disabled') {
          return res.status(401).json({
            error: {
              message: error.message,
              type: 'authentication_error',
            }
          });
        }
      }

      res.status(500).json({
        error: {
          message: 'Login failed',
          type: 'internal_error',
        }
      });
    }
  });

  // Generate API key endpoint
  router.post('/api-key', async (req: Request, res: Response) => {
    try {
      // This endpoint would need authentication middleware
      const userId = req.body.userId;
      if (!userId) {
        return res.status(400).json({
          error: {
            message: 'User ID is required',
            type: 'validation_error',
          }
        });
      }

      const apiKey = await authService.generateApiKey(userId);
      
      res.json({
        message: 'API key generated successfully',
        apiKey,
        note: 'Store this key securely. It will not be shown again.',
      });
    } catch (error) {
      logger.error('API key generation error:', error);
      
      if (error instanceof Error && error.message === 'User not found') {
        return res.status(404).json({
          error: {
            message: error.message,
            type: 'not_found_error',
          }
        });
      }

      res.status(500).json({
        error: {
          message: 'Failed to generate API key',
          type: 'internal_error',
        }
      });
    }
  });

  // Get user profile
  router.get('/profile/:userId', async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const user = authService.getUserById(userId);

      if (!user) {
        return res.status(404).json({
          error: {
            message: 'User not found',
            type: 'not_found_error',
          }
        });
      }

      res.json({
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          createdAt: user.createdAt,
          lastLoginAt: user.lastLoginAt,
          isActive: user.isActive,
        }
      });
    } catch (error) {
      logger.error('Profile retrieval error:', error);
      res.status(500).json({
        error: {
          message: 'Failed to retrieve profile',
          type: 'internal_error',
        }
      });
    }
  });

  // Get user statistics
  router.get('/stats/:userId', async (req: Request, res: Response) => {
    try {
      const { userId } = req.params;
      const stats = authService.getUserStats(userId);

      if (!stats) {
        return res.status(404).json({
          error: {
            message: 'User not found',
            type: 'not_found_error',
          }
        });
      }

      res.json({ stats });
    } catch (error) {
      logger.error('Stats retrieval error:', error);
      res.status(500).json({
        error: {
          message: 'Failed to retrieve statistics',
          type: 'internal_error',
        }
      });
    }
  });

  return router;
};
