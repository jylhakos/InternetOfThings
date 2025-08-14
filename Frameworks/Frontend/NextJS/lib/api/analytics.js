import express from 'express';
import { asyncHandler } from '../middleware/errorHandler.js';

const router = express.Router();

// Temporary in-memory storage for analytics data
let analyticsData = {
  pageViews: [
    { page: '/', views: 1250, date: '2024-01-20' },
    { page: '/about', views: 450, date: '2024-01-20' },
    { page: '/products', views: 890, date: '2024-01-20' },
    { page: '/blog', views: 320, date: '2024-01-20' },
    { page: '/', views: 1180, date: '2024-01-19' },
    { page: '/about', views: 380, date: '2024-01-19' },
    { page: '/products', views: 750, date: '2024-01-19' },
    { page: '/blog', views: 280, date: '2024-01-19' }
  ],
  userSessions: [
    { date: '2024-01-20', sessions: 892, uniqueUsers: 756, avgSessionDuration: '00:03:42' },
    { date: '2024-01-19', sessions: 834, uniqueUsers: 712, avgSessionDuration: '00:03:28' },
    { date: '2024-01-18', sessions: 756, uniqueUsers: 645, avgSessionDuration: '00:03:15' },
    { date: '2024-01-17', sessions: 698, uniqueUsers: 598, avgSessionDuration: '00:03:38' }
  ],
  topPages: [
    { page: '/', title: 'Home', views: 2430, uniqueViews: 1892 },
    { page: '/products', title: 'Products', views: 1640, uniqueViews: 1234 },
    { page: '/about', title: 'About Us', views: 830, uniqueViews: 672 },
    { page: '/blog', title: 'Blog', views: 600, uniqueViews: 456 },
    { page: '/contact', title: 'Contact', views: 345, uniqueViews: 289 }
  ],
  referralSources: [
    { source: 'google.com', sessions: 1250, percentage: 45.2 },
    { source: 'direct', sessions: 892, percentage: 32.1 },
    { source: 'facebook.com', sessions: 234, percentage: 8.4 },
    { source: 'twitter.com', sessions: 187, percentage: 6.7 },
    { source: 'youtube.com', sessions: 145, percentage: 5.2 },
    { source: 'other', sessions: 67, percentage: 2.4 }
  ],
  deviceTypes: [
    { type: 'Desktop', sessions: 1456, percentage: 52.5 },
    { type: 'Mobile', sessions: 1124, percentage: 40.6 },
    { type: 'Tablet', sessions: 191, percentage: 6.9 }
  ],
  browsers: [
    { name: 'Chrome', sessions: 1678, percentage: 60.6 },
    { name: 'Safari', sessions: 456, percentage: 16.5 },
    { name: 'Firefox', sessions: 334, percentage: 12.1 },
    { name: 'Edge', sessions: 234, percentage: 8.4 },
    { name: 'Other', sessions: 69, percentage: 2.4 }
  ]
};

// GET /api/analytics/overview - Get analytics overview
router.get('/overview', asyncHandler(async (req, res) => {
  const { period = '7d' } = req.query;
  
  // Calculate date range based on period
  const endDate = new Date();
  const startDate = new Date();
  
  switch (period) {
    case '1d':
      startDate.setDate(endDate.getDate() - 1);
      break;
    case '7d':
      startDate.setDate(endDate.getDate() - 7);
      break;
    case '30d':
      startDate.setDate(endDate.getDate() - 30);
      break;
    case '90d':
      startDate.setDate(endDate.getDate() - 90);
      break;
    default:
      startDate.setDate(endDate.getDate() - 7);
  }
  
  // Calculate totals for the period
  const totalSessions = analyticsData.userSessions.reduce((sum, day) => sum + day.sessions, 0);
  const totalUsers = analyticsData.userSessions.reduce((sum, day) => sum + day.uniqueUsers, 0);
  const totalPageViews = analyticsData.pageViews.reduce((sum, view) => sum + view.views, 0);
  
  // Calculate bounce rate and conversion rate (mock values)
  const bounceRate = 34.5;
  const conversionRate = 2.8;
  
  // Calculate growth rates (mock calculations)
  const sessionsGrowth = 12.5;
  const usersGrowth = 8.3;
  const pageViewsGrowth = 15.2;
  const bounceRateGrowth = -2.1;
  
  res.json({
    success: true,
    data: {
      overview: {
        totalSessions,
        totalUsers,
        totalPageViews,
        bounceRate,
        conversionRate,
        growth: {
          sessions: sessionsGrowth,
          users: usersGrowth,
          pageViews: pageViewsGrowth,
          bounceRate: bounceRateGrowth
        }
      },
      period
    }
  });
}));

