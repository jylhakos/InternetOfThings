import express from 'express';
import { asyncHandler } from '../middleware/errorHandler.js';

const router = express.Router();

// Temporary in-memory storage for quotes until Prisma is set up
let quotes = [
  {
    id: '1',
    text: 'The best time to plant a tree was 20 years ago. The second best time is now.',
    author: 'Chinese Proverb',
    category: 'Motivation',
    kind: 'INSPIRATIONAL',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '2',
    text: 'Code is like. When you have to explain it, it\'s.',
    author: 'C H',
    category: 'Programming',
    kind: 'SCIENTIFIC',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: '3',
    text: 'The only way to do great work is to love what you do.',
    author: 'S J',
    category: 'Career',
    kind: 'MOTIVATIONAL',
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

// GET /api/quotes - Get all quotes
router.get('/', asyncHandler(async (req, res) => {
  const { category, kind, limit = 10, offset = 0 } = req.query;
  
  let filteredQuotes = quotes.filter(quote => quote.isActive);
  
  if (category) {
    filteredQuotes = filteredQuotes.filter(quote => 
      quote.category.toLowerCase().includes(category.toLowerCase())
    );
  }
  
  if (kind) {
    filteredQuotes = filteredQuotes.filter(quote => 
      quote.kind === kind.toUpperCase()
    );
  }
  
  const paginatedQuotes = filteredQuotes
    .slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  
  res.json({
    success: true,
    data: paginatedQuotes,
    pagination: {
      total: filteredQuotes.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: parseInt(offset) + parseInt(limit) < filteredQuotes.length
    }
  });
}));

// GET /api/quotes/random - Get random quote
router.get('/random', asyncHandler(async (req, res) => {
  const { category, kind } = req.query;
  
  let filteredQuotes = quotes.filter(quote => quote.isActive);
  
  if (category) {
    filteredQuotes = filteredQuotes.filter(quote => 
      quote.category.toLowerCase().includes(category.toLowerCase())
    );
  }
  
  if (kind) {
    filteredQuotes = filteredQuotes.filter(quote => 
      quote.kind === kind.toUpperCase()
    );
  }
  
  if (filteredQuotes.length === 0) {
    return res.status(404).json({
      success: false,
      error: 'No quotes found matching the criteria'
    });
  }
  
  const randomQuote = filteredQuotes[Math.floor(Math.random() * filteredQuotes.length)];
  
  res.json({
    success: true,
    data: randomQuote
  });
}));

// GET /api/quotes/:id - Get specific quote
router.get('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const quote = quotes.find(q => q.id === id);
  
  if (!quote) {
    return res.status(404).json({
      success: false,
      error: 'Quote not found'
    });
  }
  
  res.json({
    success: true,
    data: quote
  });
}));

// POST /api/quotes - Create new quote
router.post('/', asyncHandler(async (req, res) => {
  const { text, author, category, kind = 'INSPIRATIONAL' } = req.body;
  
  if (!text || !author) {
    return res.status(400).json({
      success: false,
      error: 'Text and author are required'
    });
  }
  
  const validKinds = ['INSPIRATIONAL', 'MOTIVATIONAL', 'PHILOSOPHICAL', 'SCIENTIFIC', 'WISDOM'];
  if (!validKinds.includes(kind)) {
    return res.status(400).json({
      success: false,
      error: `Kind must be one of: ${validKinds.join(', ')}`
    });
  }
  
  const newQuote = {
    id: String(Date.now()),
    text,
    author,
    category: category || 'General',
    kind,
    isActive: true,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  quotes.push(newQuote);
  
  res.status(201).json({
    success: true,
    data: newQuote,
    message: 'Quote created successfully'
  });
}));

// PUT /api/quotes/:id - Update quote
router.put('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { text, author, category, kind, isActive } = req.body;
  
  const quoteIndex = quotes.findIndex(q => q.id === id);
  
  if (quoteIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Quote not found'
    });
  }
  
  const updatedQuote = {
    ...quotes[quoteIndex],
    ...(text && { text }),
    ...(author && { author }),
    ...(category && { category }),
    ...(kind && { kind }),
    ...(typeof isActive === 'boolean' && { isActive }),
    updatedAt: new Date().toISOString()
  };
  
  quotes[quoteIndex] = updatedQuote;
  
  res.json({
    success: true,
    data: updatedQuote,
    message: 'Quote updated successfully'
  });
}));

// DELETE /api/quotes/:id - Delete quote
router.delete('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const quoteIndex = quotes.findIndex(q => q.id === id);
  
  if (quoteIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Quote not found'
    });
  }
  
  quotes.splice(quoteIndex, 1);
  
  res.json({
    success: true,
    message: 'Quote deleted successfully'
  });
}));

// GET /api/quotes/stats - Get quote statistics
router.get('/stats', asyncHandler(async (req, res) => {
  const stats = {
    total: quotes.length,
    active: quotes.filter(q => q.isActive).length,
    inactive: quotes.filter(q => !q.isActive).length,
    byKind: {},
    byCategory: {}
  };
  
  quotes.forEach(quote => {
    // Count by kind
    stats.byKind[quote.kind] = (stats.byKind[quote.kind] || 0) + 1;
    
    // Count by category
    stats.byCategory[quote.category] = (stats.byCategory[quote.category] || 0) + 1;
  });
  
  res.json({
    success: true,
    data: stats
  });
}));

export default router;
