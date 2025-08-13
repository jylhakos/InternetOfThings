# Full-Stack Integration Demo

This project demonstrates a complete full-stack application with separated frontend and backend services that work together seamlessly.

## Architecture Overview

```
fullstack-integration/
├── backend/          # Express.js REST API
├── frontend/         # React + Vite application
├── shared/           # Shared utilities and types
├── docker-compose.yml
└── README.md
```

## Features

### Backend (Express.js + MongoDB)
- **RESTful API**: Complete CRUD operations
- **Authentication**: JWT-based user authentication
- **Database**: MongoDB with Mongoose ODM
- **Validation**: Request validation with Joi
- **Security**: CORS, helmet, rate limiting
- **Documentation**: Swagger API documentation
- **Testing**: Jest unit and integration tests

### Frontend (React + Vite)
- **Modern React**: Hooks, context, and latest patterns
- **Routing**: React Router for navigation
- **State Management**: Context API with reducers
- **HTTP Client**: Axios with interceptors
- **UI Components**: Reusable component library
- **Forms**: Formik with Yup validation
- **Styling**: CSS modules and Styled Components

### Integration Features
- **API Communication**: Frontend ↔ Backend via REST API
- **Authentication Flow**: Login, registration, and protected routes
- **Real-time Updates**: WebSocket integration (optional)
- **Error Handling**: Centralized error management
- **Loading States**: Proper loading and error states
- **Data Synchronization**: Optimistic updates with rollback

## Quick Start

### Prerequisites
- Node.js >= 18.0.0
- MongoDB (local or Atlas)
- npm >= 8.0.0

### Installation
```bash
# Install all dependencies
npm run install:all

# Or install manually
npm install
cd backend && npm install
cd ../frontend && npm install
```

### Development
```bash
# Start both frontend and backend concurrently
npm run dev

# Or start individually
npm run dev:backend  # Backend on port 3001
npm run dev:frontend # Frontend on port 5173
```

### Production Build
```bash
npm run build
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get user profile

### Users
- `GET /api/users` - Get all users (admin)
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `DELETE /api/users/:id` - Delete user

### Products
- `GET /api/products` - Get all products
- `GET /api/products/:id` - Get product by ID
- `POST /api/products` - Create product (auth required)
- `PUT /api/products/:id` - Update product (auth required)
- `DELETE /api/products/:id` - Delete product (auth required)

## Frontend Routes

- `/` - Home page
- `/login` - User login
- `/register` - User registration
- `/dashboard` - User dashboard (protected)
- `/products` - Product catalog
- `/products/:id` - Product details
- `/profile` - User profile (protected)
- `/admin` - Admin panel (admin only)

## Environment Variables

### Backend (.env)
```
NODE_ENV=development
PORT=3001
MONGODB_URI=mongodb://localhost:27017/fullstack-demo
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRE=7d
CORS_ORIGIN=http://localhost:5173
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:3001/api
VITE_APP_NAME=Full-Stack Demo
```

## Docker Support

```bash
# Start with Docker Compose
docker-compose up -d

# Stop services
docker-compose down
```

## Testing

```bash
# Run all tests
npm test

# Test backend only
npm run test:backend

# Test frontend only
npm run test:frontend
```

## Key Integration Patterns

### 1. API Client Setup
```javascript
// frontend/src/utils/api.js
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### 2. Error Handling
```javascript
// Global error handling with context
const ErrorProvider = ({ children }) => {
  const [error, setError] = useState(null);
  
  const handleError = (error) => {
    console.error('Application Error:', error);
    setError(error.message || 'An unexpected error occurred');
  };
  
  return (
    <ErrorContext.Provider value={{ error, handleError, clearError: () => setError(null) }}>
      {children}
    </ErrorContext.Provider>
  );
};
```

### 3. Authentication Flow
```javascript
// Protected route component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) return <LoadingSpinner />;
  if (!user) return <Navigate to="/login" />;
  
  return children;
};
```

### 4. Data Fetching Patterns
```javascript
// Custom hook for data fetching
const useProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products');
        setProducts(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    
    fetchProducts();
  }, []);
  
  return { products, loading, error, refetch: fetchProducts };
};
```

## Best Practices Demonstrated

1. **Separation of Concerns**: Clear separation between frontend and backend
2. **Error Boundaries**: React error boundaries for graceful error handling
3. **Loading States**: Proper loading states and skeletons
4. **Form Validation**: Client and server-side validation
5. **Security**: JWT authentication, CORS, input sanitization
6. **Performance**: Code splitting, lazy loading, memoization
7. **Testing**: Unit tests, integration tests, E2E tests
8. **Documentation**: Comprehensive API and code documentation

## Deployment

### Backend Deployment (Node.js)
1. Build the application: `npm run build:backend`
2. Set production environment variables
3. Deploy to your preferred platform (Heroku, Vercel, AWS, etc.)

### Frontend Deployment (Static Files)
1. Build the application: `npm run build:frontend`
2. Deploy the `dist` folder to a static hosting service
3. Configure environment variables for production API URL

### Full-Stack Deployment
- Use Docker Compose for containerized deployment
- Consider platforms like Railway, Render, or DigitalOcean App Platform
- Set up CI/CD pipelines for automated deployments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

MIT License - feel free to use this project as a learning resource or starting point for your own applications.
