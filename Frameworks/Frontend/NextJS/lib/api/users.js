import express from 'express';
import { asyncHandler } from '../middleware/errorHandler.js';

const router = express.Router();

// Temporary in-memory storage for users
let users = [
  {
    id: 'user1',
    email: 'john.doe@example.com',
    name: 'John Doe',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face',
    role: 'ADMIN',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    profile: {
      bio: 'Full-stack developer passionate about modern web technologies',
      website: 'https://johndoe.dev',
      location: 'San Francisco, CA',
      company: 'Tech Corp',
      skills: ['TypeScript', 'React', 'Node.js', 'PostgreSQL']
    },
    stats: {
      posts: 15,
      followers: 342,
      following: 89
    }
  },
  {
    id: 'user2',
    email: 'jane.doe@example.com',
    name: 'Jane Doe',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616b812b6ab?w=150&h=150&fit=crop&crop=face',
    role: 'USER',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    profile: {
      bio: 'UI/UX Designer with clean, user-centered design',
      website: 'https://janesmith.design',
      location: 'New York, NY',
      company: 'Design Studio',
      skills: ['Figma', 'Adobe Creative Suite', 'Prototyping']
    },
    stats: {
      posts: 8,
      followers: 156,
      following: 45
    }
  },
  {
    id: 'user3',
    email: 'm.j@example.com',
    name: 'M J ',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face',
    role: 'USER',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    profile: {
      bio: 'DevOps engineer focused on cloud infrastructure and automation',
      location: 'Austin, TX',
      company: 'Cloud Solutions Inc',
      skills: ['AWS', 'Docker', 'Kubernetes', 'Terraform']
    },
    stats: {
      posts: 12,
      followers: 89,
      following: 67
    }
  }
];

// GET /api/users - Get all users
router.get('/', asyncHandler(async (req, res) => {
  const { 
    role, 
    search,
    limit = 10, 
    offset = 0,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;
  
  let filteredUsers = [...users];
  
  // Filter by role
  if (role) {
    filteredUsers = filteredUsers.filter(user => 
      user.role === role.toUpperCase()
    );
  }
  
  // Search in name and email
  if (search) {
    filteredUsers = filteredUsers.filter(user =>
      user.name.toLowerCase().includes(search.toLowerCase()) ||
      user.email.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  // Sort users
  filteredUsers.sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Paginate
  const paginatedUsers = filteredUsers
    .slice(parseInt(offset), parseInt(offset) + parseInt(limit))
    .map(user => ({
      ...user,
      // Don't expose sensitive information in list view
      email: undefined
    }));
  
  res.json({
    success: true,
    data: paginatedUsers,
    pagination: {
      total: filteredUsers.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: parseInt(offset) + parseInt(limit) < filteredUsers.length
    }
  });
}));

// GET /api/users/featured - Get featured users (with most followers)
router.get('/featured', asyncHandler(async (req, res) => {
  const { limit = 5 } = req.query;
  
  const featuredUsers = users
    .sort((a, b) => b.stats.followers - a.stats.followers)
    .slice(0, parseInt(limit))
    .map(user => ({
      id: user.id,
      name: user.name,
      avatar: user.avatar,
      profile: {
        bio: user.profile.bio,
        company: user.profile.company,
        location: user.profile.location
      },
      stats: user.stats
    }));
  
  res.json({
    success: true,
    data: featuredUsers
  });
}));

// GET /api/users/:id - Get specific user
router.get('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const user = users.find(u => u.id === id);
  
  if (!user) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }
  
  res.json({
    success: true,
    data: user
  });
}));

// GET /api/users/:id/posts - Get user's posts
router.get('/:id/posts', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { limit = 10, offset = 0 } = req.query;
  
  const user = users.find(u => u.id === id);
  
  if (!user) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }
  
  // In real app, fetch from posts table
  const userPosts = [
    {
      id: 'post1',
      title: 'Getting Started with Next.js 15 and Prisma',
      slug: 'getting-started-nextjs-15-prisma',
      excerpt: 'Learn how to combine Next.js 15 with Prisma for a powerful full-stack development experience.',
      publishedAt: new Date('2024-01-15').toISOString(),
      viewCount: 45,
      likes: 2,
      comments: 1
    }
  ].filter(post => post.authorId === id);
  
  res.json({
    success: true,
    data: userPosts,
    pagination: {
      total: userPosts.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: false
    }
  });
}));

