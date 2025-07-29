import React from 'react';
import ReactDOM from 'react-dom';
import App from './App.js';
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';

// Configure Apollo Client
const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql', // GraphQL server endpoint
  cache: new InMemoryCache(),
  defaultOptions: {
    watchQuery: {
      errorPolicy: 'all'
    },
    query: {
      errorPolicy: 'all'
    }
  }
});

// Wrap App with Apollo Provider
ReactDOM.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>,
  document.getElementById('root')
);