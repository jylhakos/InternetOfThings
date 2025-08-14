const express = require('express');
const { body, query, param } = require('express-validator');
const User = require('../models/user');
const { requireAdmin, requireOwnershipOrAdmin } = require('../middleware/auth');
const { asyncHandler, handleValidationErrors } = require('../middleware/errorHandler');

const router = express.Router();

/**
 * @route   GET /api/users
 * @desc    Get all users (with pagination and search)
 * @access  Private (Authenticated users)
 */
router.get('/', [
  query('page')
    .optional()
    .isInt({ min: 1 })
    .withMessage('Page must be a positive integer'),
    
  query('limit')
    .optional()
    .isInt({ min: 1, max: 100 })
    .withMessage('Limit must be between 1 and 100'),
    
  query('search')
    .optional()
    .trim()
    .escape(),
    
  query('sortBy')
    .optional()
    .isIn(['name', 'email', 'createdAt', 'lastLogin'])
    .withMessage('Invalid sort field'),
    
  query('sortOrder')
    .optional()
    .isIn(['asc', 'desc'])
    .withMessage('Sort order must be asc or desc'),
    
  handleValidationErrors
], asyncHandler(async (req, res) => {
  const {
    page = 1,
    limit = 10,
    search,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;

  const options = {
    page: parseInt(page),
    limit: parseInt(limit),
    sortBy,
    sortOrder: sortOrder === 'desc' ? -1 : 1,
    search
  };

  // Get users with pagination
  const users = await User.getActiveUsers(options);
  
  // Get total count for pagination
  const totalQuery = { isActive: true };
  if (search) {
    totalQuery.$or = [
      { name: { $regex: search, $options: 'i' } },
      { email: { $regex: search, $options: 'i' } },
      { phone: { $regex: search, $options: 'i' } }
    ];
  }
  
  const total = await User.countDocuments(totalQuery);
  const totalPages = Math.ceil(total / limit);

  res.json({
    success: true,
    message: 'Users retrieved successfully',
    data: users,
    pagination: {
      currentPage: parseInt(page),
      totalPages,
      totalItems: total,
      itemsPerPage: parseInt(limit),
      hasNextPage: page < totalPages,
      hasPrevPage: page > 1
    }
  });
}));

/**
 * @route   GET /api/users/stats
 * @desc    Get user statistics
 * @access  Private (Admin only)
 */
router.get('/stats', requireAdmin, asyncHandler(async (req, res) => {
  const stats = await User.getUserStats();

  res.json({
    success: true,
    message: 'User statistics retrieved successfully',
    data: stats
  });
}));

/**
 * @route   GET /api/users/profile
 * @desc    Get current user's profile
 * @access  Private (Authenticated user)
 */
router.get('/profile', asyncHandler(async (req, res) => {
  const user = await User.findById(req.user.id);

  if (!user || !user.isActive) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User profile not found or inactive'
    });
  }

  res.json({
    success: true,
    message: 'Profile retrieved successfully',
    data: user.toSafeObject()
  });
}));

/**
 * @route   PUT /api/users/profile
 * @desc    Update current user's profile
 * @access  Private (Authenticated user)
 */
router.put('/profile', [
  body('name')
    .optional()
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Name must be between 2 and 100 characters'),
    
  body('phone')
    .optional()
    .isMobilePhone()
    .withMessage('Please provide a valid phone number'),
    
  body('email')
    .optional()
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
    
  body('preferences.notifications.email')
    .optional()
    .isBoolean()
    .withMessage('Email notification preference must be boolean'),
    
  body('preferences.notifications.sms')
    .optional()
    .isBoolean()
    .withMessage('SMS notification preference must be boolean'),
    
  body('preferences.notifications.push')
    .optional()
    .isBoolean()
    .withMessage('Push notification preference must be boolean'),
    
  body('preferences.language')
    .optional()
    .isIn(['en', 'es', 'fr', 'de', 'it'])
    .withMessage('Invalid language selection'),
    
  body('preferences.timezone')
    .optional()
    .isString()
    .withMessage('Timezone must be a string'),
    
  handleValidationErrors
], asyncHandler(async (req, res) => {
  const updates = req.body;
  const allowedUpdates = ['name', 'phone', 'email', 'preferences'];
  const updateFields = {};

  // Filter allowed updates
  Object.keys(updates).forEach(key => {
    if (allowedUpdates.includes(key)) {
      updateFields[key] = updates[key];
    }
  });

  // Check for email/phone uniqueness if they're being updated
  if (updateFields.email || updateFields.phone) {
    const existingUser = await User.findOne({
      _id: { $ne: req.user.id },
      $or: [
        ...(updateFields.email ? [{ email: updateFields.email }] : []),
        ...(updateFields.phone ? [{ phone: updateFields.phone }] : [])
      ],
      isActive: true
    });

    if (existingUser) {
      const field = existingUser.email === updateFields.email ? 'email' : 'phone';
      return res.status(400).json({
        success: false,
        message: 'Update failed',
        error: `This ${field} is already in use`
      });
    }
  }

  // Update user
  const user = await User.findByIdAndUpdate(
    req.user.id,
    { $set: updateFields },
    { new: true, runValidators: true }
  );

  if (!user || !user.isActive) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User profile not found or inactive'
    });
  }

  res.json({
    success: true,
    message: 'Profile updated successfully',
    data: user.toSafeObject()
  });
}));

/**
 * @route   GET /api/users/:id
 * @desc    Get user by ID
 * @access  Private (User can access own profile, admin can access any)
 */