// POST /api/users - Create new user
router.post('/', asyncHandler(async (req, res) => {
  const { email, name, role = 'USER' } = req.body;
  
  if (!email || !name) {
    return res.status(400).json({
      success: false,
      error: 'Email and name are required'
    });
  }
  
  // Check if email already exists
  if (users.some(u => u.email === email)) {
    return res.status(400).json({
      success: false,
      error: 'User with this email already exists'
    });
  }
  
  const validRoles = ['USER', 'ADMIN', 'MODERATOR'];
  if (!validRoles.includes(role)) {
    return res.status(400).json({
      success: false,
      error: `Role must be one of: ${validRoles.join(', ')}`
    });
  }
  
  const newUser = {
    id: `user${Date.now()}`,
    email,
    name,
    avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(name)}&size=150`,
    role,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    profile: {
      bio: '',
      website: '',
      location: '',
      company: '',
      skills: []
    },
    stats: {
      posts: 0,
      followers: 0,
      following: 0
    }
  };
  
  users.push(newUser);
  
  res.status(201).json({
    success: true,
    data: newUser,
    message: 'User created successfully'
  });
}));

// PUT /api/users/:id - Update user
router.put('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  
  const userIndex = users.findIndex(u => u.id === id);
  
  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }
  
  const existingUser = users[userIndex];
  
  // Merge profile updates
  if (updates.profile) {
    updates.profile = {
      ...existingUser.profile,
      ...updates.profile
    };
  }
  
  const updatedUser = {
    ...existingUser,
    ...updates,
    updatedAt: new Date().toISOString()
  };
  
  users[userIndex] = updatedUser;
  
  res.json({
    success: true,
    data: updatedUser,
    message: 'User updated successfully'
  });
}));

// DELETE /api/users/:id - Delete user
router.delete('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const userIndex = users.findIndex(u => u.id === id);
  
  if (userIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }
  
  users.splice(userIndex, 1);
  
  res.json({
    success: true,
    message: 'User deleted successfully'
  });
}));

// POST /api/users/:id/follow - Follow/unfollow user
router.post('/:id/follow', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { followerId, action = 'follow' } = req.body;
  
  const user = users.find(u => u.id === id);
  const follower = users.find(u => u.id === followerId);
  
  if (!user || !follower) {
    return res.status(404).json({
      success: false,
      error: 'User not found'
    });
  }
  
  if (action === 'follow') {
    user.stats.followers += 1;
    follower.stats.following += 1;
  } else if (action === 'unfollow') {
    user.stats.followers = Math.max(0, user.stats.followers - 1);
    follower.stats.following = Math.max(0, follower.stats.following - 1);
  }
  
  res.json({
    success: true,
    data: {
      user: { id: user.id, followers: user.stats.followers },
      follower: { id: follower.id, following: follower.stats.following }
    },
    message: `User ${action}ed successfully`
  });
}));

// GET /api/users/stats - Get user statistics
router.get('/stats/summary', asyncHandler(async (req, res) => {
  const stats = {
    total: users.length,
    byRole: {},
    totalPosts: users.reduce((sum, user) => sum + user.stats.posts, 0),
    totalFollowers: users.reduce((sum, user) => sum + user.stats.followers, 0),
    averageFollowers: Math.round(users.reduce((sum, user) => sum + user.stats.followers, 0) / users.length),
    topUsers: users
      .sort((a, b) => b.stats.followers - a.stats.followers)
      .slice(0, 5)
      .map(user => ({
        id: user.id,
        name: user.name,
        followers: user.stats.followers
      }))
  };
  
  users.forEach(user => {
    stats.byRole[user.role] = (stats.byRole[user.role] || 0) + 1;
  });
  
  res.json({
    success: true,
    data: stats
  });
}));

export default router;
