const express = require('express');
const cors = require('cors');

const app = express();
const port = 3000;

// Enable CORS for all routes
app.use(cors());

// Example data
const devices = [
  { id: 1, name: 'Smartphone' },
  { id: 2, name: 'Laptop' },
  { id: 3, name: 'Tablet' }
];

app.get('/devices', (req, res) => {
  res.json(devices);
});

app.listen(port, () => {
  console.log(`Node.js server listening at http://localhost:${port}`);
});