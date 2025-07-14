import express from 'express';
import { UserController } from '../controllers/userController';
import { authenticateToken } from '../middleware/auth';
import { asyncHandler } from '@microservices/shared';

const router = express.Router();

// All routes require authentication
router.use(authenticateToken);

// GET /users/profile - Get current user profile
router.get('/profile', asyncHandler(UserController.getProfile));

// PUT /users/profile - Update current user profile
router.put('/profile', asyncHandler(UserController.updateProfile));

// GET /users/:id - Get user by ID
router.get('/:id', asyncHandler(UserController.getUserById));

// GET /users - Get all users (with pagination)
router.get('/', asyncHandler(UserController.getAllUsers));

export default router;
