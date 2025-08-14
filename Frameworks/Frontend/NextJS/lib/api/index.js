import express from 'express';
import postsRouter from './posts.js';
import quotesRouter from './quotes.js';
import usersRouter from './users.js';
import productsRouter from './products.js';
import analyticsRouter from './analytics.js';

const router = express.Router();

// API routes
router.use('/posts', postsRouter);
router.use('/quotes', quotesRouter);
router.use('/users', usersRouter);
router.use('/products', productsRouter);
router.use('/analytics', analyticsRouter);

// API status endpoint
router.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Next.js + Express.js + Prisma API',
    version: '1.0.0',
    endpoints: {
      posts: '/api/posts',
      quotes: '/api/quotes',
      users: '/api/users',
      products: '/api/products',
      analytics: '/api/analytics'
    }
  });
});

export default router;
