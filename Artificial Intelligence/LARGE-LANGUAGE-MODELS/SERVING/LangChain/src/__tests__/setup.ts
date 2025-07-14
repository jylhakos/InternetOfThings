// Test setup
beforeAll(() => {
  process.env.NODE_ENV = 'test';
  process.env.JWT_SECRET = 'test-secret';
  process.env.LOG_LEVEL = 'error';
});

afterAll(() => {
  // Cleanup
});