// GET /api/analytics/traffic - Get traffic analytics
router.get('/traffic', asyncHandler(async (req, res) => {
  const { period = '7d', groupBy = 'day' } = req.query;
  
  // Group traffic data by the specified period
  let trafficData = analyticsData.userSessions;
  
  if (groupBy === 'hour' && period === '1d') {
    // Mock hourly data for today
    trafficData = Array.from({ length: 24 }, (_, i) => ({
      period: `${i.toString().padStart(2, '0')}:00`,
      sessions: Math.floor(Math.random() * 100) + 20,
      users: Math.floor(Math.random() * 80) + 15,
      pageViews: Math.floor(Math.random() * 150) + 30
    }));
  }
  
  res.json({
    success: true,
    data: {
      traffic: trafficData,
      referralSources: analyticsData.referralSources,
      deviceTypes: analyticsData.deviceTypes,
      browsers: analyticsData.browsers
    }
  });
}));

// GET /api/analytics/pages - Get page analytics
router.get('/pages', asyncHandler(async (req, res) => {
  const { period = '7d', limit = 10, sortBy = 'views', sortOrder = 'desc' } = req.query;
  
  let pageData = [...analyticsData.topPages];
  
  // Sort pages
  pageData.sort((a, b) => {
    const aValue = a[sortBy] || 0;
    const bValue = b[sortBy] || 0;
    
    if (sortOrder === 'asc') {
      return aValue - bValue;
    } else {
      return bValue - aValue;
    }
  });
  
  // Limit results
  pageData = pageData.slice(0, parseInt(limit));
  
  // Add additional metrics
  pageData = pageData.map(page => ({
    ...page,
    bounceRate: Math.round(Math.random() * 30) + 20, // Mock bounce rate
    avgTimeOnPage: `00:0${Math.floor(Math.random() * 5) + 2}:${Math.floor(Math.random() * 60).toString().padStart(2, '0')}`, // Mock time
    exitRate: Math.round(Math.random() * 40) + 10 // Mock exit rate
  }));
  
  res.json({
    success: true,
    data: {
      pages: pageData,
      totalPages: analyticsData.topPages.length
    }
  });
}));

// GET /api/analytics/realtime - Get real-time analytics
router.get('/realtime', asyncHandler(async (req, res) => {
  // Mock real-time data
  const realTimeData = {
    activeUsers: Math.floor(Math.random() * 50) + 10,
    currentPageViews: Math.floor(Math.random() * 20) + 5,
    topActivePages: [
      { page: '/', activeUsers: Math.floor(Math.random() * 15) + 3 },
      { page: '/products', activeUsers: Math.floor(Math.random() * 10) + 2 },
      { page: '/blog', activeUsers: Math.floor(Math.random() * 8) + 1 },
      { page: '/about', activeUsers: Math.floor(Math.random() * 5) + 1 }
    ],
    recentEvents: [
      { 
        event: 'page_view', 
        page: '/', 
        timestamp: new Date(Date.now() - Math.random() * 60000).toISOString(),
        userAgent: 'Chrome/120.0.0.0',
        country: 'US'
      },
      { 
        event: 'page_view', 
        page: '/products', 
        timestamp: new Date(Date.now() - Math.random() * 120000).toISOString(),
        userAgent: 'Safari/17.0',
        country: 'CA'
      },
      { 
        event: 'conversion', 
        page: '/checkout', 
        timestamp: new Date(Date.now() - Math.random() * 180000).toISOString(),
        userAgent: 'Firefox/121.0',
        country: 'UK'
      }
    ]
  };
  
  res.json({
    success: true,
    data: realTimeData
  });
}));

// GET /api/analytics/events - Get custom event analytics
router.get('/events', asyncHandler(async (req, res) => {
  const { 
    eventName, 
    period = '7d', 
    limit = 20, 
    offset = 0 
  } = req.query;
  
  // Mock events data
  let events = [
    {
      id: 'evt1',
      name: 'button_click',
      category: 'engagement',
      label: 'hero_cta',
      value: 1,
      page: '/',
      timestamp: new Date('2024-01-20T10:30:00Z').toISOString(),
      userAgent: 'Chrome/120.0.0.0',
      sessionId: 'sess123'
    },
    {
      id: 'evt2',
      name: 'form_submit',
      category: 'conversion',
      label: 'contact_form',
      value: 1,
      page: '/contact',
      timestamp: new Date('2024-01-20T09:45:00Z').toISOString(),
      userAgent: 'Safari/17.0',
      sessionId: 'sess124'
    },
    {
      id: 'evt3',
      name: 'video_play',
      category: 'media',
      label: 'intro_video',
      value: 1,
      page: '/about',
      timestamp: new Date('2024-01-20T08:15:00Z').toISOString(),
      userAgent: 'Firefox/121.0',
      sessionId: 'sess125'
    },
    {
      id: 'evt4',
      name: 'download',
      category: 'content',
      label: 'product_brochure',
      value: 1,
      page: '/products',
      timestamp: new Date('2024-01-19T16:20:00Z').toISOString(),
      userAgent: 'Edge/120.0',
      sessionId: 'sess126'
    }
  ];
  
  // Filter by event name if specified
  if (eventName) {
    events = events.filter(event => event.name === eventName);
  }
  
  // Paginate results
  const paginatedEvents = events.slice(parseInt(offset), parseInt(offset) + parseInt(limit));
  
  // Calculate event summary
  const eventSummary = events.reduce((acc, event) => {
    if (!acc[event.name]) {
      acc[event.name] = {
        name: event.name,
        count: 0,
        category: event.category
      };
    }
    acc[event.name].count++;
    return acc;
  }, {});
  
  res.json({
    success: true,
    data: {
      events: paginatedEvents,
      summary: Object.values(eventSummary),
      pagination: {
        total: events.length,
        limit: parseInt(limit),
        offset: parseInt(offset),
        hasMore: parseInt(offset) + parseInt(limit) < events.length
      }
    }
  });
}));

