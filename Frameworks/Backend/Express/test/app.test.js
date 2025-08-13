const request = require('supertest');
const { expect } = require('chai');
const app = require('../app');

describe('Express App Debugging Tests', () => {
    describe('GET /', () => {
        it('should return welcome message with debugging info', async () => {
            const response = await request(app)
                .get('/')
                .expect(200);
            
            expect(response.body).to.have.property('message');
            expect(response.body).to.have.property('timestamp');
            expect(response.body).to.have.property('environment');
            expect(response.body.message).to.equal('Express.js Debugging Demo!');
        });
    });

    describe('GET /users', () => {
        it('should return array of users', async () => {
            const response = await request(app)
                .get('/users')
                .expect(200);
            
            expect(response.body).to.be.an('array');
            expect(response.body).to.have.lengthOf(3);
            expect(response.body[0]).to.have.property('id');
            expect(response.body[0]).to.have.property('name');
            expect(response.body[0]).to.have.property('email');
        });
    });

    describe('GET /users/:id', () => {
        it('should return user data for valid ID', async () => {
            const userId = '123';
            const response = await request(app)
                .get(`/users/${userId}`)
                .expect(200);
            
            expect(response.body).to.have.property('id', 123);
            expect(response.body).to.have.property('name', `User ${userId}`);
            expect(response.body).to.have.property('email', `user${userId}@example.com`);
            expect(response.body).to.have.property('createdAt');
        });

        it('should return 400 for invalid user ID', async () => {
            const response = await request(app)
                .get('/users/invalid')
                .expect(400);
            
            expect(response.body).to.have.property('error', 'Invalid user ID');
            expect(response.body).to.have.property('provided', 'invalid');
            expect(response.body).to.have.property('expected', 'positive integer');
        });

        it('should return 400 for negative user ID', async () => {
            const response = await request(app)
                .get('/users/-1')
                .expect(400);
            
            expect(response.body).to.have.property('error', 'Invalid user ID');
        });
    });

    describe('POST /users', () => {
        it('should create a new user with valid data', async () => {
            const userData = {
                name: 'John Doe',
                email: 'john@example.com'
            };
            
            const response = await request(app)
                .post('/users')
                .send(userData)
                .expect(201);
            
            expect(response.body).to.have.property('id');
            expect(response.body).to.have.property('name', userData.name);
            expect(response.body).to.have.property('email', userData.email);
            expect(response.body).to.have.property('createdAt');
        });

        it('should generate email if not provided', async () => {
            const userData = {
                name: 'Jane Smith'
            };
            
            const response = await request(app)
                .post('/users')
                .send(userData)
                .expect(201);
            
            expect(response.body).to.have.property('email', 'jane.smith@example.com');
        });

        it('should return 400 when name is missing', async () => {
            const userData = {
                email: 'test@example.com'
            };
            
            const response = await request(app)
                .post('/users')
                .send(userData)
                .expect(400);
            
            expect(response.body).to.have.property('error', 'Validation failed');
            expect(response.body).to.have.property('message', 'Name is required');
        });
    });

    describe('GET /error', () => {
        it('should handle errors properly', async () => {
            const response = await request(app)
                .get('/error')
                .expect(500);
            
            expect(response.body).to.have.property('status', 'error');
            expect(response.body).to.have.property('message', 'This is a test error');
        });
    });

    describe('GET /memory', () => {
        it('should return memory usage information', async () => {
            const response = await request(app)
                .get('/memory')
                .expect(200);
            
            expect(response.body).to.have.property('memory');
            expect(response.body.memory).to.have.property('rss');
            expect(response.body.memory).to.have.property('heapTotal');
            expect(response.body.memory).to.have.property('heapUsed');
            expect(response.body).to.have.property('uptime');
        });
    });

    describe('404 handler', () => {
        it('should return 404 for unknown routes', async () => {
            const response = await request(app)
                .get('/nonexistent')
                .expect(404);
            
            expect(response.body).to.have.property('error', 'Not Found');
            expect(response.body).to.have.property('availableRoutes');
            expect(response.body.availableRoutes).to.be.an('array');
        });
    });
});

// Performance tests
describe('Performance Tests', () => {
    it('should respond within acceptable time limits', async () => {
        const start = Date.now();
        await request(app)
            .get('/')
            .expect(200);
        const duration = Date.now() - start;
        
        expect(duration).to.be.below(100); // Should respond within 100ms
    });

    it('should handle multiple concurrent requests', async () => {
        const requests = Array(10).fill().map(() => 
            request(app).get('/users').expect(200)
        );
        
        const responses = await Promise.all(requests);
        responses.forEach(response => {
            expect(response.body).to.be.an('array');
        });
    });
});

// Error handling tests
describe('Error Handling', () => {
    it('should handle malformed JSON', async () => {
        await request(app)
            .post('/users')
            .type('json')
            .send('{"invalid": json}')
            .expect(400);
    });
});
