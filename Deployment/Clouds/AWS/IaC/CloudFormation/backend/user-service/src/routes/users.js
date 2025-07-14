const express = require('express');
const jwt = require('jsonwebtoken');
const Joi = require('joi');
const { getPool } = require('../database/connection');
const { authenticateToken } = require('../middleware/auth');

const router = express.Router();

// Get user profile (authenticated)
router.get('/profile', authenticateToken, async (req, res) => {
  try {
    const pool = getPool();
    const { userId } = req.user;

    const result = await pool.query(
      'SELECT id, username, email, phone, created_at FROM users WHERE id = $1',
      [userId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const user = result.rows[0];
    res.json({
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        phone: user.phone,
        createdAt: user.created_at
      }
    });
  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Update user profile (authenticated)
router.put('/profile', authenticateToken, async (req, res) => {
  try {
    const pool = getPool();
    const { userId } = req.user;
    const { username, phone } = req.body;

    // Validation schema
    const updateSchema = Joi.object({
      username: Joi.string().alphanum().min(3).max(30).optional(),
      phone: Joi.string().pattern(/^\+?[1-9]\d{1,14}$/).allow('').optional()
    });

    const { error } = updateSchema.validate(req.body);
    if (error) {
      return res.status(400).json({ 
        error: 'Validation error', 
        details: error.details.map(detail => detail.message)
      });
    }

    // Build dynamic update query
    const updates = [];
    const values = [];
    let paramIndex = 1;

    if (username !== undefined) {
      updates.push(`username = $${paramIndex}`);
      values.push(username);
      paramIndex++;
    }

    if (phone !== undefined) {
      updates.push(`phone = $${paramIndex}`);
      values.push(phone || null);
      paramIndex++;
    }

    if (updates.length === 0) {
      return res.status(400).json({ error: 'No valid fields to update' });
    }

    updates.push(`updated_at = CURRENT_TIMESTAMP`);
    values.push(userId);

    const query = `
      UPDATE users 
      SET ${updates.join(', ')} 
      WHERE id = $${paramIndex}
      RETURNING id, username, email, phone, updated_at
    `;

    const result = await pool.query(query, values);

    if (result.rows.length === 0) {
      return res.status(404).json({ error: 'User not found' });
    }

    const user = result.rows[0];
    res.json({
      message: 'Profile updated successfully',
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        phone: user.phone,
        updatedAt: user.updated_at
      }
    });
  } catch (error) {
    console.error('Update profile error:', error);
    
    // Handle unique constraint violations
    if (error.code === '23505') {
      return res.status(409).json({ error: 'Username already exists' });
    }
    
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Get all users (authenticated, for demo purposes)
router.get('/', authenticateToken, async (req, res) => {
  try {
    const pool = getPool();
    
    const result = await pool.query(
      'SELECT id, username, email, phone, created_at FROM users ORDER BY created_at DESC'
    );

    res.json({
      users: result.rows.map(user => ({
        id: user.id,
        username: user.username,
        email: user.email,
        phone: user.phone,
        createdAt: user.created_at
      }))
    });
  } catch (error) {
    console.error('Get users error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

module.exports = router;
