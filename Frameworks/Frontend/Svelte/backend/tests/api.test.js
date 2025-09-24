const request = require('supertest');
const app = require('../src/server');

describe('API Health Check', () => {
  test('GET /health should return 200', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('message', 'Server is running');
  });
});

describe('Authentication API', () => {
  const testUser = {
    name: 'Test User',
    email: 'test@example.com',
    password: 'testpassword123'
  };

  test('POST /api/auth/register should create a new user', async () => {
    const response = await request(app)
      .post('/api/auth/register')
      .send(testUser)
      .expect(201);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body.data).toHaveProperty('user');
    expect(response.body.data).toHaveProperty('token');
    expect(response.body.data.user.email).toBe(testUser.email);
  });

  test('POST /api/auth/login should authenticate user', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: testUser.password
      })
      .expect(200);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body.data).toHaveProperty('user');
    expect(response.body.data).toHaveProperty('token');
  });

  test('POST /api/auth/login with invalid credentials should fail', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({
        email: testUser.email,
        password: 'wrongpassword'
      })
      .expect(401);

    expect(response.body).toHaveProperty('success', false);
  });
});

describe('Items API', () => {
  let authToken;
  
  beforeAll(async () => {
    // Login to get auth token
    const loginResponse = await request(app)
      .post('/api/auth/login')
      .send({
        email: 'test@example.com',
        password: 'testpassword123'
      });
    
    authToken = loginResponse.body.data.token;
  });

  test('GET /api/items should require authentication', async () => {
    await request(app)
      .get('/api/items')
      .expect(401);
  });

  test('GET /api/items should return items for authenticated user', async () => {
    const response = await request(app)
      .get('/api/items')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body).toHaveProperty('data');
    expect(Array.isArray(response.body.data)).toBe(true);
  });

  test('POST /api/items should create a new item', async () => {
    const newItem = {
      name: 'Test Item',
      description: 'This is a test item'
    };

    const response = await request(app)
      .post('/api/items')
      .set('Authorization', `Bearer ${authToken}`)
      .send(newItem)
      .expect(201);

    expect(response.body).toHaveProperty('success', true);
    expect(response.body.data.name).toBe(newItem.name);
    expect(response.body.data.description).toBe(newItem.description);
  });
});