import express from 'express';
import { AuthController } from '../controllers/authController';
import { asyncHandler } from '@microservices/shared';

const router = express.Router();

// POST /auth/signup - User registration
router.post('/signup', asyncHandler(AuthController.signup));

// POST /auth/signin - User login
router.post('/signin', asyncHandler(AuthController.signin));

// GET /auth/verify - Token verification
router.get('/verify', asyncHandler(AuthController.verifyToken));

export default router;
