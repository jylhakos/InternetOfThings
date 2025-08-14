import express from 'express';
import { asyncHandler } from '../middleware/errorHandler.js';

const router = express.Router();

// Temporary in-memory storage for products
let products = [
  {
    id: 'prod1',
    name: 'Wireless Bluetooth Headphones',
    slug: 'wireless-bluetooth-headphones',
    description: 'High-quality product',
    price: 99.99,
    comparePrice: 129.99,
    sku: 'WBH-001',
    quantity: 50,
    status: 'ACTIVE',
    images: ['/images/headphones-1.jpg', '/images/headphones-2.jpg'],
    tags: ['wireless', 'bluetooth', 'audio'],
    category: {
      id: 'cat1',
      name: 'Electronics',
      slug: 'electronics'
    },
    reviews: {
      average: 4.5,
      count: 24
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: 'prod2',
    name: 'JavaScript: The Definitive Guide',
    slug: 'javascript-definitive-guide',
    description: 'Comprehensive guide to JavaScript programming',
    price: 39.99,
    comparePrice: 49.99,
    sku: 'BOOK-001',
    quantity: 25,
    status: 'ACTIVE',
    images: ['/images/js-book.jpg'],
    tags: ['programming', 'javascript', 'education'],
    category: {
      id: 'cat2',
      name: 'Books',
      slug: 'books'
    },
    reviews: {
      average: 4.8,
      count: 12
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: 'prod3',
    name: 'Premium Cotton T-Shirt',
    slug: 'premium-cotton-tshirt',
    description: 'Product available in multiple colors',
    price: 24.99,
    sku: 'SHIRT-001',
    quantity: 100,
    status: 'ACTIVE',
    images: ['/images/tshirt-1.jpg', '/images/tshirt-2.jpg'],
    tags: ['clothing', 'cotton', 'casual'],
    category: {
      id: 'cat3',
      name: 'Clothing',
      slug: 'clothing'
    },
    reviews: {
      average: 4.2,
      count: 8
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

// GET /api/products - Get all products
router.get('/', asyncHandler(async (req, res) => {
  const { 
    category, 
    tag,
    status = 'ACTIVE',
    search,
    minPrice,
    maxPrice,
    inStock,
    limit = 12, 
    offset = 0,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;
  
  let filteredProducts = [...products];
  
  // Filter by status
  if (status) {
    filteredProducts = filteredProducts.filter(product => 
      product.status === status.toUpperCase()
    );
  }
  
  // Filter by category
  if (category) {
    filteredProducts = filteredProducts.filter(product => 
      product.category.slug === category || product.category.name.toLowerCase().includes(category.toLowerCase())
    );
  }
  
  // Filter by tag
  if (tag) {
    filteredProducts = filteredProducts.filter(product => 
      product.tags.some(t => t.toLowerCase().includes(tag.toLowerCase()))
    );
  }
  
  // Search in name and description
  if (search) {
    filteredProducts = filteredProducts.filter(product =>
      product.name.toLowerCase().includes(search.toLowerCase()) ||
      product.description.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  // Filter by price range
  if (minPrice) {
    filteredProducts = filteredProducts.filter(product => 
      product.price >= parseFloat(minPrice)
    );
  }
  
  if (maxPrice) {
    filteredProducts = filteredProducts.filter(product => 
      product.price <= parseFloat(maxPrice)
    );
  }
  
  // Filter by stock availability
  if (inStock === 'true') {
    filteredProducts = filteredProducts.filter(product => 
      product.quantity > 0
    );
  }
  
  // Sort products
  filteredProducts.sort((a, b) => {
    let aValue = a[sortBy];
    let bValue = b[sortBy];
    
    // Handle nested properties
    if (sortBy === 'reviews.average') {
      aValue = a.reviews.average;
      bValue = b.reviews.average;
    } else if (sortBy === 'reviews.count') {
      aValue = a.reviews.count;
      bValue = b.reviews.count;
    }
    
    if (sortOrder === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });
  
  // Paginate
  const paginatedProducts = filteredProducts
    .slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  
  res.json({
    success: true,
    data: paginatedProducts,
    pagination: {
      total: filteredProducts.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: parseInt(offset) + parseInt(limit) < filteredProducts.length
    }
  });
}));

// GET /api/products/featured - Get featured products
router.get('/featured', asyncHandler(async (req, res) => {
  const { limit = 6 } = req.query;
  
  const featuredProducts = products
    .filter(product => product.status === 'ACTIVE' && product.quantity > 0)
    .sort((a, b) => b.reviews.average - a.reviews.average)
    .slice(0, parseInt(limit));
  
  res.json({
    success: true,
    data: featuredProducts
  });
}));

// GET /api/products/categories - Get product categories
router.get('/categories', asyncHandler(async (req, res) => {
  const categories = [...new Set(products.map(p => p.category.name))]
    .map(name => {
      const category = products.find(p => p.category.name === name).category;
      const productCount = products.filter(p => p.category.name === name).length;
      return {
        ...category,
        productCount
      };
    });
  
  res.json({
    success: true,
    data: categories
  });
}));

// GET /api/products/:id - Get specific product
router.get('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const product = products.find(p => p.id === id || p.slug === id);
  
  if (!product) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  // Get related products (same category, excluding current product)
  const relatedProducts = products
    .filter(p => p.category.id === product.category.id && p.id !== product.id && p.status === 'ACTIVE')
    .slice(0, 4);
  
  res.json({
    success: true,
    data: {
      ...product,
      relatedProducts
    }
  });
}));

// GET /api/products/:id/reviews - Get product reviews
router.get('/:id/reviews', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { limit = 10, offset = 0, sortBy = 'createdAt', sortOrder = 'desc' } = req.query;
  
  const product = products.find(p => p.id === id);
  
  if (!product) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  // Mock reviews data
  const reviews = [
    {
      id: 'review1',
      rating: 5,
      title: 'Excellent quality!',
      comment: 'These products exceeded my expectations. Great and clear.',
      verified: true,
      helpful: 12,
      reviewerName: 'A T',
      createdAt: new Date('2024-01-20').toISOString()
    },
    {
      id: 'review2',
      rating: 4,
      title: 'Good value for money',
      comment: 'Solid product with good quality. Product could be better.',
      verified: true,
      helpful: 8,
      reviewerName: 'S W',
      createdAt: new Date('2024-01-18').toISOString()
    }
  ].filter(review => review.productId === id || id === 'prod1'); // Mock filter
  
  res.json({
    success: true,
    data: reviews,
    pagination: {
      total: reviews.length,
      limit: parseInt(limit),
      offset: parseInt(offset),
      hasMore: false
    }
  });
}));

// POST /api/products - Create new product
router.post('/', asyncHandler(async (req, res) => {
  const { 
    name, 
    description, 
    price, 
    comparePrice,
    sku,
    quantity = 0,
    categoryId,
    tags = [],
    images = []
  } = req.body;
  
  if (!name || !description || !price) {
    return res.status(400).json({
      success: false,
      error: 'Name, description, and price are required'
    });
  }
  
  // Generate slug from name
  const slug = name
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/[\s_-]+/g, '-')
    .replace(/^-+|-+$/g, '');
  
  // Check if slug already exists
  if (products.some(p => p.slug === slug)) {
    return res.status(400).json({
      success: false,
      error: 'A product with this name already exists'
    });
  }
  
  const newProduct = {
    id: `prod${Date.now()}`,
    name,
    slug,
    description,
    price: parseFloat(price),
    comparePrice: comparePrice ? parseFloat(comparePrice) : null,
    sku: sku || `PROD-${Date.now()}`,
    quantity: parseInt(quantity),
    status: 'ACTIVE',
    images: Array.isArray(images) ? images : [images].filter(Boolean),
    tags: Array.isArray(tags) ? tags : [tags].filter(Boolean),
    category: {
      id: categoryId || 'cat1',
      name: 'General',
      slug: 'general'
    },
    reviews: {
      average: 0,
      count: 0
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  products.push(newProduct);
  
  res.status(201).json({
    success: true,
    data: newProduct,
    message: 'Product created successfully'
  });
}));

// PUT /api/products/:id - Update product
router.put('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const updates = req.body;
  
  const productIndex = products.findIndex(p => p.id === id);
  
  if (productIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  const existingProduct = products[productIndex];
  
  // Update slug if name changed
  if (updates.name && updates.name !== existingProduct.name) {
    updates.slug = updates.name
      .toLowerCase()
      .replace(/[^\w\s-]/g, '')
      .replace(/[\s_-]+/g, '-')
      .replace(/^-+|-+$/g, '');
  }
  
  const updatedProduct = {
    ...existingProduct,
    ...updates,
    updatedAt: new Date().toISOString()
  };
  
  products[productIndex] = updatedProduct;
  
  res.json({
    success: true,
    data: updatedProduct,
    message: 'Product updated successfully'
  });
}));

// DELETE /api/products/:id - Delete product
router.delete('/:id', asyncHandler(async (req, res) => {
  const { id } = req.params;
  
  const productIndex = products.findIndex(p => p.id === id);
  
  if (productIndex === -1) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  products.splice(productIndex, 1);
  
  res.json({
    success: true,
    message: 'Product deleted successfully'
  });
}));

// POST /api/products/:id/reviews - Add product review
router.post('/:id/reviews', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { rating, title, comment, reviewerName, reviewerEmail } = req.body;
  
  const product = products.find(p => p.id === id);
  
  if (!product) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  if (!rating || rating < 1 || rating > 5) {
    return res.status(400).json({
      success: false,
      error: 'Rating must be between 1 and 5'
    });
  }
  
  if (!reviewerName || !reviewerEmail) {
    return res.status(400).json({
      success: false,
      error: 'Reviewer name and email are required'
    });
  }
  
  const newReview = {
    id: `review${Date.now()}`,
    productId: id,
    rating: parseInt(rating),
    title: title || '',
    comment: comment || '',
    verified: false,
    helpful: 0,
    reviewerName,
    reviewerEmail,
    createdAt: new Date().toISOString()
  };
  
  // Update product review stats
  const newCount = product.reviews.count + 1;
  const newAverage = ((product.reviews.average * product.reviews.count) + rating) / newCount;
  
  product.reviews = {
    average: Math.round(newAverage * 10) / 10,
    count: newCount
  };
  
  res.status(201).json({
    success: true,
    data: newReview,
    message: 'Review added successfully'
  });
}));

// PATCH /api/products/:id/stock - Update product stock
router.patch('/:id/stock', asyncHandler(async (req, res) => {
  const { id } = req.params;
  const { quantity, operation = 'set' } = req.body;
  
  const product = products.find(p => p.id === id);
  
  if (!product) {
    return res.status(404).json({
      success: false,
      error: 'Product not found'
    });
  }
  
  if (typeof quantity !== 'number') {
    return res.status(400).json({
      success: false,
      error: 'Quantity must be a number'
    });
  }
  
  switch (operation) {
    case 'add':
      product.quantity += quantity;
      break;
    case 'subtract':
      product.quantity = Math.max(0, product.quantity - quantity);
      break;
    case 'set':
    default:
      product.quantity = Math.max(0, quantity);
      break;
  }
  
  product.updatedAt = new Date().toISOString();
  
  res.json({
    success: true,
    data: {
      id: product.id,
      quantity: product.quantity
    },
    message: 'Stock updated successfully'
  });
}));

export default router;
