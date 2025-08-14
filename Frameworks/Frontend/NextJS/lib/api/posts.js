import express from 'express';
import { asyncHandler } from '../middleware/errorHandler.js';

const router = express.Router();

// Temporary in-memory storage for posts
let posts = [
  {
    id: 'post1',
    title: 'Getting Started with Next.js 15 and Prisma',
    slug: 'getting-started-nextjs-15-prisma',
    content: '# Getting Started with Next.js 15 and Prisma\n\nNext.js 15 brings exciting new features...',
    excerpt: 'Learn how to combine Next.js 15 with Prisma for a powerful full-stack development experience.',
    published: true,
    featured: true,
    status: 'PUBLISHED',
    publishedAt: new Date('2024-01-15').toISOString(),
    viewCount: 45,
    authorId: 'user1',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    author: {
      id: 'user1',
      name: 'John Doe',
      email: 'john.doe@example.com'
    },
    tags: ['Technology', 'Web Development'],
    likes: 2,
    comments: 1
  },
  {
    id: 'post2',
    title: 'Modern UI/UX Design Principles',
    slug: 'modern-ui-ux-design-principles',
    content: '# Modern UI/UX Design Principles\n\nCreating exceptional user experiences...',
    excerpt: 'Essential design principles for creating modern, user-friendly interfaces.',
    published: true,
    featured: false,
    status: 'PUBLISHED',
    publishedAt: new Date('2024-01-20').toISOString(),
    viewCount: 32,
    authorId: 'user2',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    author: {
      id: 'user2',
      name: 'Jane Smith',
      email: 'jane.smith@example.com'
    },
    tags: ['Design'],
    likes: 1,
    comments: 1
  }
];

// GET /api/posts - Get all posts
router.get('/', asyncHandler(async (req, res) => {
  const { 
    published, 
    featured, 
    authorId, 
    tag,
    search,
    limit = 10, 
    offset = 0,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;
  
  let filteredPosts = [...posts];
  
  // Filter by published status
  if (published !== undefined) {
    filteredPosts = filteredPosts.filter(post => 
      post.published === (published === 'true')
    );
  }
  
  // Filter by featured status
  if (featured !== undefined) {
    filteredPosts = filteredPosts.filter(post => 
      post.featured === (featured === 'true')
    );
  }
  
  // Filter by author
  if (authorId) {
    filteredPosts = filteredPosts.filter(post => post.authorId === authorId);
  }
  
  // Filter by tag
  if (tag) {
    filteredPosts = filteredPosts.filter(post => 
      post.tags.some(t => t.toLowerCase().includes(tag.toLowerCase()))
    );
  }
  
  // Search in title and content
  if (search) {
    filteredPosts = filteredPosts.filter(post =>
      post.title.toLowerCase().includes(search.toLowerCase()) ||
      post.content.toLowerCase().includes(search.toLowerCase()) ||
      post.excerpt.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  // Sort posts
  filteredPosts.sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Paginate
  const paginatedPosts = filteredPosts
    .slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  
  res.json({
    success: true,
    data: paginatedPosts,
    pagination: {
      total: filteredPosts.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: parseInt(offset) + parseInt(limit) < filteredPosts.length
    }
  });
}));

// GET /api/posts/featured - Get featured posts
router.get('/featured', asyncHandler(async (req, res) => {
  const { limit = 3 } = req.query;
  
  const featuredPosts = posts
    .filter(post => post.featured && post.published)
    .sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt))
    .slice(0, parseInt(limit));
  
  res.json({
    success: true,
    data: featuredPosts
  });
}));

// GET /api/posts/popular - Get popular posts
router.get('/popular', asyncHandler(async (req, res) => {
  const { limit = 5 } = req.query;
  
  const popularPosts = posts
    .filter(post => post.published)
    .sort((a, b) => b.viewCount - a.viewCount)
    .slice(0, parseInt(limit));
  
  res.json({
    success: true,
    data: popularPosts
  });
}));

// GET /api/posts/:id - Get specific post
router.get('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const post = posts.find(p => p.id === id || p.slug === id);
  
  if (!post) {
    return res.status(404).json({
      success: false,
      error: 'Post not found'
    });
  }
  
  // Increment view count
  post.viewCount += 1;
  
  res.json({
    success: true,
    data: post
  });
}));

// POST /api/posts - Create new post
router.post('/', asyncHandler(async (req, res) => {
  const { 
    title, 
    content, 
    excerpt, 
    published = false, 
    featured = false,
    authorId,
    tags = []
  } = req.body;
  
  if (!title || !content || !authorId) {
    return res.status(400).json({
      success: false,
      error: 'Title, content, and authorId are required'
    });
  }
  
  // Generate slug from title
  const slug = title
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
  
  // Check if slug already exists
  if (posts.some(p => p.slug === slug)) {
    return res.status(400).json({
      success: false,
      error: 'A post with this title already exists'
    });
  }
  
  const newPost = {
    id: `post${Date.now()}`,
    title,
    slug,
    content,
    excerpt: excerpt || content.substring(0, 200) + '...',
    published,
    featured,
    status: published ? 'PUBLISHED' : 'DRAFT',
    publishedAt: published ? new Date().toISOString() : null,
    viewCount: 0,
    authorId,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    author: {
      id: authorId,
      name: 'Unknown Author', // In real app, fetch from users
      email: 'unknown@example.com'
    },
    tags: Array.isArray(tags) ? tags : [tags].filter(Boolean),
    likes: 0,
    comments: 0
  };
  
  posts.push(newPost);
  
  res.status(201).json({
    success: true,
    data: newPost,
    message: 'Post created successfully'
  });
}));

// PUT /api/posts/:id - Update post
router.put('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  
  const postIndex = posts.findIndex(p => p.id === id);
  
  if (postIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Post not found'
    });
  }
  
  const existingPost = posts[postIndex];
  
  // Update slug if title changed
  if (updates.title && updates.title !== existingPost.title) {
    updates.slug = updates.title
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }
  
  // Update publication status
  if (updates.published && !existingPost.published) {
    updates.publishedAt = new Date().toISOString();
    updates.status = 'PUBLISHED';
  } else if (updates.published === false) {
    updates.status = 'DRAFT';
  }
  
  const updatedPost = {
    ...existingPost,
    ...updates,
    updatedAt: new Date().toISOString()
  };
  
  posts[postIndex] = updatedPost;
  
  res.json({
    success: true,
    data: updatedPost,
    message: 'Post updated successfully'
  });
}));

// DELETE /api/posts/:id - Delete post
router.delete('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const postIndex = posts.findIndex(p => p.id === id);
  
  if (postIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Post not found'
    });
  }
  
  posts.splice(postIndex, 1);
  
  res.json({
    success: true,
    message: 'Post deleted successfully'
  });
}));

// POST /api/posts/:id/like - Toggle like
router.post('/:id/like', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { userId } = req.body;
  
  const post = posts.find(p => p.id === id);
  
  if (!post) {
    return res.status(404).json({
      success: false,
      error: 'Post not found'
    });
  }
  
  // In real app, check if user already liked and toggle
  post.likes += 1;
  
  res.json({
    success: true,
    data: { likes: post.likes },
    message: 'Post liked successfully'
  });
}));

export default router;
