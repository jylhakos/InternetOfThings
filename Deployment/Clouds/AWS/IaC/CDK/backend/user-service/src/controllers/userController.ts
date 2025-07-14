import { Response } from 'express';
import database from '../database';
import {
  User,
  createSuccessResponse,
  createErrorResponse,
  validateUpdateUser,
  logger
} from '@microservices/shared';
import { AuthenticatedRequest } from '../middleware/auth';

export class UserController {
  static async getProfile(req: AuthenticatedRequest, res: Response) {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'User not authenticated')
        );
      }

      const result = await database.query(
        'SELECT id, username, email, phone_number, created_at, updated_at FROM users WHERE id = $1',
        [userId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json(
          createErrorResponse('User not found', 'User profile not found')
        );
      }

      const user = result.rows[0];
      const userProfile: User = {
        id: user.id,
        username: user.username,
        email: user.email,
        phoneNumber: user.phone_number,
        createdAt: user.created_at,
        updatedAt: user.updated_at
      };

      res.json(createSuccessResponse(userProfile, 'Profile retrieved successfully'));
    } catch (error) {
      logger.error('Get profile error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to retrieve profile')
      );
    }
  }

  static async updateProfile(req: AuthenticatedRequest, res: Response) {
    try {
      const userId = req.user?.id;
      if (!userId) {
        return res.status(401).json(
          createErrorResponse('Authentication failed', 'User not authenticated')
        );
      }

      const { error, value } = validateUpdateUser(req.body);
      if (error) {
        return res.status(400).json(
          createErrorResponse('Validation failed', error.details[0].message)
        );
      }

      const updates = [];
      const values = [];
      let paramCount = 1;

      if (value.username) {
        updates.push(`username = $${paramCount++}`);
        values.push(value.username);
      }
      if (value.email) {
        updates.push(`email = $${paramCount++}`);
        values.push(value.email);
      }
      if (value.phoneNumber) {
        updates.push(`phone_number = $${paramCount++}`);
        values.push(value.phoneNumber);
      }

      if (updates.length === 0) {
        return res.status(400).json(
          createErrorResponse('No updates provided', 'At least one field must be updated')
        );
      }

      updates.push(`updated_at = CURRENT_TIMESTAMP`);
      values.push(userId);

      const query = `
        UPDATE users 
        SET ${updates.join(', ')} 
        WHERE id = $${paramCount}
        RETURNING id, username, email, phone_number, created_at, updated_at
      `;

      const result = await database.query(query, values);

      if (result.rows.length === 0) {
        return res.status(404).json(
          createErrorResponse('User not found', 'User not found')
        );
      }

      const user = result.rows[0];
      const updatedProfile: User = {
        id: user.id,
        username: user.username,
        email: user.email,
        phoneNumber: user.phone_number,
        createdAt: user.created_at,
        updatedAt: user.updated_at
      };

      logger.info(`User profile updated: ${userId}`);
      res.json(createSuccessResponse(updatedProfile, 'Profile updated successfully'));
    } catch (error) {
      logger.error('Update profile error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to update profile')
      );
    }
  }

  static async getUserById(req: AuthenticatedRequest, res: Response) {
    try {
      const { id } = req.params;
      const userId = parseInt(id);

      if (isNaN(userId)) {
        return res.status(400).json(
          createErrorResponse('Invalid user ID', 'User ID must be a number')
        );
      }

      const result = await database.query(
        'SELECT id, username, email, phone_number, created_at FROM users WHERE id = $1',
        [userId]
      );

      if (result.rows.length === 0) {
        return res.status(404).json(
          createErrorResponse('User not found', 'User not found')
        );
      }

      const user = result.rows[0];
      const userProfile: User = {
        id: user.id,
        username: user.username,
        email: user.email,
        phoneNumber: user.phone_number,
        createdAt: user.created_at
      };

      res.json(createSuccessResponse(userProfile, 'User retrieved successfully'));
    } catch (error) {
      logger.error('Get user by ID error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to retrieve user')
      );
    }
  }

  static async getAllUsers(req: AuthenticatedRequest, res: Response) {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 10;
      const offset = (page - 1) * limit;

      const result = await database.query(
        `SELECT id, username, email, phone_number, created_at 
         FROM users 
         ORDER BY created_at DESC 
         LIMIT $1 OFFSET $2`,
        [limit, offset]
      );

      const countResult = await database.query('SELECT COUNT(*) FROM users');
      const totalUsers = parseInt(countResult.rows[0].count);

      const users: User[] = result.rows.map(user => ({
        id: user.id,
        username: user.username,
        email: user.email,
        phoneNumber: user.phone_number,
        createdAt: user.created_at
      }));

      const response = {
        users,
        pagination: {
          currentPage: page,
          totalPages: Math.ceil(totalUsers / limit),
          totalUsers,
          hasNextPage: page < Math.ceil(totalUsers / limit),
          hasPrevPage: page > 1
        }
      };

      res.json(createSuccessResponse(response, 'Users retrieved successfully'));
    } catch (error) {
      logger.error('Get all users error:', error);
      res.status(500).json(
        createErrorResponse('Internal server error', 'Failed to retrieve users')
      );
    }
  }
}
