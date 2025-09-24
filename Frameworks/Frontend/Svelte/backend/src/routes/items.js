const express = require('express');
const { body, validationResult } = require('express-validator');
const { query } = require('../config/database');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Validation rules
const createItemValidation = [
  body('name')
    .isLength({ min: 1, max: 255 })
    .withMessage('Name must be between 1 and 255 characters'),
  body('description')
    .optional()
    .isLength({ max: 1000 })
    .withMessage('Description must not exceed 1000 characters')
];

// Get all items (authenticated users see their own items)
router.get('/', authenticateToken, async (req, res) => {
  try {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const offset = (page - 1) * limit;

    // Get items for the authenticated user
    const result = await query(
      'SELECT id, name, description, created_at, updated_at FROM items WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
      [req.user.id, limit, offset]
    );

    // Get total count for pagination
    const countResult = await query(
      'SELECT COUNT(*) FROM items WHERE user_id = $1',
      [req.user.id]
    );

    const totalItems = parseInt(countResult.rows[0].count);
    const totalPages = Math.ceil(totalItems / limit);

    res.json({
      success: true,
      data: result.rows.map(item => ({
        id: item.id,
        name: item.name,
        description: item.description,
        createdAt: item.created_at,
        updatedAt: item.updated_at
      })),
      pagination: {
        currentPage: page,
        totalPages,
        totalItems,
        itemsPerPage: limit
      }
    });

  } catch (error) {
    console.error('Get items error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get items'
    });
  }
});

// Get single item by ID
router.get('/:id', authenticateToken, async (req, res) => {
  try {
    const itemId = parseInt(req.params.id);

    if (isNaN(itemId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid item ID'
      });
    }

    const result = await query(
      'SELECT id, name, description, created_at, updated_at FROM items WHERE id = $1 AND user_id = $2',
      [itemId, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Item not found'
      });
    }

    const item = result.rows[0];

    res.json({
      success: true,
      data: {
        id: item.id,
        name: item.name,
        description: item.description,
        createdAt: item.created_at,
        updatedAt: item.updated_at
      }
    });

  } catch (error) {
    console.error('Get item error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to get item'
    });
  }
});

// Create new item
router.post('/', authenticateToken, createItemValidation, async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const { name, description } = req.body;

    const result = await query(
      'INSERT INTO items (name, description, user_id) VALUES ($1, $2, $3) RETURNING id, name, description, created_at, updated_at',
      [name, description || null, req.user.id]
    );

    const item = result.rows[0];

    res.status(201).json({
      success: true,
      message: 'Item created successfully',
      data: {
        id: item.id,
        name: item.name,
        description: item.description,
        createdAt: item.created_at,
        updatedAt: item.updated_at
      }
    });

  } catch (error) {
    console.error('Create item error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create item'
    });
  }
});

// Update item
router.put('/:id', authenticateToken, createItemValidation, async (req, res) => {
  try {
    // Check validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: 'Validation failed',
        errors: errors.array()
      });
    }

    const itemId = parseInt(req.params.id);
    const { name, description } = req.body;

    if (isNaN(itemId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid item ID'
      });
    }

    const result = await query(
      'UPDATE items SET name = $1, description = $2, updated_at = CURRENT_TIMESTAMP WHERE id = $3 AND user_id = $4 RETURNING id, name, description, created_at, updated_at',
      [name, description || null, itemId, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Item not found'
      });
    }

    const item = result.rows[0];

    res.json({
      success: true,
      message: 'Item updated successfully',
      data: {
        id: item.id,
        name: item.name,
        description: item.description,
        createdAt: item.created_at,
        updatedAt: item.updated_at
      }
    });

  } catch (error) {
    console.error('Update item error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update item'
    });
  }
});

// Delete item
router.delete('/:id', authenticateToken, async (req, res) => {
  try {
    const itemId = parseInt(req.params.id);

    if (isNaN(itemId)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid item ID'
      });
    }

    const result = await query(
      'DELETE FROM items WHERE id = $1 AND user_id = $2 RETURNING id',
      [itemId, req.user.id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Item not found'
      });
    }

    res.json({
      success: true,
      message: 'Item deleted successfully'
    });

  } catch (error) {
    console.error('Delete item error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete item'
    });
  }
});

module.exports = router;