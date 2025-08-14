const express = require('express');
const bcrypt = require('bcryptjs');
const { body } = require('express-validator');
const User = require('../models/user');
const { 
  generateTokens, 
  verifyRefreshToken,
  generateAccessToken,
  sensitiveOperationLimit
} = require('../middleware/auth');
const { asyncHandler, handleValidationErrors } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * @route   POST /api/auth/register
 * @desc    Register a new user
 * @access  Public
 */
router.post('/register', [
  // Validation middleware
  body('name')
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Name must be between 2 and 100 characters'),
  
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
    
  body('phone')
    .isMobilePhone()
    .withMessage('Please provide a valid phone number'),
    
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number'),
    
  handleValidationErrors,
  sensitiveOperationLimit(3, 15 * 60 * 1000) // 3 attempts per 15 minutes
], asyncHandler(async (req, res) => {
  const { name, email, phone, password } = req.body;

  // Check if user already exists
  const existingUser = await User.findOne({
    $or: [{ email }, { phone }]
  });

  if (existingUser) {
    const field = existingUser.email === email ? 'email' : 'phone';
    return res.status(400).json({
      success: false,
      message: 'User already exists',
      error: `A user with this ${field} already exists`
    });
  }

  // Hash password
  const saltRounds = 12;
  const hashedPassword = await bcrypt.hash(password, saltRounds);

  // Create user
  const user = new User({
    name: name.trim(),
    email: email.toLowerCase(),
    phone: phone.replace(/\s+/g, ''),
    password: hashedPassword,
    metadata: {
      registrationSource: 'api',
      ipAddress: req.ip,
      userAgent: req.get('User-Agent')
    }
  });

  await user.save();

  // Generate tokens
  const tokens = generateTokens(user);

  // Update last login
  user.lastLogin = new Date();
  await user.save();

  res.status(201).json({
    success: true,
    message: 'User registered successfully',
    data: {
      user: user.toSafeObject(),
      ...tokens
    }
  });
}));

/**
 * @route   POST /api/auth/login
 * @desc    Authenticate user and get token
 * @access  Public
 */
router.post('/login', [
  body('username')
    .notEmpty()
    .withMessage('Username (email or phone) is required'),
    
  body('password')
    .notEmpty()
    .withMessage('Password is required'),
    
  handleValidationErrors,
  sensitiveOperationLimit(5, 15 * 60 * 1000) // 5 attempts per 15 minutes
], asyncHandler(async (req, res) => {
  const { username, password } = req.body;

  // Find user by email or phone
  const isEmail = username.includes('@');
  const user = isEmail 
    ? await User.findByEmail(username).select('+password')
    : await User.findByPhone(username).select('+password');

  if (!user) {
    return res.status(401).json({
      success: false,
      message: 'Invalid credentials',
      error: 'User not found or invalid credentials'
    });
  }

  // Check password
  const isPasswordValid = await user.isValidPassword(password);
  
  if (!isPasswordValid) {
    return res.status(401).json({
      success: false,
      message: 'Invalid credentials',
      error: 'Invalid password'
    });
  }

  // Generate tokens
  const tokens = generateTokens(user);

  // Update last login
  await user.updateLastLogin();

  res.json({
    success: true,
    message: 'Login successful',
    data: {
      user: user.toSafeObject(),
      ...tokens
    }
  });
}));

/**
 * @route   POST /api/auth/refresh
 * @desc    Refresh access token using refresh token
 * @access  Public
 */
router.post('/refresh', [
  body('refreshToken')
    .notEmpty()
    .withMessage('Refresh token is required'),
    
  handleValidationErrors
], asyncHandler(async (req, res) => {
  const { refreshToken } = req.body;

  try {
    // Verify refresh token
    const decoded = await verifyRefreshToken(refreshToken);

    // Find user
    const user = await User.findById(decoded.id);
    
    if (!user || !user.isActive) {
      return res.status(401).json({
        success: false,
        message: 'Invalid refresh token',
        error: 'User not found or inactive'
      });
    }

    // Generate new access token
    const accessToken = generateAccessToken(user);

    res.json({
      success: true,
      message: 'Token refreshed successfully',
      data: {
        accessToken,
        tokenType: 'Bearer',
        expiresIn: process.env.JWT_EXPIRE || '24h'
      }
    });

  } catch (error) {
    return res.status(401).json({
      success: false,
      message: 'Invalid refresh token',
      error: 'Token verification failed'
    });
  }
}));

/**
 * @route   POST /api/auth/logout
 * @desc    Logout user (client-side token removal)
 * @access  Public
 */
router.post('/logout', (req, res) => {
  // In a production app, you might want to:
  // 1. Add the token to a blacklist
  // 2. Clear any server-side sessions
  // 3. Log the logout event
  
  res.json({
    success: true,
    message: 'Logged out successfully',
    data: null
  });
});

/**
 * @route   POST /api/auth/forgot-password
 * @desc    Request password reset
 * @access  Public
 */
router.post('/forgot-password', [
  body('email')
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
    
  handleValidationErrors,
  sensitiveOperationLimit(3, 60 * 60 * 1000) // 3 attempts per hour
], asyncHandler(async (req, res) => {
  const { email } = req.body;

  const user = await User.findByEmail(email);
  
  if (!user) {
    // Return success even if user doesn't exist (security measure)
    return res.json({
      success: true,
      message: 'If an account with that email exists, a password reset link has been sent',
      data: null
    });
  }

  // In a real implementation, you would:
  // 1. Generate a secure reset token
  // 2. Store it in the database with expiration
  // 3. Send an email with reset link
  // 4. Handle the reset in a separate endpoint

  // For now, just return a success message
  res.json({
    success: true,
    message: 'Password reset instructions sent to your email',
    data: null
  });
}));

/**
 * @route   POST /api/auth/reset-password
 * @desc    Reset password using reset token
 * @access  Public
 */
router.post('/reset-password', [
  body('token')
    .notEmpty()
    .withMessage('Reset token is required'),
    
  body('password')
    .isLength({ min: 6 })
    .withMessage('Password must be at least 6 characters long')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
    .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number'),
    
  handleValidationErrors
], asyncHandler(async (req, res) => {
  const { token, password } = req.body;

  // In a real implementation, you would:
  // 1. Verify the reset token
  // 2. Check if it's not expired
  // 3. Find the associated user
  // 4. Update their password
  // 5. Invalidate the reset token

  // For now, just return a success message
  res.json({
    success: true,
    message: 'Password reset successful. Please login with your new password.',
    data: null
  });
}));

/**
 * @route   GET /api/auth/verify-email/:token
 * @desc    Verify email address
 * @access  Public
 */
router.get('/verify-email/:token', asyncHandler(async (req, res) => {
  const { token } = req.params;

  // In a real implementation, you would:
  // 1. Verify the email verification token
  // 2. Find the associated user
  // 3. Mark their email as verified
  // 4. Redirect to success page or return success response

  res.json({
    success: true,
    message: 'Email verified successfully',
    data: null
  });
}));

module.exports = router;