router.get('/:id', [
  param('id')
    .isMongoId()
    .withMessage('Invalid user ID'),
    
  handleValidationErrors,
  requireOwnershipOrAdmin('id')
], asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);

  if (!user || !user.isActive) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User not found or inactive'
    });
  }

  res.json({
    success: true,
    message: 'User retrieved successfully',
    data: user.toSafeObject()
  });
}));

/**
 * @route   PUT /api/users/:id
 * @desc    Update user by ID
 * @access  Private (Admin only for other users, users can update own profile)
 */
router.put('/:id', [
  param('id')
    .isMongoId()
    .withMessage('Invalid user ID'),
    
  body('name')
    .optional()
    .trim()
    .isLength({ min: 2, max: 100 })
    .withMessage('Name must be between 2 and 100 characters'),
    
  body('phone')
    .optional()
    .isMobilePhone()
    .withMessage('Please provide a valid phone number'),
    
  body('email')
    .optional()
    .isEmail()
    .normalizeEmail()
    .withMessage('Please provide a valid email'),
    
  body('role')
    .optional()
    .isIn(['user', 'admin'])
    .withMessage('Role must be user or admin'),
    
  body('isActive')
    .optional()
    .isBoolean()
    .withMessage('isActive must be boolean'),
    
  handleValidationErrors,
  requireOwnershipOrAdmin('id')
], asyncHandler(async (req, res) => {
  const updates = req.body;
  const userId = req.params.id;
  const currentUserId = req.user.id;
  const isAdmin = req.user.role === 'admin';

  // Non-admin users can't update role or isActive
  if (!isAdmin && (updates.role || updates.hasOwnProperty('isActive'))) {
    return res.status(403).json({
      success: false,
      message: 'Access denied',
      error: 'You cannot modify role or active status'
    });
  }

  // Check for email/phone uniqueness if they're being updated
  if (updates.email || updates.phone) {
    const existingUser = await User.findOne({
      _id: { $ne: userId },
      $or: [
        ...(updates.email ? [{ email: updates.email }] : []),
        ...(updates.phone ? [{ phone: updates.phone }] : [])
      ],
      isActive: true
    });

    if (existingUser) {
      const field = existingUser.email === updates.email ? 'email' : 'phone';
      return res.status(400).json({
        success: false,
        message: 'Update failed',
        error: `This ${field} is already in use`
      });
    }
  }

  // Update user
  const user = await User.findByIdAndUpdate(
    userId,
    { $set: updates },
    { new: true, runValidators: true }
  );

  if (!user) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User not found'
    });
  }

  res.json({
    success: true,
    message: 'User updated successfully',
    data: user.toSafeObject()
  });
}));

/**
 * @route   DELETE /api/users/:id
 * @desc    Delete user (soft delete)
 * @access  Private (Admin only)
 */
router.delete('/:id', [
  param('id')
    .isMongoId()
    .withMessage('Invalid user ID'),
    
  handleValidationErrors,
  requireAdmin
], asyncHandler(async (req, res) => {
  const userId = req.params.id;

  // Prevent admin from deleting themselves
  if (userId === req.user.id) {
    return res.status(400).json({
      success: false,
      message: 'Cannot delete your own account',
      error: 'Self-deletion not allowed'
    });
  }

  // Soft delete (set isActive to false)
  const user = await User.findByIdAndUpdate(
    userId,
    { isActive: false },
    { new: true }
  );

  if (!user) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User not found'
    });
  }

  res.json({
    success: true,
    message: 'User deleted successfully',
    data: null
  });
}));

/**
 * @route   POST /api/users/:id/restore
 * @desc    Restore soft-deleted user
 * @access  Private (Admin only)
 */
router.post('/:id/restore', [
  param('id')
    .isMongoId()
    .withMessage('Invalid user ID'),
    
  handleValidationErrors,
  requireAdmin
], asyncHandler(async (req, res) => {
  const userId = req.params.id;

  const user = await User.findByIdAndUpdate(
    userId,
    { isActive: true },
    { new: true }
  );

  if (!user) {
    return res.status(404).json({
      success: false,
      message: 'User not found',
      error: 'User not found'
    });
  }

  res.json({
    success: true,
    message: 'User restored successfully',
    data: user.toSafeObject()
  });
}));

/**
 * @route   POST /api/users
 * @desc    Create new user (Admin only)
 * @access  Private (Admin only)
 */
router.post('/', [
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
    
  body('role')
    .optional()
    .isIn(['user', 'admin'])
    .withMessage('Role must be user or admin'),
    
  handleValidationErrors,
  requireAdmin
], asyncHandler(async (req, res) => {
  const { name, email, phone, role = 'user' } = req.body;

  // Check if user already exists
  const existingUser = await User.findOne({
    $or: [{ email }, { phone }],
    isActive: true
  });

  if (existingUser) {
    const field = existingUser.email === email ? 'email' : 'phone';
    return res.status(400).json({
      success: false,
      message: 'User already exists',
      error: `A user with this ${field} already exists`
    });
  }

  // Generate temporary password
  const tempPassword = Math.random().toString(36).slice(-8);
  const bcrypt = require('bcryptjs');
  const hashedPassword = await bcrypt.hash(tempPassword, 12);

  // Create user
  const user = new User({
    name: name.trim(),
    email: email.toLowerCase(),
    phone: phone.replace(/\s+/g, ''),
    password: hashedPassword,
    role,
    metadata: {
      registrationSource: 'admin',
      ipAddress: req.ip,
      userAgent: req.get('User-Agent')
    }
  });

  await user.save();

  res.status(201).json({
    success: true,
    message: 'User created successfully',
    data: {
      user: user.toSafeObject(),
      temporaryPassword: tempPassword // In production, send this via email
    }
  });
}));

module.exports = router;