// POST /api/analytics/events - Track custom event
router.post('/events', asyncHandler(async (req, res) => {
  const { 
    name, 
    category = 'custom', 
    label = '', 
    value = 1, 
    page, 
    userAgent,
    sessionId 
  } = req.body;
  
  if (!name) {
    return res.status(400).json({
      success: false,
      error: 'Event name is required'
    });
  }
  
  const newEvent = {
    id: `evt${Date.now()}`,
    name,
    category,
    label,
    value: parseInt(value) || 1,
    page: page || '/',
    timestamp: new Date().toISOString(),
    userAgent: userAgent || req.get('User-Agent'),
    sessionId: sessionId || `sess${Date.now()}`
  };
  
  // In a real app, this would be saved to the database
  console.log('Event tracked:', newEvent);
  
  res.status(201).json({
    success: true,
    data: newEvent,
    message: 'Event tracked successfully'
  });
}));

// GET /api/analytics/conversions - Get conversion analytics
router.get('/conversions', asyncHandler(async (req, res) => {
  const { period = '7d', funnelType = 'general' } = req.query;
  
  // Mock conversion funnel data
  const conversionData = {
    general: [
      { step: 'Landing Page', users: 1000, percentage: 100 },
      { step: 'Product View', users: 450, percentage: 45 },
      { step: 'Add to Cart', users: 180, percentage: 18 },
      { step: 'Checkout', users: 89, percentage: 8.9 },
      { step: 'Purchase', users: 28, percentage: 2.8 }
    ],
    signup: [
      { step: 'Visit Signup Page', users: 500, percentage: 100 },
      { step: 'Start Form', users: 320, percentage: 64 },
      { step: 'Complete Form', users: 240, percentage: 48 },
      { step: 'Email Verification', users: 200, percentage: 40 },
      { step: 'Account Active', users: 180, percentage: 36 }
    ]
  };
  
  const funnelData = conversionData[funnelType] || conversionData.general;
  
  // Calculate conversion rates between steps
  const funnelWithRates = funnelData.map((step, index) => {
    if (index === 0) {
      return { ...step, dropOffRate: 0, conversionRate: 100 };
    }
    
    const previousStep = funnelData[index - 1];
    const dropOffRate = ((previousStep.users - step.users) / previousStep.users) * 100;
    const conversionRate = (step.users / previousStep.users) * 100;
    
    return {
      ...step,
      dropOffRate: Math.round(dropOffRate * 100) / 100,
      conversionRate: Math.round(conversionRate * 100) / 100
    };
  });
  
  res.json({
    success: true,
    data: {
      funnel: funnelWithRates,
      overallConversionRate: funnelWithRates[funnelWithRates.length - 1].percentage,
      totalUsers: funnelWithRates[0].users,
      conversions: funnelWithRates[funnelWithRates.length - 1].users
    }
  });
}));

// GET /api/analytics/goals - Get goal completion analytics
router.get('/goals', asyncHandler(async (req, res) => {
  const { period = '7d' } = req.query;
  
  // Mock goals data
  const goals = [
    {
      id: 'goal1',
      name: 'Newsletter Signup',
      type: 'conversion',
      completions: 145,
      value: 5.00,
      conversionRate: 12.3,
      trend: 8.5
    },
    {
      id: 'goal2',
      name: 'Product Purchase',
      type: 'revenue',
      completions: 28,
      value: 75.50,
      conversionRate: 2.8,
      trend: -2.1
    },
    {
      id: 'goal3',
      name: 'Contact Form',
      type: 'engagement',
      completions: 67,
      value: 15.00,
      conversionRate: 5.4,
      trend: 15.2
    },
    {
      id: 'goal4',
      name: 'Blog Engagement',
      type: 'engagement',
      completions: 234,
      value: 2.50,
      conversionRate: 18.9,
      trend: 23.7
    }
  ];
  
  const totalRevenue = goals.reduce((sum, goal) => sum + (goal.completions * goal.value), 0);
  const totalConversions = goals.reduce((sum, goal) => sum + goal.completions, 0);
  
  res.json({
    success: true,
    data: {
      goals,
      summary: {
        totalRevenue: Math.round(totalRevenue * 100) / 100,
        totalConversions,
        averageConversionRate: Math.round((goals.reduce((sum, goal) => sum + goal.conversionRate, 0) / goals.length) * 100) / 100
      }
    }
  });
}));

export default router;
