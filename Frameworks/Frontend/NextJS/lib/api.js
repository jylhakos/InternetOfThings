import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? process.env.API_URL || 'http://localhost:3000'
  : 'http://localhost:3000';

// Utility function to make API requests to our Express backend
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}/api${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error);
    throw error;
  }
}

// GET requests
export async function apiGet(endpoint, params = {}) {
  const searchParams = new URLSearchParams(params).toString();
  const fullEndpoint = searchParams ? `${endpoint}?${searchParams}` : endpoint;
  
  return apiRequest(fullEndpoint, {
    method: 'GET',
  });
}

// POST requests
export async function apiPost(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

// PUT requests
export async function apiPut(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

// DELETE requests
export async function apiDelete(endpoint) {
  return apiRequest(endpoint, {
    method: 'DELETE',
  });
}

// PATCH requests
export async function apiPatch(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Quotes API functions
export const quotesApi = {
  getAll: (params) => apiGet('/quotes', params),
  getRandom: () => apiGet('/quotes/random'),
  getStats: () => apiGet('/quotes/stats'),
  getByKind: (kind, params) => apiGet(`/quotes/kind/${kind}`, params),
  getById: (id) => apiGet(`/quotes/${id}`),
  create: (data) => apiPost('/quotes', data),
  update: (id, data) => apiPut(`/quotes/${id}`, data),
  delete: (id) => apiDelete(`/quotes/${id}`),
};

// Posts API functions
export const postsApi = {
  getAll: (params) => apiGet('/posts', params),
  getFeatured: (params) => apiGet('/posts/featured', params),
  getPopular: (params) => apiGet('/posts/popular', params),
  getBySlug: (slug) => apiGet(`/posts/${slug}`),
  create: (data) => apiPost('/posts', data),
  update: (id, data) => apiPut(`/posts/${id}`, data),
  delete: (id) => apiDelete(`/posts/${id}`),
  like: (id) => apiPost(`/posts/${id}/like`),
  unlike: (id) => apiDelete(`/posts/${id}/like`),
};

// Users API functions
export const usersApi = {
  getAll: (params) => apiGet('/users', params),
  getFeatured: (params) => apiGet('/users/featured', params),
  getProfile: (username) => apiGet(`/users/${username}`),
  create: (data) => apiPost('/users', data),
  update: (id, data) => apiPut(`/users/${id}`, data),
  delete: (id) => apiDelete(`/users/${id}`),
  follow: (id) => apiPost(`/users/${id}/follow`),
  unfollow: (id) => apiDelete(`/users/${id}/follow`),
};

// Products API functions
export const productsApi = {
  getAll: (params) => apiGet('/products', params),
  getFeatured: (params) => apiGet('/products/featured', params),
  getCategories: () => apiGet('/products/categories'),
  getById: (id) => apiGet(`/products/${id}`),
  getReviews: (id, params) => apiGet(`/products/${id}/reviews`, params),
  create: (data) => apiPost('/products', data),
  update: (id, data) => apiPut(`/products/${id}`, data),
  delete: (id) => apiDelete(`/products/${id}`),
  addReview: (id, data) => apiPost(`/products/${id}/reviews`, data),
  updateStock: (id, data) => apiPatch(`/products/${id}/stock`, data),
};

// Analytics API functions
export const analyticsApi = {
  getOverview: (params) => apiGet('/analytics/overview', params),
  getTraffic: (params) => apiGet('/analytics/traffic', params),
  getPages: (params) => apiGet('/analytics/pages', params),
  getRealtime: () => apiGet('/analytics/realtime'),
  getEvents: (params) => apiGet('/analytics/events', params),
  trackEvent: (data) => apiPost('/analytics/events', data),
  getConversions: (params) => apiGet('/analytics/conversions', params),
  getGoals: (params) => apiGet('/analytics/goals', params),
};

// Error handling utilities
export class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Response utilities for API routes
export function successResponse(data, message = 'Success') {
  return NextResponse.json({
    success: true,
    data,
    message,
  });
}

export function errorResponse(error, status = 500) {
  return NextResponse.json({
    success: false,
    error: error.message || 'Internal server error',
  }, { status });
}

export function validationErrorResponse(errors) {
  return NextResponse.json({
    success: false,
    error: 'Validation failed',
    details: errors,
  }, { status: 400 });
}

// Validation utilities
export function validateRequired(data, requiredFields) {
  const errors = [];
  
  for (const field of requiredFields) {
    if (!data[field] || (typeof data[field] === 'string' && data[field].trim() === '')) {
      errors.push(`${field} is required`);
    }
  }
  
  return errors;
}

export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function validateUrl(url) {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}
