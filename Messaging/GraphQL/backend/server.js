const express = require('express');
const { createHandler } = require('graphql-http');
const cors = require('cors');
const schema = require('./schema');

const app = express();

// Enable CORS for React app
app.use(cors({
  origin: 'http://localhost:3000', // React app URL
  credentials: true
}));

// REST endpoint for compatibility (optional)
app.use(express.json());

// Traditional REST endpoint for notes (for backward compatibility)
app.post('/notes', (req, res) => {
  const { content, important } = req.body;
  
  // This could redirect to GraphQL mutation or handle directly
  // For now, we'll handle it directly for compatibility
  const noteObject = {
    id: require('uuid').v4(),
    content: content,
    date: new Date().toISOString(),
    important: important !== undefined ? important : Math.random() > 0.5,
  };
  
  // In a real app, you'd save to database here
  console.log('Note received via REST:', noteObject);
  res.json(noteObject);
});

// GraphQL endpoint with modern graphql-http
const handler = createHandler({
  schema: schema,
  graphiql: true, // Enable GraphiQL interface for testing
});

app.use('/graphql', handler);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'Server is running', timestamp: new Date().toISOString() });
});

const port = process.env.PORT || 4000;

app.listen(port, () => {
  console.log(`GraphQL Server running on http://localhost:${port}`);
  console.log(`GraphiQL interface available at http://localhost:${port}/graphql`);
  console.log(`Health check at http://localhost:${port}/health`);
});
