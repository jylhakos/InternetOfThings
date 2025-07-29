# GraphQL application

A full-stack application demonstrating GraphQL implementation for IoT messaging with React frontend and Node.js backend.

## Architecture

- **Frontend**: React app with Apollo client for GraphQL
- **Backend**: Node.js Express server with GraphQL API
- **Database**: In-memory store (can be extended to SQLite/PostgreSQL)
- **Communication**: GraphQL queries and mutations

## Features

-  Create, read, and toggle note importance
-  Real-time updates with Apollo Client
-  GraphQL interface for API testing
-  REST API compatibility endpoint
-  CORS enabled for cross-origin requests

## Setup Instructions

### 1. Backend

```bash
cd backend
npm install
npm run dev
```

**Required dependencies**
```bash
npm install express express-graphql graphql cors sqlite3 uuid nodemon
```

**Backend runs on:** `http://localhost:4000`
**GraphQL interface:** `http://localhost:4000/graphql`

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

**Required dependencies:**
```bash
npm install @apollo/client graphql
```

**Frontend runs on:** `http://localhost:3000`

## GraphQL Schema

### Types
```graphql
type Note {
  id: String
  content: String
  date: String
  important: Boolean
}
```

### Queries
```graphql
# Get all notes
query GetNotes {
  notes {
    id
    content
    date
    important
  }
}

# Get single note by ID
query GetNote($id: String!) {
  note(id: $id) {
    id
    content
    date
    important
  }
}
```

### Mutations
```graphql
# Add new note
mutation AddNote($content: String!, $important: Boolean) {
  addNote(content: $content, important: $important) {
    id
    content
    date
    important
  }
}

# Toggle note importance
mutation ToggleImportance($id: String!) {
  toggleImportance(id: $id) {
    id
    content
    date
    important
  }
}

# Delete note
mutation DeleteNote($id: String!) {
  deleteNote(id: $id) {
    id
    content
  }
}
```

## Testing GraphQL server

### 1. Using GraphQL interface
1. Start the backend server: `npm run dev`
2. Open browser: `http://localhost:4000/graphql`
3. Try sample queries:

```graphql
# Query all notes
{
  notes {
    id
    content
    important
    date
  }
}

# Add a new note
mutation {
  addNote(content: "My IoT sensor data", important: true) {
    id
    content
    important
    date
  }
}
```

### 2. Using React app
1. Start both backend and frontend servers
2. Open `http://localhost:3000`
3. Add notes using the form
4. Toggle importance by clicking the buttons
5. Filter between all/important notes

### 3. REST API compatibility
The backend also provides a REST endpoint for backward compatibility:

```bash
# POST new note
curl -X POST http://localhost:4000/notes \
  -H "Content-Type: application/json" \
  -d '{"content": "Test note", "important": true}'
```

## React + Apollo client integration

### Apollo client (src/index.js)
```javascript
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache(),
});

// Wrap app with Apollo Provider
<ApolloProvider client={client}>
  <App />
</ApolloProvider>
```

### Using GraphQL in components
```javascript
import { useQuery, useMutation, gql } from '@apollo/client';

// Query hook
const { loading, error, data } = useQuery(GET_NOTES);

// Mutation hook
const [addNote] = useMutation(ADD_NOTE, {
  refetchQueries: [{ query: GET_NOTES }]
});
```

## Database

To extend to a SQL database (SQLite example):

### 1. Install SQLite
```bash
npm install sqlite3
```

### 2. Create database helper
```javascript
// database.js
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./notes.db');

db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    date TEXT NOT NULL,
    important BOOLEAN DEFAULT 0
  )`);
});

module.exports = db;
```

### 3. Update Schema resolvers
Replace in-memory array with database operations:
```javascript
// In schema.js resolvers
const db = require('./database');

// Query resolver
resolve() {
  return new Promise((resolve, reject) => {
    db.all("SELECT * FROM notes", (err, rows) => {
      if (err) reject(err);
      else resolve(rows);
    });
  });
}
```

## Development

### Backend
- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests

### Frontend
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests

## Environment Variables

Create `.env` files for configuration:

**Backend (.env)**
```
PORT=4000
NODE_ENV=development
DB_PATH=./notes.db
CORS_ORIGIN=http://localhost:3000
```

**Frontend (.env)**
```
REACT_APP_GRAPHQL_URI=http://localhost:4000/graphql
```

## Project
```
GraphQL/
├── README.md
├── backend/
│   ├── package.json
│   ├── server.js          # Express GraphQL server
│   ├── schema.js          # GraphQL schema and resolvers
│   └── .gitignore
└── frontend/
    ├── package.json
    ├── src/
    │   ├── index.js       # Apollo Client setup
    │   ├── App.js         # Main component with GraphQL hooks
    │   └── components/
    │       └── Note.js    # Note display component
    └── .gitignore
```

## Performance

- Apollo Client caching for efficient data fetching
- Query batching and deduplication
- Polling interval for real-time updates
- Error boundaries for graceful error handling

## Security

- CORS properly configured
- Input validation in GraphQL resolvers
- Rate limiting (can be added with express-rate-limit)
- Authentication (can be added with JWT)

### References

- [GraphQL Official Documentation](https://graphql.org/)
- [Running an Express GraphQL Server](https://www.graphql-js.org/docs/running-an-express-graphql-server/)
- [Apollo Client React Documentation](https://www.apollographql.com/docs/react/)
- [Express GraphQL Middleware](https://github.com/graphql/express-graphql)

