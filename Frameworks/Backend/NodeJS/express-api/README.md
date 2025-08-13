# Express.js REST API Example

A comprehensive Express.js REST API demonstrating modern backend development patterns with authentication, validation, and database integration.

## Features

- 🔐 JWT Authentication
- 📝 Input validation with Joi
- 🗄️ MongoDB integration with Mongoose
- 🛡️ Security middleware (Helmet, CORS, Rate Limiting)
- 📊 Structured logging
- 🚨 Error handling
- 📄 API documentation

## Quick Start

### Prerequisites

- Node.js >= 16
- MongoDB (local or cloud)
- npm or yarn

### Installation

```bash
npm install
```

### Environment Variables

Create a `.env` file:

```env
PORT=5000
NODE_ENV=development
JWT_SECRET=your-super-secret-jwt-key-here
MONGODB_URI=mongodb://localhost:27017/express-api
CLIENT_URL=http://localhost:3000
```

### Running the Server

```bash
# Development
npm run dev

# Production
npm start
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/verify` | Verify JWT token |

### Users

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/users` | Get all users | No |
| GET | `/api/users/:id` | Get user by ID | No |
| POST | `/api/users` | Create user | No |
| PUT | `/api/users/:id` | Update user | Yes |
| DELETE | `/api/users/:id` | Delete user | Yes |

### Products

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/products` | Get all products | No |
| GET | `/api/products/:id` | Get product by ID | No |
| POST | `/api/products` | Create product | Yes |
| PUT | `/api/products/:id` | Update product | Yes |
| DELETE | `/api/products/:id` | Delete product | Yes |
| GET | `/api/products/meta/categories` | Get all categories | No |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Server health status |

## Example Requests

### Register User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Create Product (with auth)

```bash
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "name": "Smartphone",
    "description": "Latest model smartphone",
    "price": 699.99,
    "category": "electronics"
  }'
```

### Get Products with Filtering

```bash
# Get electronics under $500
curl "http://localhost:5000/api/products?category=electronics&maxPrice=500"

# Search products
curl "http://localhost:5000/api/products?search=phone"

# Pagination
curl "http://localhost:5000/api/products?page=2&limit=5"
```

## Project Structure

```
express-api/
├── middleware/
│   ├── auth.js           # JWT authentication middleware
│   ├── errorHandler.js   # Global error handling
│   └── logger.js         # Request logging
├── models/
│   ├── User.js          # User data model
│   └── Product.js       # Product data model
├── routes/
│   ├── auth.js          # Authentication routes
│   ├── users.js         # User management routes
│   └── products.js      # Product management routes
├── package.json
├── server.js            # Main server file
└── README.md
```

## Security Features

- **Helmet**: Sets security headers
- **CORS**: Configurable cross-origin requests
- **Rate Limiting**: Prevents API abuse
- **JWT Authentication**: Secure token-based auth
- **Input Validation**: Joi schema validation
- **Password Hashing**: bcryptjs for secure passwords

## Error Handling

The API includes comprehensive error handling:

- **Validation Errors**: Detailed field-level errors
- **Authentication Errors**: Clear auth failure messages
- **Database Errors**: Mongoose error translations
- **404 Handling**: Unknown route responses
- **500 Errors**: Server error logging and responses

## Development

### Adding New Routes

1. Create route file in `/routes`
2. Define validation schemas
3. Implement route handlers
4. Add middleware as needed
5. Import and use in `server.js`

### Adding Models

1. Create model file in `/models`
2. Define Mongoose schema
3. Add validations and indexes
4. Include virtuals and methods as needed

## Testing

```bash
npm test
```

## Deployment

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 5000
CMD ["npm", "start"]
```

### Environment Variables for Production

```env
NODE_ENV=production
PORT=5000
JWT_SECRET=your-very-secure-production-secret
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/dbname
```
